"""Explicit-path commits with the checkout's identity and normal git safeguards."""

import subprocess
from pathlib import Path

import pytest
from fakes import FixedClock

from gitstore.repos import checkout_project, commit, git, write
from lodge.app import CommitOutcome, Committed, LodgeError
from lodge.gitstore import StoreSettings, open_store
from lodge.gitstore.commit import commit_paths


def work(tmp_path: Path) -> Path:
    _, repo = checkout_project(tmp_path)
    git(repo, "switch", "-c", "work")
    write(repo, "one.txt", "one")
    write(repo, "other.txt", "other")
    git(repo, "add", "one.txt", "other.txt")
    return repo


def perform(repo: Path) -> Committed:
    return commit_paths(repo, "main", ("one.txt",), "Viewer write", 0)


def test_commits_only_the_named_paths(tmp_path: Path) -> None:
    repo = work(tmp_path)
    assert perform(repo).outcome is CommitOutcome.COMMITTED
    assert git(repo, "diff", "--cached", "--name-only") == "other.txt"
    assert git(repo, "show", "--pretty=", "--name-only", "HEAD") == "one.txt"


def test_commit_takes_the_checkouts_identity(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = work(tmp_path)
    for role in ("AUTHOR", "COMMITTER"):
        monkeypatch.delenv(f"GIT_{role}_NAME")
        monkeypatch.delenv(f"GIT_{role}_EMAIL")
    git(repo, "config", "user.name", "Storage Author")
    git(repo, "config", "user.email", "storage@example.com")
    assert perform(repo).outcome is CommitOutcome.COMMITTED
    assert git(repo, "show", "-s", "--format=%an") == "Storage Author"


def test_no_commit_on_the_base_branch(tmp_path: Path) -> None:
    repo = work(tmp_path)
    git(repo, "switch", "main")
    before = git(repo, "rev-parse", "HEAD")
    assert perform(repo).outcome is CommitOutcome.ON_BASE
    assert git(repo, "rev-parse", "HEAD") == before
    assert "one.txt" in git(repo, "diff", "--cached", "--name-only")


def test_no_commit_on_a_detached_head(tmp_path: Path) -> None:
    repo = work(tmp_path)
    git(repo, "switch", "--detach")
    assert perform(repo).outcome is CommitOutcome.DETACHED


def conflict(repo: Path, operation: str) -> None:
    git(repo, "reset", "--hard")
    commit(repo, "conflict.txt", "start\n", "Start conflict")
    git(repo, "branch", "side")
    commit(repo, "conflict.txt", "work\n", "Work conflict")
    target = git(repo, "rev-parse", "HEAD")
    git(repo, "switch", "side")
    commit(repo, "conflict.txt", "side\n", "Side conflict")
    if operation == "revert":
        target = git(repo, "rev-parse", "HEAD~1")
    with pytest.raises(subprocess.CalledProcessError):
        git(repo, operation, target if operation != "merge" else "work")
    write(repo, "one.txt", "staged during conflict")
    git(repo, "add", "one.txt")


def test_no_commit_during_a_merge(tmp_path: Path) -> None:
    repo = work(tmp_path)
    conflict(repo, "merge")
    assert perform(repo).outcome is CommitOutcome.IN_PROGRESS
    assert "one.txt" in git(repo, "diff", "--cached", "--name-only")


def test_no_commit_during_a_revert(tmp_path: Path) -> None:
    repo = work(tmp_path)
    conflict(repo, "revert")
    assert perform(repo).outcome is CommitOutcome.IN_PROGRESS
    assert "one.txt" in git(repo, "diff", "--cached", "--name-only")
    assert (repo / git(repo, "rev-parse", "--git-path", "REVERT_HEAD")).exists()


def test_no_commit_during_a_rebase(tmp_path: Path) -> None:
    repo = work(tmp_path)
    (repo / git(repo, "rev-parse", "--git-path", "rebase-merge")).mkdir()
    assert perform(repo).outcome is CommitOutcome.IN_PROGRESS


def test_no_commit_during_a_cherry_pick(tmp_path: Path) -> None:
    repo = work(tmp_path)
    conflict(repo, "cherry-pick")
    assert perform(repo).outcome is CommitOutcome.IN_PROGRESS
    assert "one.txt" in git(repo, "diff", "--cached", "--name-only")


def test_locked_index_retries_once_then_locked(tmp_path: Path) -> None:
    repo = work(tmp_path)
    (repo / git(repo, "rev-parse", "--git-path", "index.lock")).touch()
    slept: list[float] = []
    result = commit_paths(repo, "main", ("one.txt",), "Write", 0.25, slept.append)
    assert result.outcome is CommitOutcome.LOCKED and slept == [0.25]


def test_lock_gone_on_retry_commits(tmp_path: Path) -> None:
    repo = work(tmp_path)
    lock = repo / git(repo, "rev-parse", "--git-path", "index.lock")
    lock.touch()
    slept: list[float] = []

    def unlock(seconds: float) -> None:
        slept.append(seconds)
        lock.unlink()

    result = commit_paths(repo, "main", ("one.txt",), "Write", 0.25, unlock)
    assert result.outcome is CommitOutcome.COMMITTED and slept == [0.25]


def test_other_failure_is_failed_with_gits_line(tmp_path: Path) -> None:
    repo = work(tmp_path)
    hook = repo / git(repo, "rev-parse", "--git-path", "hooks/pre-commit")
    hook.write_text("#!/bin/sh\necho 'Storage hook refused' >&2\nexit 1\n")
    hook.chmod(0o755)
    result = perform(repo)
    assert result.outcome is CommitOutcome.FAILED
    assert result.detail == "Storage hook refused"


def test_silent_hook_failure_has_detail(tmp_path: Path) -> None:
    repo = work(tmp_path)
    hook = repo / git(repo, "rev-parse", "--git-path", "hooks/commit-msg")
    hook.write_text("#!/bin/sh\nexit 1\n")
    hook.chmod(0o755)
    before = git(repo, "rev-parse", "HEAD")
    result = perform(repo)
    assert result.outcome is CommitOutcome.FAILED
    assert result.detail == "git commit exited with status 1"
    assert git(repo, "rev-parse", "HEAD") == before
    assert git(repo, "diff", "--cached", "--name-only").splitlines() == ["one.txt", "other.txt"]


def test_commit_paths_are_literal(tmp_path: Path) -> None:
    repo = work(tmp_path)
    for name in ("a*.md", "another.md"):
        write(repo, name, name)
        git(repo, "add", "--", name)
    result = commit_paths(repo, "main", ("a*.md",), "Literal file", 0)
    assert result.outcome is CommitOutcome.COMMITTED
    assert git(repo, "show", "--pretty=", "--name-only", "HEAD") == "a*.md"
    assert "another.md" in git(repo, "diff", "--cached", "--name-only")


def test_checkout_store_commits_by_path(tmp_path: Path) -> None:
    repo = work(tmp_path)
    store = open_store(repo, StoreSettings(), FixedClock())
    git(repo, "switch", "main")
    assert store.commit(("one.txt",), "Base").outcome is CommitOutcome.ON_BASE
    git(repo, "switch", "work")
    assert store.commit(("one.txt",), "Work").outcome is CommitOutcome.COMMITTED
    assert git(repo, "diff", "--cached", "--name-only") == "other.txt"


def test_branch_store_refuses_commit(tmp_path: Path) -> None:
    repo = work(tmp_path)
    store = open_store(repo, StoreSettings(mode="branch"), FixedClock())
    with pytest.raises(LodgeError, match="branch mode commits when it publishes"):
        store.commit(("one.txt",), "No")
