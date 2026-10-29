import sys
from collections.abc import Iterator
from pathlib import Path

import pytest

TESTS = Path(__file__).resolve().parents[1]
for folder in ("core", "app"):
    if str(TESTS / folder) not in sys.path:
        sys.path.insert(0, str(TESTS / folder))


@pytest.fixture(autouse=True)
def isolated_git(tmp_path_factory: pytest.TempPathFactory) -> Iterator[None]:
    """Git with no user or system configuration, a fixed identity, and no prompts."""
    config = tmp_path_factory.mktemp("gitconfig") / "config"
    config.write_text("")
    patch = pytest.MonkeyPatch()
    patch.setenv("GIT_CONFIG_GLOBAL", str(config))
    patch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    patch.setenv("GIT_TERMINAL_PROMPT", "0")
    for role in ("AUTHOR", "COMMITTER"):
        patch.setenv(f"GIT_{role}_NAME", "Test Author")
        patch.setenv(f"GIT_{role}_EMAIL", "test@example.com")
    for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR"):
        patch.delenv(name, raising=False)
    yield
    patch.undo()
