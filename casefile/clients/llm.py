import httpx

from casefile.config import Settings

_HF_CHAT_URL = "https://router.huggingface.co/v1/chat/completions"


class LlmClient:
    def __init__(self, settings: Settings, client: httpx.AsyncClient) -> None:
        self._settings = settings
        self._client = client

    @property
    def available(self) -> bool:
        return self._settings.llm_configured()

    async def ping(self) -> str:
        provider = self._settings.llm_provider
        if provider == "openai":
            return await self._ping_openai()
        if provider == "huggingface":
            return await self._complete_huggingface(
                "You are a ping probe.",
                "Reply with exactly: pong",
                max_tokens=512,  # reasoning models think before answering
            )
        return await self._ping_anthropic()

    async def complete(
        self,
        system: str,
        user: str,
        *,
        max_tokens: int = 1024,
        response_format: dict | None = None,
    ) -> str:
        provider = self._settings.llm_provider
        if provider == "openai":
            return await self._complete_openai(
                system, user, max_tokens=max_tokens, response_format=response_format
            )
        if provider == "huggingface":
            return await self._complete_huggingface(
                system, user, max_tokens=max_tokens, response_format=response_format
            )
        return await self._complete_anthropic(system, user, max_tokens=max_tokens)

    async def _ping_anthropic(self) -> str:
        key = self._settings.anthropic_api_key
        if not key:
            raise RuntimeError("CASEFILE_ANTHROPIC_API_KEY is not set")
        response = await self._client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": self._settings.resolved_llm_model(),
                "max_tokens": 16,
                "messages": [{"role": "user", "content": "Reply with exactly: pong"}],
            },
        )
        response.raise_for_status()
        data = response.json()
        content = data.get("content", [])
        if content and isinstance(content[0], dict):
            return str(content[0].get("text", ""))
        return ""

    async def _ping_openai(self) -> str:
        key = self._settings.openai_api_key
        if not key:
            raise RuntimeError("CASEFILE_OPENAI_API_KEY is not set")
        response = await self._client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "content-type": "application/json"},
            json={
                "model": self._settings.resolved_llm_model(),
                "max_tokens": 16,
                "messages": [{"role": "user", "content": "Reply with exactly: pong"}],
            },
        )
        response.raise_for_status()
        return _openai_content(response.json())

    async def _complete_anthropic(self, system: str, user: str, *, max_tokens: int) -> str:
        key = self._settings.anthropic_api_key
        if not key:
            raise RuntimeError("CASEFILE_ANTHROPIC_API_KEY is not set")
        response = await self._client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": self._settings.resolved_llm_model(),
                "max_tokens": max_tokens,
                "system": system,
                "messages": [{"role": "user", "content": user}],
            },
        )
        response.raise_for_status()
        data = response.json()
        content = data.get("content", [])
        if content and isinstance(content[0], dict):
            return str(content[0].get("text", ""))
        return ""

    async def _complete_openai(
        self,
        system: str,
        user: str,
        *,
        max_tokens: int,
        response_format: dict | None = None,
    ) -> str:
        key = self._settings.openai_api_key
        if not key:
            raise RuntimeError("CASEFILE_OPENAI_API_KEY is not set")
        payload: dict = {
            "model": self._settings.resolved_llm_model(),
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        if response_format is not None:
            payload["response_format"] = response_format
        response = await self._client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}", "content-type": "application/json"},
            json=payload,
        )
        response.raise_for_status()
        return _openai_content(response.json())

    async def _complete_huggingface(
        self,
        system: str,
        user: str,
        *,
        max_tokens: int,
        response_format: dict | None = None,
    ) -> str:
        key = self._settings.hf_token
        if not key:
            raise RuntimeError("CASEFILE_HF_TOKEN is not set")
        payload: dict = {
            "model": self._settings.resolved_llm_model(),
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }
        if response_format is not None:
            payload["response_format"] = response_format
        response = await self._client.post(
            _HF_CHAT_URL,
            headers={"Authorization": f"Bearer {key}", "content-type": "application/json"},
            json=payload,
        )
        response.raise_for_status()
        return _openai_content(response.json())


def _openai_content(data: dict) -> str:
    choices = data.get("choices", [])
    if choices and isinstance(choices[0], dict):
        message = choices[0].get("message", {})
        if isinstance(message, dict):
            # Never fall back to `reasoning`: chain of thought is not an answer
            # and must not reach a report.
            return str(message.get("content") or "")
    return ""
