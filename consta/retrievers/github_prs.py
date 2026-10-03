from consta.clients import ClientBundle
from consta.models.assessment import AssessmentRequest
from consta.models.evidence import EvidenceItem, EvidenceKind
from consta.models.profile import EcosystemProfile
from consta.retrievers.base import RetrievalPlan, RetrievalSpec


class GitHubPrsRetriever:
    name = "github_prs"
    tier = 2

    def plan(
        self,
        request: AssessmentRequest,
        profile: EcosystemProfile | None,
        plan: RetrievalPlan,
    ) -> RetrievalSpec | None:
        for spec in plan.specs:
            if spec.retriever == self.name:
                return spec
        return None

    async def fetch(
        self,
        spec: RetrievalSpec,
        request: AssessmentRequest,
        profile: EcosystemProfile | None,
        clients: ClientBundle,
    ) -> list[EvidenceItem]:
        items: list[EvidenceItem] = []
        for query in spec.queries:
            results = await clients.github.search_issues(query, per_page=10)
            for rank, pr in enumerate(results):
                number = pr.get("number")
                if number is None:
                    continue
                score = max(0.1, 0.9 - rank * 0.05)
                items.append(
                    EvidenceItem(
                        id=f"pr-{number}",
                        kind=EvidenceKind.PULL_REQUEST,
                        title=str(pr.get("title") or f"PR #{number}"),
                        url=pr.get("html_url", f"https://github.com/{request.repo}/pull/{number}"),
                        snippet=str(pr.get("title") or "")[:500],
                        source_retriever=self.name,
                        relevance_score=score,
                        metadata={
                            "merged_at": pr.get("closed_at"),
                            "state": pr.get("state"),
                        },
                    )
                )
        return items
