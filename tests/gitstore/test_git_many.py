"""Concurrent git calls preserve ordering, cancellation, and missing-git errors."""

import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from gitstore.repos import git
from lodge.gitstore import git as runner
from lodge.gitstore.errors import GitMissing


def test_results_in_call_order(tmp_path: Path) -> None:
    git(tmp_path, "init", "-b", "main")
    results = runner.run_many(
        [["rev-parse", "--is-inside-work-tree"], ["config", "absent.key"]], tmp_path
    )
    assert [(r.returncode, r.stdout) for r in results] == [(0, b"true\n"), (1, b"")]


def test_all_started_before_any_awaited(tmp_path: Path) -> None:
    events: list[str] = []

    class Process:
        returncode = 0

        def __init__(self, *args: object, **kwargs: object) -> None:
            events.append("start")

        def communicate(self) -> tuple[bytes, bytes]:
            events.append("wait")
            return b"", b""

    with patch.object(subprocess, "Popen", Process):
        runner.run_many([["status"], ["diff"], ["config", "--list"]], tmp_path)
    assert events == ["start"] * 3 + ["wait"] * 3


def test_request_exit_waits_for_every_call(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    waited: list[int] = []

    class Process:
        returncode = 0

        def __init__(self, *args: object, **kwargs: object) -> None:
            pass

        def communicate(self) -> tuple[bytes, bytes]:
            if not waited:
                runner.request_exit(23)
            waited.append(1)
            return b"", b""

    monkeypatch.setattr(runner, "_pending", None)
    with patch.object(subprocess, "Popen", Process), pytest.raises(SystemExit) as stop:
        runner.run_many([["status"], ["diff"]], tmp_path)
    assert stop.value.code == 23
    assert waited == [1, 1]


def test_missing_git_raises_git_missing(tmp_path: Path) -> None:
    with (
        patch.object(subprocess, "Popen", side_effect=FileNotFoundError),
        pytest.raises(GitMissing),
    ):
        runner.run_many([["status"]], tmp_path)
