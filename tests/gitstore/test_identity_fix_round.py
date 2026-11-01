"""Production uses stat candidates and fails conservatively."""

import subprocess
from collections.abc import Sequence
from pathlib import Path
from unittest.mock import patch

from gitstore.repos import git, write
from gitstore.test_identity import RECORD, agrees, prepared
from lodge.gitstore import git as runner


def test_production_uses_stat_candidates(tmp_path: Path) -> None:
    _, store = prepared(tmp_path)
    with patch.object(runner, "run_many", wraps=runner.run_many) as calls:
        agrees(store)
    assert calls.call_count == 1


def test_failed_ls_files_reads_every_base_path(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)
    git(repo, "update-index", "--assume-unchanged", RECORD)
    write(repo, RECORD, "Hidden edit.\n")
    original = runner.run_many

    def failed(
        calls: Sequence[Sequence[str]], cwd: Path
    ) -> list[subprocess.CompletedProcess[bytes]]:
        results = original(calls, cwd)
        results[2] = subprocess.CompletedProcess(calls[2], 1, b"", b"failed flags")
        return results

    with patch.object(runner, "run_many", failed):
        agrees(store)
