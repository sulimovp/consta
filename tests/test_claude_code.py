"""The claude-code provider runs `claude -p` and reads its JSON result."""

import asyncio
import json

import httpx
import pytest

from consta.clients.llm import LlmClient
from consta.config import Settings


class _FakeProc:
    def __init__(self, payload: dict, returncode: int = 0) -> None:
        self._out = json.dumps(payload).encode()
        self.returncode = returncode
        self.stdin_seen = b""

    async def communicate(self, data: bytes):
        self.stdin_seen = data
        return self._out, b""


def _settings(**kw):
    return Settings(llm_provider="claude-code", claude_cli="/fake/claude", **kw)


@pytest.mark.asyncio
async def test_complete_passes_system_and_model_and_reads_result(monkeypatch):
    calls = {}
    proc = _FakeProc({"type": "result", "is_error": False, "result": "ok"})

    async def fake_exec(*args, **kwargs):
        calls["args"] = args
        calls["cwd"] = kwargs["cwd"]
        return proc

    monkeypatch.setattr(asyncio, "create_subprocess_exec", fake_exec)
    async with httpx.AsyncClient() as client:
        llm = LlmClient(_settings(llm_model="opus"), client)
        assert llm.available
        assert await llm.complete("the rules", "the evidence") == "ok"

    args = calls["args"]
    assert args[0] == "/fake/claude"
    assert args[args.index("--system-prompt") + 1] == "the rules"
    assert args[args.index("--model") + 1] == "opus"
    assert args[args.index("--tools") + 1] == ""
    assert proc.stdin_seen == b"the evidence"


@pytest.mark.asyncio
async def test_error_result_raises(monkeypatch):
    proc = _FakeProc({"is_error": True, "result": "Failed to authenticate"}, returncode=1)

    async def fake_exec(*args, **kwargs):
        return proc

    monkeypatch.setattr(asyncio, "create_subprocess_exec", fake_exec)
    async with httpx.AsyncClient() as client:
        with pytest.raises(RuntimeError, match="Failed to authenticate"):
            await LlmClient(_settings(), client).complete("s", "u")


def test_not_configured_without_cli(monkeypatch):
    monkeypatch.setattr("shutil.which", lambda name: None)
    assert not Settings(llm_provider="claude-code").llm_configured()
