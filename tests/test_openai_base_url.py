"""CONSTA_OPENAI_BASE_URL points the openai provider at any OpenAI-compatible server."""

import httpx
import pytest

from consta.clients.llm import LlmClient
from consta.config import Settings


def _settings(**kw):
    kw.setdefault("llm_model", "local-model")
    return Settings(llm_provider="openai", openai_api_key="local", **kw)


@pytest.mark.asyncio
async def test_default_base_url_is_openai(httpx_mock):
    httpx_mock.add_response(
        url="https://api.openai.com/v1/chat/completions",
        method="POST",
        json={"choices": [{"message": {"content": "ok"}}]},
    )
    async with httpx.AsyncClient() as client:
        assert await LlmClient(_settings(), client).complete("s", "u") == "ok"


@pytest.mark.asyncio
async def test_custom_base_url_is_used_for_complete_and_ping(httpx_mock):
    url = "http://127.0.0.1:8765/v1/chat/completions"
    for reply in ("ok", "pong"):
        httpx_mock.add_response(
            url=url, method="POST", json={"choices": [{"message": {"content": reply}}]}
        )
    settings = _settings(openai_base_url="http://127.0.0.1:8765/v1/")
    async with httpx.AsyncClient() as client:
        llm = LlmClient(settings, client)
        assert await llm.complete("s", "u") == "ok"
        assert await llm.ping() == "pong"
    assert len(httpx_mock.get_requests()) == 2
