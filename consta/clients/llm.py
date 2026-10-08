import httpx

from consta.config import Settings

_HF_CHAT_URL = "https://router.huggingface.co/v1/chat/completions"
_OPENROUTER_CHAT_URL = "https://openrouter.ai/api/v1/chat/completions"


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
        if provider == "openrouter":
            return await self._complete_openrouter(
                "You are a ping probe.", "Reply with exactly: pong", max_tokens=512
            )
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
        if provider == "openrouter":
            return await self._complete_openrouter(
                system, user, max_tokens=max_tokens, response_format=response_format
            )
        return await self._complete_anthropic(system, user, max_tokens=max_tokens)

    async def _ping_anthropic(self) -> str:
        key = self._settings.anthropic_api_key
        if not key:
            raise RuntimeError("CONSTA_ANTHROPIC_API_KEY is not set")
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
            raise RuntimeError("CONSTA_OPENAI_API_KEY is not set")
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
            raise RuntimeError("CONSTA_ANTHROPIC_API_KEY is not set")
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
            raise RuntimeError("CONSTA_OPENAI_API_KEY is not set")
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
            raise RuntimeError("CONSTA_HF_TOKEN is not set")
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

    async def _complete_openrouter(
        self,
        system: str,
        user: str,
        *,
        max_tokens: int,
        response_format: dict | None = None,
    ) -> str:
        key = self._settings.openrouter_api_key
        if not key:
            raise RuntimeError("CONSTA_OPENROUTER_API_KEY is not set")
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
            _OPENROUTER_CHAT_URL,
            headers={
                "Authorization": f"Bearer {key}",
                "content-type": "application/json",
                # Optional attribution headers OpenRouter uses for its app listing.
                "HTTP-Referer": "https://github.com/sulimovp/consta",
                "X-Title": "Consta",
            },
            json=payload,
        )
        if response.is_error:
            # OpenRouter explains refusals (spend limit, unknown model) in the body;
            # a bare status code hides the fix from the report.
            try:
                detail = response.json().get("error", {}).get("message", "")
            except ValueError:
                detail = ""
            raise RuntimeError(f"OpenRouter {response.status_code}: {detail or response.reason_phrase}")
        data = response.json()
        content = _openai_content(data)
        if not content.strip():
            # Free-tier upstreams can answer 200 with an error or an empty message.
            error = data.get("error") if isinstance(data.get("error"), dict) else {}
            choices = data.get("choices") or [{}]
            reason = error.get("message") or f"finish_reason={choices[0].get('finish_reason')}"
            raise RuntimeError(f"OpenRouter returned an empty answer ({reason})")
        return content


def _openai_content(data: dict) -> str:
    choices = data.get("choices", [])
    if choices and isinstance(choices[0], dict):
        message = choices[0].get("message", {})
        if isinstance(message, dict):
            # Never fall back to `reasoning`: chain of thought is not an answer
            # and must not reach a report.
            return str(message.get("content") or "")
    return ""
