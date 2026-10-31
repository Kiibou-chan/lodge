"""Commit explicit paths, preserving git's identity, hooks, and other staged work."""

import time
from collections.abc import Callable, Sequence
from pathlib import Path

from lodge.app import CommitOutcome, Committed
from lodge.gitstore.git import attempt, first_line, run


def commit_paths(
    root: Path,
    base: str,
    paths: Sequence[str],
    message: str,
    retry_seconds: float,
    sleep: Callable[[float], None] = time.sleep,
) -> Committed:
    branch = attempt(["symbolic-ref", "--quiet", "--short", "HEAD"], root)
    if branch.returncode:
        return Committed(CommitOutcome.DETACHED)
    if branch.stdout.decode().strip() == base:
        return Committed(CommitOutcome.ON_BASE)
    for name in (
        "MERGE_HEAD",
        "CHERRY_PICK_HEAD",
        "REVERT_HEAD",
        "rebase-merge",
        "rebase-apply",
        "sequencer",
    ):
        if (root / run(["rev-parse", "--git-path", name], root)).exists():
            return Committed(CommitOutcome.IN_PROGRESS)
    for number in range(2):
        done = attempt(["commit", "--only", "--quiet", "-m", message, "--", *paths], root)
        if done.returncode == 0:
            return Committed(CommitOutcome.COMMITTED)
        if b"index.lock" not in done.stderr:
            return Committed(CommitOutcome.FAILED, first_line(done.stderr, done.stdout))
        if number == 0:
            sleep(retry_seconds)
    return Committed(CommitOutcome.LOCKED)
