"""Citation integrity checks for synthesis summaries."""

from __future__ import annotations

import re
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from consta.models.evidence import EvidenceItem

_REF_RE = re.compile(r"\[(\d+)\]")
# A quote of at most 15 words must sit immediately before each group of markers.
_MARKER_GROUP_RE = re.compile(r"(?:\[\d+\])+")
_QUOTE_BEFORE_RE = re.compile(r'"([^"]{1,240})"\s*$')
_CITE_NUM_RE = re.compile(r"\[(\d+)\]")
# Kinds whose title is itself content (an issue title states the bug); other titles are names.
_CONTENT_TITLED_KINDS = frozenset(
    {"issue", "issue_comment", "pull_request", "discourse_thread", "hf_discussion"}
)


def check_citations(
    summary: str | None,
    citation_map: dict[int, str],
    valid_ids: set[str],
    *,
    id_by_num: dict[int, str] | None = None,
    items_by_id: dict[str, EvidenceItem] | None = None,
) -> list[str]:
    if not summary:
        return []

    errors: list[str] = []
    refs_in_text = {int(m.group(1)) for m in _REF_RE.finditer(summary)}
    if not refs_in_text:
        return ["Summary has no [n] citations; uncited synthesis is not shown."]

    paragraphs = [p for p in re.split(r"\n\s*\n", summary) if p.strip()]
    for idx, paragraph in enumerate(paragraphs, start=1):
        if not _REF_RE.search(paragraph):
            errors.append(
                f"Paragraph {idx} has no [n] citation; every claim must cite evidence."
            )

    for num in sorted(refs_in_text):
        evidence_id = citation_map.get(num)
        if evidence_id is None:
            errors.append(
                f"Citation [{num}] appears in prose but has no citations map entry "
                "(unsourced bracket — not filled from list position)."
            )
            continue
        if evidence_id not in valid_ids:
            errors.append(f"Citation [{num}] maps to unknown evidence id {evidence_id!r}")
        if id_by_num is not None:
            expected = id_by_num.get(num)
            if expected is not None and evidence_id != expected:
                errors.append(
                    f"Citation [{num}] maps to {evidence_id!r} but evidence slot [{num}] "
                    f"is {expected!r}"
                )

    for num, evidence_id in citation_map.items():
        if evidence_id not in valid_ids:
            errors.append(f"citation_map[{num}] references unknown evidence id {evidence_id!r}")

    if items_by_id is not None:
        # Check every marker on its own: a number cited twice needs both quotes to hold,
        # otherwise a fabricated first quote hides behind a genuine second one.
        seen: set[tuple[int, str | None]] = set()
        for num, quote in _citation_uses(summary):
            if (num, quote) in seen:
                continue
            seen.add((num, quote))
            evidence_id = citation_map.get(num)
            if evidence_id is None or evidence_id not in items_by_id:
                continue
            if not quote:
                errors.append(
                    f"Citation [{num}] is missing a short verbatim quote (≤15 words) "
                    "from the cited evidence immediately before the marker."
                )
                continue
            if len(quote.split()) > 15:
                errors.append(f"Citation [{num}] quote exceeds 15 words: {quote!r}")
                continue
            item = items_by_id[evidence_id]
            names_only = _normalize_span(quote) == _normalize_span(item.title)
            if names_only and item.kind not in _CONTENT_TITLED_KINDS:
                # "pandas" or "Module vital signs: numpy/ma" names the source; it supports no claim.
                errors.append(
                    f"Citation [{num}] quotes only the name {quote!r}; "
                    "quote the passage that supports the claim."
                )
                continue
            hay = quote_haystack(item)
            if not _quote_in(quote, hay):
                errors.append(
                    f"Citation [{num}] quote {quote!r} not found in cited item {evidence_id!r}"
                )

    return errors


def _citation_uses(summary: str) -> list[tuple[int, str | None]]:
    """Each citation marker with the quote right before it (None if there is none).

    `"span" [1][2]` attaches the same span to both numbers.
    """
    uses: list[tuple[int, str | None]] = []
    for group in _MARKER_GROUP_RE.finditer(summary):
        before = _QUOTE_BEFORE_RE.search(summary, 0, group.start())
        quote = before.group(1).strip() if before else None
        for num_s in _CITE_NUM_RE.findall(group.group(0)):
            uses.append((int(num_s), quote))
    return uses


def quote_haystack(item: EvidenceItem) -> str:
    """Title + fetched snippet only. Curator `relevance` notes are not source text."""
    return f"{item.title} {item.snippet}"


def _quote_in(quote: str, hay: str) -> bool:
    """Verbatim match; an elided quote ("a ... b") needs every fragment, in order."""
    hay_n = _normalize_span(hay)
    pos = 0
    fragments = [f for f in re.split(r"\.\.\.|…", quote) if f.strip()]
    if not fragments:
        return False
    for fragment in fragments:
        found = hay_n.find(_normalize_span(fragment), pos)
        if found == -1:
            return False
        pos = found + len(_normalize_span(fragment))
    return True


def _normalize_span(text: str) -> str:
    # Backticks and quote marks are formatting: a quote delimited by "..." cannot keep
    # inner double quotes, and models drop markdown code ticks. Words must still match.
    text = re.sub(r"[`\"'‘’“”]", "", text.lower())
    return re.sub(r"\s+", " ", text).strip()
