"""What the operations need from outside: the store, the clock, and the entropy."""

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum
from typing import Protocol

from lodge.core import Tree


class PublishOutcome(StrEnum):
    PUBLISHED = "published"
    STAGED = "staged"
    REJECTED = "rejected"


class CommitOutcome(StrEnum):
    COMMITTED = "committed"
    ON_BASE = "on the base branch"
    DETACHED = "on a detached HEAD"
    IN_PROGRESS = "during a merge, rebase, cherry-pick, or revert"
    LOCKED = "git's index is locked by another process"
    FAILED = "git could not commit"


@dataclass(frozen=True)
class Committed:
    outcome: CommitOutcome
    detail: str = ""


@dataclass(frozen=True)
class Gate:
    """What `check --gate` compares: each of the `checked` states, by label, with `published`.

    A label is empty when there is one state; `notes` are printed with the result.
    """

    published: Tree
    checked: tuple[tuple[str, Tree], ...]
    notes: tuple[str, ...] = ()


class Store(Protocol):
    def commit(self, paths: Sequence[str], message: str) -> Committed:
        """Commit exactly `paths` with the checkout's identity and hooks.

        Leave other staged files staged; the outcome says why when it does not commit.
        """
        ...

    def trees(self) -> tuple[Tree, Tree]:
        """The current and the published state, from one read."""
        ...

    def freshness(self) -> str | None:
        """How fresh the data is when it comes from a shared branch; None when it is local."""
        ...

    def gate(self, current: Tree) -> Gate:
        """What the gate compares for `current`, the tree `trees` returned; a `LodgeError` when
        there is no published state to compare with."""
        ...

    def publish(self, base: Tree, writes: Mapping[str, str], message: str) -> PublishOutcome:
        """Write `writes` on top of `base`; REJECTED when a path in `writes`, or the branch tip, no
        longer matches `base`."""
        ...


class Clock(Protocol):
    def now(self) -> datetime:
        """The time, timezone-aware."""
        ...

    def sleep(self, seconds: float) -> None:
        """Wait, so that `now` moves on by at least `seconds`."""
        ...


class IdSource(Protocol):
    def entropy(self) -> bytes:
        """At least six random bytes."""
        ...
