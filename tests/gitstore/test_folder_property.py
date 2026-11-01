"""The existing two-hundred-history oracle also exercises persistent folder deltas."""

import time
from pathlib import Path
from unittest.mock import patch

from gitstore import test_identity_property as oracle
from gitstore.repos import CHECKOUT, Ticker
from gitstore.test_identity import prepared
from lodge.app import Store
from lodge.gitstore import folders, open_index, open_store


def check_histories(tmp_path: Path) -> None:
    repo, _ = prepared(tmp_path)
    index = open_index(repo / ".git")
    assert index is not None

    def indexed(_path: Path) -> tuple[Path, Store]:
        return repo, open_store(repo, CHECKOUT, Ticker(), index=index)

    try:
        with (
            patch.object(oracle, "prepared", indexed),
            patch.object(folders, "time_ns", lambda: time.time_ns() + 3_000_000_000, create=True),
        ):
            oracle.test_random_edits_agree(tmp_path)
    finally:
        index.close()


def test_folder_property(tmp_path: Path) -> None:
    check_histories(tmp_path)
