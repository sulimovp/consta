"""Flask UI smoke tests (no live APIs)."""

import pytest

from casefile.web.app import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    return app.test_client()


def test_index_loads(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"Should you invest" in response.data
    assert b"pytorch-masked" in response.data or b"torch.masked" in response.data


def test_health_page(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert b"GitHub API" in response.data


def test_preset_query_param(client):
    response = client.get("/?preset=numpy-ma")
    assert response.status_code == 200
    assert b"numpy/numpy" in response.data
    assert b"numpy/ma" in response.data


def test_sample_cases_listed_on_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert b"pytorch-nested" in response.data or b"torch.nested" in response.data
    assert b"sklearn-generic" in response.data or b"feature X" in response.data


def test_summary_html_is_escaped():
    from casefile.models.assessment import AssessmentReport, AssessmentRequest
    from casefile.models.evidence import EvidenceBundle
    from casefile.web.app import _render_result, create_app

    report = AssessmentReport(
        request=AssessmentRequest(question="q", repo="o/r"),
        evidence=EvidenceBundle(),
        summary='Fine "quote" [1] <script>alert(1)</script>',
    )
    with create_app().test_request_context("/"):
        page = _render_result(report)
    assert "<script>alert(1)</script>" not in page
    assert "&lt;script&gt;" in page


def test_every_evidence_kind_has_a_web_label():
    from casefile.models.evidence import EvidenceKind
    from casefile.web.app import _WEB_KIND_LABELS

    assert set(_WEB_KIND_LABELS) == set(EvidenceKind)
