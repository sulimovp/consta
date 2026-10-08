"""OpenRouter synthesis backend (OpenAI-compatible chat completions)."""

import json

import httpx
import pytest

from consta.clients.llm import LlmClient
from consta.config import Settings

_URL = "https://openrouter.ai/api/v1/chat/completions"


def _settings(**kw):
    # Explicit llm_model so a developer's CONSTA_LLM_MODEL in .env can't leak in.
    kw.setdefault("llm_model", None)
    return Settings(llm_provider="openrouter", openrouter_api_key="sk-or-test", **kw)


def test_openrouter_configured_and_default_model():
    assert _settings().llm_configured()
    assert _settings().resolved_llm_model() == "anthropic/claude-sonnet-5.5"
    assert not Settings(llm_provider="openrouter", openrouter_api_key=None).llm_configured()
    assert _settings(llm_model="openai/gpt-oss-120b").resolved_llm_model() == "openai/gpt-oss-120b"


@pytest.mark.asyncio
async def test_openrouter_complete_posts_chat_request(httpx_mock):
    httpx_mock.add_response(
        url=_URL, method="POST", json={"choices": [{"message": {"content": "pong"}}]}
    )
    async with httpx.AsyncClient() as client:
        reply = await LlmClient(_settings(), client).complete("sys", "user", max_tokens=32)

    assert reply == "pong"
    request = httpx_mock.get_request()
    assert request.headers["Authorization"] == "Bearer sk-or-test"
    body = json.loads(request.content)
    assert body["model"] == "anthropic/claude-sonnet-5.5"
    assert body["messages"][0] == {"role": "system", "content": "sys"}
    assert body["max_tokens"] == 32


@pytest.mark.asyncio
async def test_openrouter_missing_key_raises():
    async with httpx.AsyncClient() as client:
        llm = LlmClient(Settings(llm_provider="openrouter", openrouter_api_key=None), client)
        with pytest.raises(RuntimeError, match="CONSTA_OPENROUTER_API_KEY"):
            await llm.complete("s", "u")


@pytest.mark.asyncio
async def test_openrouter_error_message_is_surfaced(httpx_mock):
    httpx_mock.add_response(
        url=_URL,
        method="POST",
        status_code=403,
        json={"error": {"message": "Key limit exceeded (total limit).", "code": 403}},
    )
    async with httpx.AsyncClient() as client:
        with pytest.raises(RuntimeError, match="OpenRouter 403: Key limit exceeded"):
            await LlmClient(_settings(), client).complete("s", "u")


@pytest.mark.asyncio
async def test_openrouter_empty_200_is_an_error(httpx_mock):
    httpx_mock.add_response(
        url=_URL,
        method="POST",
        json={"error": {"message": "Provider returned error", "code": 429}, "choices": []},
    )
    async with httpx.AsyncClient() as client:
        with pytest.raises(RuntimeError, match="empty answer \\(Provider returned error\\)"):
            await LlmClient(_settings(), client).complete("s", "u")
