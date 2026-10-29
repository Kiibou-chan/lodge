import os
import time
from pathlib import Path

import pytest

from gitstore.repos import (
    BRANCH,
    Ticker,
    bare_remote,
    clone,
    git,
    initialised,
    publish_one,
    seeded,
    worktree,
)
from lodge.app import LodgeError, PublishOutcome
from lodge.core import load
from lodge.gitstore import NotInitialised, StoreSettings, init_store, open_store

DECISION = "lodge/decisions/d-aaaaaa-keep.md"
ATTACHMENT = "lodge/attachments/d-aaaaaa/log.txt"
KEPT = {"lodge/decisions/.gitkeep", "lodge/spec/.gitkeep"}


def test_branch_publish_commits_on_base_and_pushes(tmp_path: Path) -> None:
    remote = bare_remote(tmp_path)
    repo, clock = initialised(remote, "work")
    first = git(remote, "rev-parse", "lodge")
    main = git(repo, "rev-parse", "main")
    store = open_store(repo, BRANCH, clock)
    current, published = store.trees()
    assert current is published and current.rev == first
    outcome = store.publish(current, {DECISION: "text\n"}, "lodge: add d-aaaaaa Keep")
    assert outcome is PublishOutcome.PUBLISHED
    tip = git(remote, "rev-parse", "lodge")
    assert git(remote, "rev-parse", f"{tip}^") == first
    assert git(remote, "log", "-1", "--format=%B", tip) == "lodge: add d-aaaaaa Keep"
    assert git(remote, "show", f"{tip}:{DECISION}") == "text"
    assert git(repo, "rev-parse", "refs/remotes/origin/lodge") == tip
    assert git(repo, "rev-parse", "main") == main and git(repo, "status", "--porcelain") == ""
    assert not (repo / "lodge").exists()
    assert set(store.trees()[0].files) == KEPT | {DECISION}


def test_branch_publish_keeps_other_files_and_appends_trailer(tmp_path: Path) -> None:
    remote = bare_remote(tmp_path)
    repo, clock = initialised(remote, "work")
    settings = StoreSettings(mode="branch", commit_trailer="Co-Authored-By: A <a@example.com>")
    store = open_store(repo, settings, clock)
    current, _ = store.trees()
    store.publish(current, {DECISION: "one\n"}, "first line\n\nbody")
    current, _ = store.trees()
    store.publish(current, {DECISION: "two\n"}, "second")
    log = git(remote, "log", "--format=%B%x00", "lodge").split("\x00")
    assert log[0].strip() == "second\n\nCo-Authored-By: A <a@example.com>"
    assert log[1].strip() == "first line\n\nbody\n\nCo-Authored-By: A <a@example.com>"
    assert git(remote, "show", f"lodge:{DECISION}") == "two"
    assert git(remote, "ls-tree", "-r", "--name-only", "lodge").splitlines() == sorted(
        KEPT | {DECISION}
    )


def test_branch_fetch_only_when_stale(tmp_path: Path) -> None:
    remote = bare_remote(tmp_path)
    a, clock = initialised(remote, "a")
    store = open_store(a, BRANCH, clock)
    assert DECISION not in store.trees()[0].files
    b = clone(remote, "b")
    publish_one(b, Ticker(), {DECISION: "from b\n"})
    clock.advance(30)
    assert DECISION not in store.trees()[0].files
    clock.advance(31)
    assert store.trees()[0].files[DECISION] == "from b\n"


def test_unrelated_fetch_does_not_refresh_stamp(tmp_path: Path) -> None:
    remote = bare_remote(tmp_path)
    a, clock = initialised(remote, "a")
    store = open_store(a, BRANCH, clock)
    store.trees()
    publish_one(clone(remote, "b"), Ticker(), {DECISION: "from b\n"})
    clock.advance(120)
    git(a, "fetch", "origin", "main")
    assert store.trees()[0].files[DECISION] == "from b\n"


def test_zero_staleness_always_fetches(tmp_path: Path) -> None:
    remote = bare_remote(tmp_path)
    a, clock = initialised(remote, "a")
    store = open_store(a, StoreSettings(mode="branch", max_staleness_seconds=0), clock)
    store.trees()
    publish_one(clone(remote, "b"), Ticker(), {DECISION: "from b\n"})
    assert DECISION in store.trees()[0].files


def test_freshness_line(tmp_path: Path) -> None:
    remote = bare_remote(tmp_path)
    repo, clock = initialised(remote, "work")
    store = open_store(repo, BRANCH, clock)
    current, _ = store.trees()
    assert store.freshness() == f"lodge@{current.rev[:7] if current.rev else ''}, fetched 0 s ago"
    clock.advance(12)
    assert store.freshness() == f"lodge@{(current.rev or '')[:7]}, fetched 12 s ago"


def test_branch_fetch_failure_serves_cache_and_says_so(tmp_path: Path) -> None:
    remote = bare_remote(tmp_path)
    repo, clock = initialised(remote, "work")
    store = open_store(repo, BRANCH, clock)
    store.trees()
    fetched = clock.at
    git(repo, "remote", "set-url", "origin", str(tmp_path / "gone.git"))
    clock.advance(120)
    current, published = store.trees()
    assert set(current.files) == KEPT and published == current
    assert store.freshness() == f"fetch failed; data as of {fetched.isoformat(timespec='seconds')}"
    git(repo, "remote", "set-url", "origin", str(remote))
    store.trees()
    assert store.freshness() is not None and "fetched 0 s ago" in store.freshness()  # type: ignore[operator]


def test_branch_moved_ref_rejected(tmp_path: Path) -> None:
    remote = bare_remote(tmp_path)
    repo, clock = initialised(remote, "work")
    a = open_store(repo, BRANCH, clock)
    b = open_store(worktree(repo, "second"), BRANCH, clock)
    stale, _ = a.trees()
    current, _ = b.trees()
    assert b.publish(current, {DECISION: "b\n"}, "m") is PublishOutcome.PUBLISHED
    tip = git(remote, "rev-parse", "lodge")
    assert a.publish(stale, {ATTACHMENT: "a\n"}, "m") is PublishOutcome.REJECTED
    assert git(remote, "rev-parse", "lodge") == tip


def test_branch_rejected_push_marks_stale(tmp_path: Path) -> None:
    remote = bare_remote(tmp_path)
    a, clock = initialised(remote, "a")
    store = open_store(a, BRANCH, clock)
    stale, _ = store.trees()
    publish_one(clone(remote, "b"), Ticker(), {DECISION: "from b\n"})
    assert store.publish(stale, {ATTACHMENT: "a\n"}, "m") is PublishOutcome.REJECTED
    assert git(remote, "show", f"lodge:{DECISION}") == "from b"
    assert ATTACHMENT not in git(remote, "ls-tree", "-r", "--name-only", "lodge")
    current, _ = store.trees()
    assert current.files[DECISION] == "from b\n"
    assert store.publish(current, {ATTACHMENT: "a\n"}, "m") is PublishOutcome.PUBLISHED


def test_branch_push_failure_other_than_rejection_is_an_error(tmp_path: Path) -> None:
    remote = bare_remote(tmp_path)
    repo, clock = initialised(remote, "work")
    store = open_store(repo, BRANCH, clock)
    current, _ = store.trees()
    hook = remote / "hooks" / "pre-receive"
    hook.write_text("#!/bin/sh\necho no >&2\nexit 1\n")
    hook.chmod(0o755)
    tip = git(repo, "rev-parse", "refs/remotes/origin/lodge")
    with pytest.raises(LodgeError):
        store.publish(current, {DECISION: "x\n"}, "m")
    assert git(repo, "rev-parse", "refs/remotes/origin/lodge") == tip


def test_attachments_listed(tmp_path: Path) -> None:
    remote = bare_remote(tmp_path)
    repo, clock = initialised(remote, "work")
    store = open_store(repo, BRANCH, clock)
    current, _ = store.trees()
    store.publish(current, {ATTACHMENT: "unread\n", DECISION: "d\n"}, "m")
    read, _ = store.trees()
    assert read.attachments == {ATTACHMENT} and ATTACHMENT not in read.files
    assert DECISION in read.files


def test_stray_and_non_utf8_files_reported(tmp_path: Path) -> None:
    remote = bare_remote(tmp_path)
    repo, clock = initialised(remote, "work")
    store = open_store(repo, BRANCH, clock)
    current, _ = store.trees()
    bad = b"---\nid: \xff\n---\n".decode("utf-8", errors="surrogateescape")
    store.publish(
        current, {"lodge/notes.txt": "stray\n", "lodge/decisions/d-bbbbbb-bad.md": bad}, "m"
    )
    problems = load(store.trees()[0]).problems
    assert {(p.path, p.check) for p in problems} == {
        ("lodge/notes.txt", 1),
        ("lodge/decisions/d-bbbbbb-bad.md", 1),
    }
    assert git(remote, "show", "lodge:lodge/decisions/d-bbbbbb-bad.md") == bad.rstrip("\n")


def lock_of(repo: Path) -> Path:
    return Path(git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir")) / "lodge.lock"


def test_read_that_cannot_take_the_lock_serves_the_cache_and_says_so(tmp_path: Path) -> None:
    remote = bare_remote(tmp_path)
    repo, clock = initialised(remote, "work")
    store = open_store(repo, BRANCH, clock, lock_wait_seconds=0.2)
    lock = lock_of(repo)
    lock.write_text("held")
    current, _ = store.trees()
    assert set(current.files) == KEPT
    assert store.freshness() == f"not fetched: another lodge holds {lock}; data as of unknown"
    assert lock.exists()


def test_read_serves_the_cache_when_the_lock_is_left_over(tmp_path: Path) -> None:
    remote = bare_remote(tmp_path)
    repo, clock = initialised(remote, "work")
    store = open_store(repo, BRANCH, clock, lock_wait_seconds=0.2)
    lock = lock_of(repo)
    lock.write_text("held")
    old = time.time() - 3600
    os.utime(lock, (old, old))
    store.trees()
    assert store.freshness() == (
        f"not fetched: {lock} is older than ten minutes and may be left over; "
        "delete it if no lodge is running; data as of unknown"
    )


def test_read_with_nothing_cached_and_a_held_lock_is_an_error(tmp_path: Path) -> None:
    remote = bare_remote(tmp_path)
    repo = seeded(remote, "work")
    store = open_store(repo, BRANCH, Ticker(), lock_wait_seconds=0.2)
    lock_of(repo).write_text("held")
    with pytest.raises(LodgeError, match=r"lodge\.lock"):
        store.trees()


def test_publish_still_waits_for_the_lock_and_reports_it(tmp_path: Path) -> None:
    remote = bare_remote(tmp_path)
    repo, clock = initialised(remote, "work")
    store = open_store(repo, BRANCH, clock, lock_wait_seconds=0.2)
    current, _ = store.trees()
    lock_of(repo).write_text("held")
    with pytest.raises(LodgeError, match=r"lodge\.lock"):
        store.publish(current, {DECISION: "x\n"}, "m")


def test_stamp_of_another_branch_counts_as_never_fetched(tmp_path: Path) -> None:
    remote = bare_remote(tmp_path)
    repo, clock = initialised(remote, "work")
    open_store(repo, BRANCH, clock).trees()
    elsewhere = StoreSettings(mode="branch", branch="records")
    with pytest.raises(NotInitialised, match="lodge init"):
        open_store(repo, elsewhere, clock).trees()
    gone = StoreSettings(mode="branch", remote="nope")
    with pytest.raises(LodgeError, match="cannot fetch nope/lodge") as raised:
        open_store(repo, gone, clock).trees()
    assert not isinstance(raised.value, NotInitialised)


def test_init_ignores_branches_that_only_end_in_the_name(tmp_path: Path) -> None:
    remote = bare_remote(tmp_path)
    repo = seeded(remote, "work")
    git(repo, "push", "origin", "main:refs/heads/feature/lodge")
    init_store(repo, BRANCH)
    assert git(remote, "rev-parse", "lodge") != git(remote, "rev-parse", "feature/lodge")


def test_submodule_entry_is_reported_not_dropped(tmp_path: Path) -> None:
    remote = bare_remote(tmp_path)
    repo, clock = initialised(remote, "work")
    sub = "lodge/spec/sub"
    base = git(repo, "rev-parse", "refs/remotes/origin/lodge")
    tree = git(repo, "mktree", input=f"160000 commit {base}\tsub\n")
    top = git(repo, "mktree", input=f"040000 tree {tree}\tspec\n")
    root = git(repo, "mktree", input=f"040000 tree {top}\tlodge\n")
    commit = git(repo, "commit-tree", root, "-m", "gitlink")
    git(repo, "push", "origin", f"{commit}:refs/heads/lodge", "--force")
    git(repo, "fetch", "origin", "+refs/heads/lodge:refs/remotes/origin/lodge")
    current, _ = open_store(repo, BRANCH, clock).trees()
    assert current.files[sub] == "" and sub in {p.path for p in load(current).problems}


def test_existing_attachment_is_never_overwritten(tmp_path: Path) -> None:
    remote = bare_remote(tmp_path)
    repo, clock = initialised(remote, "work")
    store = open_store(repo, BRANCH, clock)
    current, _ = store.trees()
    store.publish(current, {ATTACHMENT: "first\n"}, "m")
    current, _ = store.trees()
    with pytest.raises(LodgeError, match="attachment"):
        store.publish(current, {ATTACHMENT: "second\n"}, "m")
    assert git(remote, "show", f"lodge:{ATTACHMENT}") == "first"


def test_gate_says_it_runs_inside_add(tmp_path: Path) -> None:
    remote = bare_remote(tmp_path)
    repo, clock = initialised(remote, "work")
    store = open_store(repo, BRANCH, clock)
    current, _ = store.trees()
    assert store.gate(current).notes == (
        "in branch mode the gate runs inside lodge add; a push to the branch by hand skips it",
    )
