"""Report-quality regressions: evidence mix, citation gate, snippets, rendering."""

import pytest

from consta.clients.http import extract_page_text
from consta.engine.citation_checker import check_citations
from consta.engine.orchestrator import _diversify
from consta.engine.validator import validate_evidence
from consta.models.assessment import AssessmentRequest
from consta.models.evidence import EvidenceItem, EvidenceKind
from consta.profiles import load_profile
from consta.render.markdown import _snippet_suffix


@pytest.fixture
def pytorch_profile(profiles_dir):
    return load_profile(profiles_dir, "pytorch", allow_stale=True)


def _item(id_, kind, score, title="t", snippet="s"):
    return EvidenceItem(
        id=id_,
        kind=kind,
        title=title,
        url=f"https://example.com/{id_}",
        snippet=snippet,
        source_retriever="test",
        relevance_score=score,
    )


def test_diversify_puts_every_kind_in_the_lead():
    issues = [_item(f"issue-{n}", EvidenceKind.ISSUE, 1.0 - n * 0.01) for n in range(30)]
    vitals = _item("vitals", EvidenceKind.VITAL_SIGNS, 0.92)
    adjacent = _item("adjacent-x", EvidenceKind.ADJACENT_PROJECT, 0.7)
    ordered = sorted([*issues, vitals, adjacent], key=lambda i: -i.relevance_score)
    lead = [i.id for i in _diversify(ordered)[:25]]
    assert "vitals" in lead and "adjacent-x" in lead


def test_uncited_paragraph_is_rejected():
    summary = 'Docs are missing "Masked Tensor documentation" [1].\n\nSo it is worth doing.'
    errors = check_citations(summary, {1: "issue-1"}, {"issue-1"})
    assert any("Paragraph 2" in e for e in errors)


def test_off_topic_pr_is_excluded(pytorch_profile):
    request = AssessmentRequest(
        question="Is reviving torch.masked worth it?", repo="pytorch/pytorch", path="torch/masked"
    )
    pr = _item(
        "pr-1",
        EvidenceKind.PULL_REQUEST,
        0.9,
        title="[ONNX] fix export of embedding with padding_idx",
        snippet="[ONNX] fix export of embedding with padding_idx",
    )
    kept, excluded = validate_evidence([pr], pytorch_profile, request)
    assert not kept and excluded[0].id == "pr-1"


def test_page_text_skips_css_and_unescapes():
    html = (
        '<html><head><title>Flex &#8211; PyTorch</title>'
        '<link media="(min-width >= 40rem)" rel="stylesheet"><style>:root{--x:1}</style></head>'
        "<body><nav>Skip to main content</nav><main><p>Masked attention &amp; more.</p></main></body></html>"
    )
    title, snippet, refresh = extract_page_text(html)
    assert title == "Flex – PyTorch"
    assert snippet == "Masked attention & more."
    assert refresh is None


def test_page_text_reports_meta_refresh():
    html = '<meta http-equiv="refresh" content="0; url=../2.14/nested.html"><a>Continue</a>'
    assert extract_page_text(html)[2] == "../2.14/nested.html"


def test_rendered_snippet_does_not_repeat_title():
    item = _item("issue-1", EvidenceKind.ISSUE, 0.9, title="Bug", snippet="Bug — details here")
    assert _snippet_suffix(item) == " — details here"
    pr = _item("pr-1", EvidenceKind.PULL_REQUEST, 0.9, title="Fix", snippet="Fix")
    assert _snippet_suffix(pr) == ""


def test_quoting_only_a_name_is_rejected():
    item = _item("adjacent-pandas", EvidenceKind.ADJACENT_PROJECT, 0.7, title="pandas", snippet="docs")
    errors = check_citations(
        'pandas already covers this "pandas" [1].',
        {1: "adjacent-pandas"},
        {"adjacent-pandas"},
        id_by_num={1: "adjacent-pandas"},
        items_by_id={"adjacent-pandas": item},
    )
    assert any("quotes only the name" in e for e in errors)


def test_citations_renumbered_to_the_mapped_id_slot():
    from consta.engine.synthesizer import _parse_synthesis

    raw = (
        '{"paragraphs": "Activity is low \\"commits fell\\" [1]. Docs \\"are missing\\" [2].",'
        ' "citations": {"1": "vitals", "2": "issue-1"}}'
    )
    paragraphs, cites, _ = _parse_synthesis(raw, {1: "issue-1", 2: "x", 3: "vitals"})
    assert paragraphs == 'Activity is low "commits fell" [3]. Docs "are missing" [1].'
    assert cites == {3: "vitals", 1: "issue-1"}


def test_elided_quote_needs_fragments_in_order():
    item = _item("i", EvidenceKind.ISSUE, 0.9, title="T", snippet="alpha beta gamma delta")
    ok = check_citations('x "alpha ... delta" [1]', {1: "i"}, {"i"}, id_by_num={1: "i"}, items_by_id={"i": item})
    bad = check_citations('x "delta ... alpha" [1]', {1: "i"}, {"i"}, id_by_num={1: "i"}, items_by_id={"i": item})
    assert ok == [] and bad


def test_quote_ignores_code_ticks_and_inner_quotes():
    item = _item(
        "issue-9",
        EvidenceKind.ISSUE,
        0.9,
        title='RFC SLEP006: allow a "strict" mode for `BaggingClassifier`',
        snippet="body",
    )
    kwargs = dict(id_by_num={1: "issue-9"}, items_by_id={"issue-9": item})
    ok = check_citations('x "allow a strict mode for BaggingClassifier" [1]', {1: "issue-9"}, {"issue-9"}, **kwargs)
    bad = check_citations('x "allow a lenient mode for BaggingClassifier" [1]', {1: "issue-9"}, {"issue-9"}, **kwargs)
    assert ok == [] and bad
