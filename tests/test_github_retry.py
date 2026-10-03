"""GitHub client retry on rate-limit responses."""

import httpx
import pytest

from casefile.clients.github import GitHubClient
from casefile.config import Settings


@pytest.mark.asyncio
async def test_search_issues_retries_on_403(httpx_mock, tmp_path):
    httpx_mock.add_response(status_code=403, headers={"Retry-After": "0"})
    httpx_mock.add_response(
        status_code=200,
        json={
            "total_count": 1,
            "items": [
                {
                    "number": 1,
                    "title": "ok",
                    "html_url": "https://github.com/o/r/issues/1",
                }
            ],
        },
    )
    query = "repo:o/r is:issue retry-403-unique"
    async with httpx.AsyncClient() as client:
        gh = GitHubClient(
            Settings(github_token="t", cache_dir=tmp_path), client
        )
        items = await gh.search_issues(query)
    assert len(items) == 1


@pytest.mark.asyncio
async def test_permission_403_is_not_retried(httpx_mock, tmp_path):
    httpx_mock.add_response(
        status_code=403,
        headers={"x-ratelimit-remaining": "4999"},
        json={"message": "Resource not accessible by personal access token"},
    )
    async with httpx.AsyncClient() as client:
        gh = GitHubClient(Settings(github_token="t", cache_dir=tmp_path), client)
        with pytest.raises(httpx.HTTPStatusError):
            await gh.search_issues("repo:o/r is:issue permission-403-unique")
    assert len(httpx_mock.get_requests()) == 1
