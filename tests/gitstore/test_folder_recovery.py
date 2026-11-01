"""Partial folder walks must be retried after permissions recover."""

import os
from pathlib import Path

import pytest

from gitstore.repos import write
from gitstore.test_folders import cached as cached
from gitstore.test_folders import mode as mode
from gitstore.test_folders import opened, seed
from gitstore.test_identity import agrees
from lodge.gitstore.index_db import IndexDB


@pytest.mark.skipif(os.geteuid() == 0, reason="root can list unreadable folders")
@pytest.mark.parametrize("existing", [False, True])
def test_unlistable_folder_recovers(cached: tuple[Path, IndexDB], existing: bool) -> None:
    repo, index = seed(cached)
    folder = "lodge/decisions" if existing else "lodge/decisions/new"
    child = f"{folder}/untracked.md"
    write(repo, child, "Recovered berth.\n")
    (repo / folder).chmod(0)
    try:
        try:
            list((repo / folder).iterdir())
        except PermissionError:
            pass
        else:
            pytest.skip("filesystem does not enforce directory permissions")
        assert child not in agrees(opened(repo, index)).blobs
    finally:
        (repo / folder).chmod(0o755)
    assert child in agrees(opened(repo, index)).blobs
