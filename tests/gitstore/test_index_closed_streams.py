"""Actual closed output descriptors retain the historical command exit status."""

import subprocess
import sys
from pathlib import Path

import pytest
from builders import decision, files_of

from gitstore.repos import checkout_project, git, write


@pytest.mark.parametrize("fd", [1, 2])
@pytest.mark.parametrize("command", [["show", "d-aaaaaa"], ["waiting"], ["threads"]])
@pytest.mark.parametrize("index_off", [False, True])
def test_closed_output_descriptor(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, fd: int, command: list[str], index_off: bool
) -> None:
    _, repo = checkout_project(tmp_path)
    for path, text in files_of(decision(id="d-aaaaaa")).items():
        write(repo, path, text)
    git(repo, "add", "--", "lodge")
    git(repo, "commit", "-m", "Synthetic records")
    if index_off:
        monkeypatch.setenv("LODGE_INDEX", "off")
    result = subprocess.run(
        [
            "bash",
            "-c",
            f'exec "$@" {fd}>&-',
            "closed-output",
            sys.executable,
            "-m",
            "lodge.main",
            *command,
        ],
        cwd=repo,
        capture_output=True,
        text=True,
        timeout=10,
    )
    assert result.returncode == 0, result.stderr
    assert "Traceback" not in result.stderr
