"""A `lodge add` ended by SIGTERM or SIGHUP lets the running git finish, then releases the lock."""

import os
import signal
import subprocess
import sys
import time
from pathlib import Path

import pytest

from e2e.support import area_text, decision_text, entry_text
from gitstore.repos import bare_remote, git, initialised

ENTRY = "s-aaaaaa"


@pytest.mark.parametrize(
    ("sent", "code"), [(signal.SIGTERM, 143), (signal.SIGHUP, 129)], ids=["term", "hup"]
)
def test_signal_during_a_push_releases_the_lock(
    tmp_path: Path, sent: signal.Signals, code: int
) -> None:
    remote = bare_remote(tmp_path)
    repo, _ = initialised(remote, "work")
    (repo / ".lodge.toml").write_text('[store]\nmode = "branch"\n', encoding="utf-8")
    started = tmp_path / "pushing"
    hook = repo / ".git" / "hooks" / "pre-push"
    hook.write_text(f"#!/bin/sh\ntouch {started}\nsleep 2\n")
    hook.chmod(0o755)
    drafts = tmp_path / "drafts"
    drafts.mkdir()
    texts = {
        "area.md": area_text(ENTRY),
        "entry.md": entry_text(ENTRY),
        "decision.md": decision_text("Keep", "changes:", f"  - {{entry: {ENTRY}, action: create}}"),
    }
    for name, text in texts.items():
        (drafts / name).write_text(text, encoding="utf-8")
    lock = Path(git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir")) / "lodge.lock"
    process = subprocess.Popen(
        [sys.executable, "-m", "lodge.main", "add", *(str(drafts / n) for n in texts)],
        cwd=repo,
        env=os.environ,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    deadline = time.monotonic() + 20
    while not started.exists() and time.monotonic() < deadline:
        time.sleep(0.05)
    assert started.exists() and lock.exists()
    process.send_signal(sent)
    assert process.wait(timeout=20) == code
    assert not lock.exists()
    assert git(remote, "rev-list", "--count", "lodge") == "2"
    assert not (repo / ".git" / "index.lock").exists()
