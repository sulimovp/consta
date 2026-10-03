import re
from pathlib import Path

import yaml

from consta.models.profile import EcosystemProfile


class ProfileNotFoundError(FileNotFoundError):
    pass


class ProfileStaleError(ValueError):
    pass


_PROFILE_ID_RE = re.compile(r"[A-Za-z0-9][A-Za-z0-9_-]*")


def load_profile(profiles_dir: Path, ecosystem_id: str, *, allow_stale: bool = False) -> EcosystemProfile:
    # Ids come from CLI flags and web forms; never let them escape profiles_dir.
    if not _PROFILE_ID_RE.fullmatch(ecosystem_id):
        raise ProfileNotFoundError(f"Invalid profile name {ecosystem_id!r}")
    path = profiles_dir / f"{ecosystem_id}.yaml"
    if not path.is_file():
        raise ProfileNotFoundError(f"No profile at {path}")

    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    profile = EcosystemProfile.model_validate(raw)
    if profile.is_stale() and not allow_stale:
        raise ProfileStaleError(
            f"Profile {ecosystem_id!r} last verified {profile.last_verified}; "
            f"refresh or pass allow_stale=True"
        )
    return profile


def list_profiles(profiles_dir: Path) -> list[str]:
    return sorted(p.stem for p in profiles_dir.glob("*.yaml") if not p.name.startswith("_"))
