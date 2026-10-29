"""A rewritten `lodge` branch is noticed by every read until it is acknowledged (G4)."""

import subprocess
from collections.abc import Sequence
from pathlib import Path

import pytest

from gitstore.repos import BRANCH, Ticker, bare_remote, clone, git, initialised, publish_one
from lodge.app import Store
from lodge.gitstore import open_store
from lodge.gitstore.git import attempt as real

DECISION = "lodge/decisions/d-aaaaaa-keep.md"
ACCEPTED = "refs/lodge/accepted"
ACK = f"git update-ref -d {ACCEPTED}"


def rewrite_remote(remote: Path, text: str) -> str:
    """Another clone amends the remote branch's last commit to hold `text`; the old tip."""
    old = git(remote, "rev-parse", "lodge")
    other = clone(remote, "rewriter")
    git(other, "fetch", "origin", "lodge")
    git(other, "checkout", "-q", "-b", "lodge", "FETCH_HEAD")
    (other / DECISION).write_text(text, encoding="utf-8")
    git(other, "add", "--", DECISION)
    git(other, "commit", "-q", "--amend", "-m", "tidied")
    git(other, "push", "--force", "origin", "lodge")
    return old


def with_decision(tmp_path: Path) -> tuple[Path, Path, Ticker, Store]:
    remote = bare_remote(tmp_path)
    repo, clock = initialised(remote, "work")
    publish_one(repo, clock, {DECISION: "kept whole\n"})
    store = open_store(repo, BRANCH, clock)
    store.trees()
    clock.advance(120)
    return remote, repo, clock, store


def test_first_read_accepts_the_tip(tmp_path: Path) -> None:
    _, repo, _, store = with_decision(tmp_path)
    assert git(repo, "rev-parse", ACCEPTED) == git(repo, "rev-parse", "refs/remotes/origin/lodge")
    assert "rewritten" not in (store.freshness() or "")


def test_rewritten_branch_is_said_and_compared(tmp_path: Path) -> None:
    remote, repo, _, store = with_decision(tmp_path)
    old = rewrite_remote(remote, "dropped\n")
    current, published = store.trees()
    assert current.files[DECISION] == "dropped\n"
    assert published.files[DECISION] == "kept whole\n"
    freshness = store.freshness() or ""
    assert "the lodge branch was rewritten since lodge last accepted it" in freshness
    assert ACK in freshness and "tell the author; only the author accepts a rewrite" in freshness
    assert git(repo, "rev-parse", ACCEPTED) == old
    gate = store.gate(current)
    assert gate.published.files[DECISION] == "kept whole\n"
    assert gate.checked == (("", current),)


def test_a_plain_git_fetch_does_not_hide_the_rewrite(tmp_path: Path) -> None:
    remote, repo, _, store = with_decision(tmp_path)
    rewrite_remote(remote, "dropped\n")
    git(repo, "fetch", "origin")
    current, published = store.trees()
    assert published.files[DECISION] == "kept whole\n"
    assert "was rewritten" in (store.freshness() or "")
    assert store.gate(current).published.files[DECISION] == "kept whole\n"


def test_the_rewrite_stands_for_a_later_process_and_a_commit_on_top(tmp_path: Path) -> None:
    remote, repo, clock, store = with_decision(tmp_path)
    old = rewrite_remote(remote, "dropped\n")
    current, _ = store.trees()
    store.publish(current, {"lodge/spec/.gitkeep": ""}, "m")
    later = open_store(repo, BRANCH, clock)
    _, published = later.trees()
    assert "was rewritten" in (later.freshness() or "")
    assert published.rev == old and git(repo, "rev-parse", ACCEPTED) == old


def test_deleting_the_accepted_ref_acknowledges_the_rewrite(tmp_path: Path) -> None:
    remote, repo, _, store = with_decision(tmp_path)
    rewrite_remote(remote, "dropped\n")
    store.trees()
    git(repo, "update-ref", "-d", ACCEPTED)
    current, published = store.trees()
    assert "was rewritten" not in (store.freshness() or "")
    assert published is current and store.gate(current).published is current
    assert git(repo, "rev-parse", ACCEPTED) == current.rev


def test_a_fast_forward_moves_the_accepted_tip(tmp_path: Path) -> None:
    remote, repo, _, store = with_decision(tmp_path)
    publish_one(clone(remote, "b"), Ticker(), {DECISION: "kept whole, longer\n"})
    current, published = store.trees()
    assert "was rewritten" not in (store.freshness() or "")
    assert published is current and git(repo, "rev-parse", ACCEPTED) == current.rev


def test_lodges_own_push_moves_the_accepted_tip(tmp_path: Path) -> None:
    _, repo, _, store = with_decision(tmp_path)
    current, _ = store.trees()
    store.publish(current, {"lodge/spec/.gitkeep": ""}, "m")
    assert git(repo, "rev-parse", ACCEPTED) == git(repo, "rev-parse", "refs/remotes/origin/lodge")
    assert git(repo, "rev-parse", ACCEPTED) != current.rev


def test_a_git_that_cannot_answer_is_not_taken_for_no_rewrite(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    remote, repo, _, store = with_decision(tmp_path)
    accepted = git(repo, "rev-parse", ACCEPTED)
    other = clone(remote, "later")
    publish_one(other, Ticker(), {"lodge/decisions/d-bbbbbb-more.md": "more\n"})

    def cannot_answer(args: Sequence[str], cwd: Path) -> "subprocess.CompletedProcess[bytes]":
        done = real(args, cwd)
        if args[0] != "merge-base":
            return done
        return subprocess.CompletedProcess(args, 128, b"", b"fatal: Not a valid commit name")

    monkeypatch.setattr("lodge.gitstore.accepted.attempt", cannot_answer)
    store.trees()
    assert "was rewritten" in (store.freshness() or "")
    assert git(repo, "rev-parse", ACCEPTED) == accepted
