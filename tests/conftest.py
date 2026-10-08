import pytest

from consta.config import get_settings


@pytest.fixture(autouse=True)
def _isolated_cache(tmp_path, monkeypatch):
    # Mocked GitHub responses must never land in the real ~/.cache/consta search cache,
    # or the next live run serves them as fact for the cache TTL.
    monkeypatch.setenv("CONSTA_CACHE_DIR", str(tmp_path / "consta-cache"))


@pytest.fixture
def profiles_dir():
    return get_settings().resolved_profiles_dir()
