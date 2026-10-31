"""Two sessions adding at once, through the real operations over real stores (Review Focus 1)."""

from collections.abc import Mapping, Sequence
from pathlib import Path

from applying import area_text, decision_text, spec_text
from fakes import CountingIds, FixedClock

from gitstore.repos import BRANCH, Ticker, bare_remote, clone, git, initialised, worktree
from lodge.app import AddOutcome, Committed, Gate, Lodge, PublishOutcome, Store
from lodge.core import CoreSettings, Tree, check_state, load
from lodge.gitstore import open_store

FIRST = [
    ("area.md", area_text("name: storage")),
    ("d.md", decision_text("changes:", "  - {entry: s-bbbbbb, action: create}")),
    ("s.md", spec_text("id: s-bbbbbb", "area: storage")),
]
A_DRAFTS = [
    ("d.md", decision_text("changes:", "  - {entry: s-cccccc, action: create}")),
    ("s.md", spec_text("id: s-cccccc", "area: storage", body="First session.")),
]
B_DRAFTS = [
    ("d.md", decision_text("changes:", "  - {entry: s-dddddd, action: create}")),
    ("s.md", spec_text("id: s-dddddd", "area: storage", body="Second session.")),
]


class Interleaved:
    """A store that runs `during` once, between the first `trees()` and the next `publish`."""

    def __init__(self, inner: Store, during: "Lodge") -> None:
        self.inner = inner
        self.during = during
        self.drafts = A_DRAFTS
        self.fired = False
        self.outcomes: list[PublishOutcome] = []

    def commit(self, paths: Sequence[str], message: str) -> Committed:
        return self.inner.commit(paths, message)

    def trees(self) -> tuple[Tree, Tree]:
        read = self.inner.trees()
        if not self.fired:
            self.fired = True
            assert self.during.add(self.drafts).outcome is AddOutcome.PUBLISHED
        return read

    def freshness(self) -> str | None:
        return self.inner.freshness()

    def gate(self, current: Tree) -> Gate:
        return self.inner.gate(current)

    def publish(self, base: Tree, writes: Mapping[str, str], message: str) -> PublishOutcome:
        outcome = self.inner.publish(base, writes, message)
        self.outcomes.append(outcome)
        return outcome


def lodge_over(store: Store, first_id: int) -> Lodge:
    return Lodge(store, FixedClock(), CountingIds(first=first_id), CoreSettings())


def remote_tip(remote: Path, tmp_path: Path) -> Tree:
    """The tip of the remote's branch, read through a fresh clone."""
    return open_store(clone(remote, "reader"), BRANCH, Ticker()).trees()[0]


def seeded_project(tmp_path: Path) -> tuple[Path, Path, Ticker]:
    remote = bare_remote(tmp_path)
    first, clock = initialised(remote, "first")
    assert lodge_over(open_store(first, BRANCH, clock), 1).add(FIRST).outcome is (
        AddOutcome.PUBLISHED
    )
    return remote, first, clock


def assert_both_published(tip: Tree) -> None:
    s = load(tip)
    assert {"s-bbbbbb", "s-cccccc", "s-dddddd"} <= set(s.entries)
    assert len(s.decisions) == 3
    assert s.areas["storage"].order == ("s-bbbbbb", "s-cccccc", "s-dddddd")
    assert check_state(s).ok, check_state(s).problems


def test_two_clones_add_at_once(tmp_path: Path) -> None:
    remote, first, clock = seeded_project(tmp_path)
    second = clone(remote, "second")
    a = lodge_over(open_store(first, BRANCH, clock), 20)
    b_store = open_store(second, BRANCH, Ticker())
    between = Interleaved(b_store, a)
    added = lodge_over(between, 40).add(B_DRAFTS)
    assert added.outcome is AddOutcome.PUBLISHED
    assert between.outcomes == [PublishOutcome.REJECTED, PublishOutcome.PUBLISHED]
    assert_both_published(remote_tip(remote, tmp_path))


def test_two_worktrees_of_one_clone_add_interleaved(tmp_path: Path) -> None:
    remote, first, clock = seeded_project(tmp_path)
    second = worktree(first, "second")
    a = lodge_over(open_store(first, BRANCH, clock), 20)
    between = Interleaved(open_store(second, BRANCH, clock), a)
    assert lodge_over(between, 40).add(B_DRAFTS).outcome is AddOutcome.PUBLISHED
    assert between.outcomes == [PublishOutcome.REJECTED, PublishOutcome.PUBLISHED]
    assert_both_published(remote_tip(remote, tmp_path))


def test_stale_tree_publish_rejected_ref_unchanged(tmp_path: Path) -> None:
    remote, first, clock = seeded_project(tmp_path)
    second = worktree(first, "second")
    a = open_store(first, BRANCH, clock)
    b = open_store(second, BRANCH, clock)
    a_read, _ = a.trees()
    b_read, _ = b.trees()
    path = "lodge/attachments/d-aaaaaa/a.txt"
    assert a.publish(a_read, {path: "a\n"}, "a") is PublishOutcome.PUBLISHED
    tip = git(first, "rev-parse", "refs/remotes/origin/lodge")
    assert b.publish(b_read, {"lodge/attachments/d-aaaaaa/b.txt": "b\n"}, "b") is (
        PublishOutcome.REJECTED
    )
    assert git(first, "rev-parse", "refs/remotes/origin/lodge") == tip
    assert git(remote, "rev-parse", "lodge") == tip
