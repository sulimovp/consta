from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

_PACKAGE_DIR = Path(__file__).resolve().parent


def data_path(repo_relative: str, packaged: str) -> Path:
    """Resolve a data file: repo checkout first (editable installs), then the wheel copy."""
    repo_root = _PACKAGE_DIR.parent
    # In a wheel install repo_root is site-packages; never trust it.
    if (repo_root / "pyproject.toml").is_file() and (repo_root / repo_relative).exists():
        return repo_root / repo_relative
    return _PACKAGE_DIR / "_data" / packaged


# User-wide config first, then ./.env (later files win), so `consta` works from any directory.
USER_ENV_FILE = Path.home() / ".config" / "consta" / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="CONSTA_", env_file=(USER_ENV_FILE, ".env"), extra="ignore"
    )

    github_token: str | None = None
    hf_token: str | None = None
    anthropic_api_key: str | None = None
    openai_api_key: str | None = None
    openrouter_api_key: str | None = None
    llm_provider: str = "anthropic"
    llm_model: str | None = None
    cache_dir: Path = Path.home() / ".cache" / "consta"
    profiles_dir: Path | None = None
    github_api_base: str = "https://api.github.com"
    http_timeout: float = 30.0

    def llm_configured(self) -> bool:
        if self.llm_provider == "openai":
            return bool(self.openai_api_key)
        if self.llm_provider == "huggingface":
            return bool(self.hf_token)
        if self.llm_provider == "openrouter":
            return bool(self.openrouter_api_key)
        return bool(self.anthropic_api_key)

    def resolved_llm_model(self) -> str:
        if self.llm_model:
            return self.llm_model
        if self.llm_provider == "openai":
            return "gpt-4o-mini"
        if self.llm_provider == "huggingface":
            return "openai/gpt-oss-120b:groq"
        if self.llm_provider == "openrouter":
            return "anthropic/claude-sonnet-5.5"
        return "claude-haiku-4-5"

    def resolved_profiles_dir(self) -> Path:
        if self.profiles_dir is not None:
            return self.profiles_dir
        return data_path("profiles", "profiles")


def get_settings() -> Settings:
    return Settings()
