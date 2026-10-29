"""A push that loses a real race is `REJECTED`, and `add` retries it (Review Focus 1)."""

import sys
from pathlib import Path

import pytest
from applying import area_text, decision_text, spec_text
from fakes import CountingIds, FixedClock

from gitstore.repos import BRANCH, Ticker, bare_remote, clone, git, initialised
from lodge.app import AddOutcome, Lodge, PublishOutcome
from lodge.core import CoreSettings, check_state, load
from lodge.gitstore import open_store

FIRST = [
    ("area.md", area_text("name: storage")),
    ("d.md", decision_text("changes:", "  - {entry: s-bbbbbb, action: create}")),
    ("s.md", spec_text("id: s-bbbbbb", "area: storage")),
]
MINE = [
    ("d.md", decision_text("changes:", "  - {entry: s-cccccc, action: create}")),
    ("s.md", spec_text("id: s-cccccc", "area: storage", body="Mine.")),
]
THEIRS = [
    ("d.md", decision_text("changes:", "  - {entry: s-dddddd, action: create}")),
    ("s.md", spec_text("id: s-dddddd", "area: storage", body="Theirs.")),
]


def lodge_over(repo: Path, clock: Ticker, first_id: int) -> Lodge:
    store = open_store(repo, BRANCH, clock)
    return Lodge(store, FixedClock(), CountingIds(first=first_id), CoreSettings())


def rigged_remote(tmp_path: Path) -> tuple[Path, Path, Ticker]:
    """A remote whose first received push finds the branch already moved to another session's.

    Another clone publishes THEIRS, the remote branch is put back to where it was, and a
    pre-receive hook moves it forward again, once, while the first push is being received.
    """
    remote = bare_remote(tmp_path)
    mine, clock = initialised(remote, "mine")
    assert lodge_over(mine, clock, 1).add(FIRST).outcome is AddOutcome.PUBLISHED
    before = git(remote, "rev-parse", "lodge")
    theirs = clone(remote, "theirs")
    assert lodge_over(theirs, Ticker(), 50).add(THEIRS).outcome is AddOutcome.PUBLISHED
    other = git(remote, "rev-parse", "lodge")
    git(remote, "update-ref", "refs/heads/lodge", before)
    marker = tmp_path / "hook-ran"
    hook = remote / "hooks" / "pre-receive"
    hook.write_text(
        f"#!/bin/sh\n[ -e {marker} ] && exit 0\ntouch {marker}\n"
        "env -u GIT_QUARANTINE_PATH -u GIT_OBJECT_DIRECTORY -u GIT_ALTERNATE_OBJECT_DIRECTORIES "
        f"git update-ref refs/heads/lodge {other}\n"
    )
    hook.chmod(0o755)
    return remote, mine, clock


def test_push_that_loses_a_race_is_rejected_and_marks_stale(tmp_path: Path) -> None:
    remote, mine, clock = rigged_remote(tmp_path)
    store = open_store(mine, BRANCH, clock)
    current, _ = store.trees()
    outcome = store.publish(current, {"lodge/attachments/d-aaaaaa/a.txt": "a\n"}, "m")
    assert outcome is PublishOutcome.REJECTED
    assert git(remote, "rev-parse", "lodge") != current.rev
    assert any(p.endswith("s-dddddd-transcripts.md") for p in store.trees()[0].files)


def test_add_retries_after_losing_a_race_and_both_decisions_land(tmp_path: Path) -> None:
    remote, mine, clock = rigged_remote(tmp_path)
    assert lodge_over(mine, clock, 20).add(MINE).outcome is AddOutcome.PUBLISHED
    tip = open_store(clone(remote, "reader"), BRANCH, Ticker()).trees()[0]
    s = load(tip)
    assert {"s-bbbbbb", "s-cccccc", "s-dddddd"} <= set(s.entries)
    assert len(s.decisions) == 3
    assert check_state(s).ok, check_state(s).problems


def lost_report(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> tuple[Path, Path, Ticker]:
    """A remote reached over a stand-in for ssh that drops the first push's report."""
    remote = bare_remote(tmp_path)
    repo, clock = initialised(remote, "mine")
    git(repo, "remote", "set-url", "origin", f"ssh://fake{remote}")
    ssh = Path(__file__).with_name("fakessh.py")
    monkeypatch.setenv("GIT_SSH_COMMAND", f"{sys.executable} -I {ssh}")
    monkeypatch.setenv("GIT_SSH_VARIANT", "simple")
    monkeypatch.setenv("FAKESSH_MARKER", str(tmp_path / "dropped"))
    return remote, repo, clock


def test_a_push_that_landed_with_its_report_lost_is_published(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    remote, repo, clock = lost_report(tmp_path, monkeypatch)
    store = open_store(repo, BRANCH, clock)
    current, _ = store.trees()
    path = "lodge/attachments/d-aaaaaa/a.txt"
    assert store.publish(current, {path: "a\n"}, "m") is PublishOutcome.PUBLISHED
    assert (tmp_path / "dropped").exists()
    assert git(repo, "rev-parse", "refs/remotes/origin/lodge") == git(remote, "rev-parse", "lodge")
    assert git(remote, "rev-list", "--count", f"{current.rev}..lodge") == "1"


def test_add_over_a_lost_report_leaves_one_decision(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    remote, repo, clock = lost_report(tmp_path, monkeypatch)
    lodge = lodge_over(repo, clock, 1)
    assert lodge.add([("d.md", decision_text())]).outcome is AddOutcome.PUBLISHED
    assert (tmp_path / "dropped").exists()
    tip = open_store(clone(remote, "reader"), BRANCH, Ticker()).trees()[0]
    assert len(load(tip).decisions) == 1


def test_a_landed_push_that_another_clone_built_on_is_published_and_the_newer_ref_stays(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    remote, repo, clock = lost_report(tmp_path, monkeypatch)
    monkeypatch.setenv(
        "FAKESSH_AFTER",
        f"cd {remote} && export GIT_AUTHOR_NAME=a GIT_AUTHOR_EMAIL=a@example.com "
        "GIT_COMMITTER_NAME=a GIT_COMMITTER_EMAIL=a@example.com && "
        "t=$(git rev-parse refs/heads/lodge) && "
        'c=$(git commit-tree -p "$t" -m later "$t^{tree}") && '
        'git update-ref refs/heads/lodge "$c" && '
        f"git -C {repo} fetch --quiet origin +refs/heads/lodge:refs/remotes/origin/lodge",
    )
    store = open_store(repo, BRANCH, clock)
    current, _ = store.trees()
    path = "lodge/attachments/d-aaaaaa/a.txt"
    assert store.publish(current, {path: "a\n"}, "m") is PublishOutcome.PUBLISHED
    assert git(remote, "rev-list", "--count", f"{current.rev}..lodge") == "2"
    assert git(repo, "rev-parse", "refs/remotes/origin/lodge") == git(remote, "rev-parse", "lodge")
