import json
import re

from consta.clients.llm import LlmClient
from consta.engine.citation_checker import check_citations
from consta.models.assessment import AssessmentRequest
from consta.models.evidence import EvidenceItem

_SYSTEM = """You are an evidence synthesis assistant for open-source contribution decisions.
Rules:
- Use ONLY the evidence items provided. Do not name projects, issues, or facts not in the list.
- Write 2-3 short paragraphs separated by blank lines; every paragraph cites at least one item. Weigh module activity and adjacent projects, not only bug reports. Be conditional, not cheerleading — contribution may be unwise if adjacent projects already solve the need.
- Every factual claim must end with a short verbatim quote (at most 15 words) copied from the cited item's title or snippet, in double quotes, then the citation number(s). Example: ... "native tool use and optional thinking" [3]. Adjacent-project curator notes are not source text — do not quote them. For adjacent projects, vital signs and files, quote the snippet, not the bare name.
- Citation numbers [n] MUST match the evidence list below. In the JSON citations object, key "n" MUST be exactly the evidence id shown for [n] (the id=… value), never a different item.
- List open_questions for things the evidence does NOT resolve (maintainer roadmap, prototype status, duplicate work).
- Return ONLY valid JSON, no markdown fences:
  {"paragraphs": "...", "citations": {"1": "evidence-id"}, "open_questions": ["...", "..."]}
- If evidence is insufficient, say so in paragraphs and open_questions. Do not guess."""

SYNTHESIS_LIMIT = 25
# Reasoning models (gpt-oss on the HF router) spend most of the budget thinking;
# a tight cap truncates the JSON and the whole synthesis is lost.
_MAX_TOKENS = 8000


async def synthesize(
    request: AssessmentRequest,
    items: list[EvidenceItem],
    llm: LlmClient,
) -> tuple[str | None, dict[int, str], list[str], dict[int, str]]:
    numbered = []
    id_by_num: dict[int, str] = {}
    for idx, item in enumerate(items[:SYNTHESIS_LIMIT], start=1):
        id_by_num[idx] = item.id
        numbered.append(
            f"[{idx}] id={item.id} kind={item.kind} title={item.title}\n"
            f"url={item.url}\nsnippet={item.snippet}\n"
        )

    evidence_block = "\n".join(numbered)
    user = (
        f"Question: {request.question}\n"
        f"Repository: {request.repo}\n\n"
        f"Evidence:\n{evidence_block}"
    )
    raw = await llm.complete(_SYSTEM, user, max_tokens=_MAX_TOKENS)
    paragraphs, citation_map, open_questions = _parse_synthesis(raw, id_by_num)

    items_by_id = {item.id: item for item in items[:SYNTHESIS_LIMIT]}
    errors = check_citations(
        paragraphs,
        citation_map,
        set(id_by_num.values()),
        id_by_num=id_by_num,
        items_by_id=items_by_id,
    )
    if errors and paragraphs:
        allowed = "\n".join(f'  "{n}": "{eid}"' for n, eid in sorted(id_by_num.items()))
        repair_user = (
            f"{user}\n\n"
            "Your previous JSON failed citation checks:\n"
            + "\n".join(f"- {e}" for e in errors)
            + "\n\nRewrite the full JSON. The citations object MUST be a subset of:\n{\n"
            + allowed
            + "\n}\n"
            "Key n may only map to the id shown for that same n. "
            "Every claim needs a ≤15-word verbatim quote from that item's title or "
            "snippet immediately before [n]."
        )
        raw2 = await llm.complete(_SYSTEM, repair_user, max_tokens=_MAX_TOKENS)
        paragraphs2, citation_map2, open_questions2 = _parse_synthesis(raw2, id_by_num)
        errors2 = check_citations(
            paragraphs2,
            citation_map2,
            set(id_by_num.values()),
            id_by_num=id_by_num,
            items_by_id=items_by_id,
        )
        # Only take the repair if it is actually better; a truncated retry must not win.
        if paragraphs2 and len(errors2) < len(errors):
            paragraphs, citation_map, open_questions = (
                paragraphs2,
                citation_map2,
                open_questions2 or open_questions,
            )

    return paragraphs, citation_map, open_questions, id_by_num


def _parse_synthesis(
    raw: str, id_by_num: dict[int, str]
) -> tuple[str | None, dict[int, str], list[str]]:
    for candidate in _json_candidates(raw):
        try:
            data = json.loads(candidate)
        except (json.JSONDecodeError, ValueError, TypeError):
            continue
        if not isinstance(data, dict):
            continue
        paragraphs = str(data.get("paragraphs", "")).strip()
        citations_raw = data.get("citations", {})
        citation_map: dict[int, str] = {}
        if isinstance(citations_raw, dict):
            for key, value in citations_raw.items():
                try:
                    num = int(str(key).strip("[] "))
                except ValueError:
                    continue
                # Keep the model's claimed id (after light normalization). Do NOT
                # rewrite it to id_by_num[num] — disagreement is a checker error.
                citation_map[num] = _normalize_evidence_id(str(value), id_by_num)
        open_questions = _parse_open_questions(data.get("open_questions"))
        if paragraphs:
            paragraphs, citation_map = _renumber_to_slots(paragraphs, citation_map, id_by_num)
            return paragraphs, citation_map, open_questions

    # Non-JSON fallback: keep prose but do not invent citation mappings from [n].
    prose = raw.strip()
    prose = re.sub(r"\s*\{[\s\S]*\"paragraphs\"[\s\S]*\}\s*$", "", prose).strip()
    return prose or None, {}, []


def _renumber_to_slots(
    paragraphs: str, citation_map: dict[int, str], id_by_num: dict[int, str]
) -> tuple[str, dict[int, str]]:
    """Point each [n] at the slot of the id the model mapped it to.

    Models often number citations by order of appearance while naming the right id.
    The id is the identity; the quote gate then checks the quote against that item.
    Unknown ids are left alone so the checker still rejects them.
    """
    in_prose = {int(n) for n in re.findall(r"\[(\d+)\]", paragraphs)}
    if not in_prose <= citation_map.keys():
        return paragraphs, citation_map  # an unmapped [n] must stay visible to the checker
    slot_by_id = {eid: num for num, eid in id_by_num.items()}
    moves = {
        num: slot_by_id[eid]
        for num, eid in citation_map.items()
        if eid in slot_by_id and slot_by_id[eid] != num
    }
    if not moves:
        return paragraphs, citation_map
    renumbered = re.sub(
        r"\[(\d+)\]",
        lambda m: f"[{moves.get(int(m.group(1)), int(m.group(1)))}]",
        paragraphs,
    )
    remapped = {moves.get(num, num): eid for num, eid in citation_map.items()}
    return renumbered, remapped


def _normalize_evidence_id(evidence_id: str, id_by_num: dict[int, str]) -> str:
    valid = set(id_by_num.values())
    if evidence_id in valid:
        return evidence_id
    # Models sometimes emit the slot number instead of the id — only accept that
    # when it resolves to the id for that same slot.
    if evidence_id.isdigit():
        num = int(evidence_id)
        if num in id_by_num:
            return id_by_num[num]
        candidate = f"issue-{evidence_id}"
        if candidate in valid:
            return candidate
    return evidence_id


def _parse_open_questions(raw: object) -> list[str]:
    if not isinstance(raw, list):
        return []
    return [str(q).strip() for q in raw if str(q).strip()]


def _json_candidates(raw: str) -> list[str]:
    text = raw.strip()
    candidates: list[str] = []

    fence = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, re.IGNORECASE)
    if fence:
        candidates.append(fence.group(1).strip())

    candidates.append(text)

    start = text.find("{")
    if start != -1:
        candidates.append(text[start:].strip())

    seen: set[str] = set()
    unique: list[str] = []
    for item in candidates:
        if item and item not in seen:
            seen.add(item)
            unique.append(item)
    return unique
