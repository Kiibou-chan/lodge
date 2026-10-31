"""Commit explicit paths, with the checkout's identity and hooks, leaving other staged work."""

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
    names = (
        "MERGE_HEAD",
        "CHERRY_PICK_HEAD",
        "REVERT_HEAD",
        "rebase-merge",
        "rebase-apply",
        "sequencer",
    )
    git_paths = run(["rev-parse", *(a for n in names for a in ("--git-path", n))], root)
    for path in git_paths.splitlines():
        if (root / path).exists():
            return Committed(CommitOutcome.IN_PROGRESS)
    for number in range(2):
        done = attempt(
            ["--literal-pathspecs", "commit", "--only", "--quiet", "-m", message, "--", *paths],
            root,
        )
        if done.returncode == 0:
            return Committed(CommitOutcome.COMMITTED)
        if b"index.lock" not in done.stderr:
            return Committed(
                CommitOutcome.FAILED,
                first_line(done.stderr, done.stdout)
                or f"git commit exited with status {done.returncode}",
            )
        if number == 0:
            sleep(retry_seconds)
    return Committed(CommitOutcome.LOCKED)
