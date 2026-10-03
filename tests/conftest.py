import pytest

from consta.config import get_settings


@pytest.fixture
def profiles_dir():
    return get_settings().resolved_profiles_dir()
