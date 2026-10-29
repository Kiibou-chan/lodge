"""In-memory ports for the app tests; the project is made up."""

from collections.abc import Mapping
from datetime import datetime, timedelta, timezone

from builders import files_of

from lodge.app import Gate, PublishOutcome
from lodge.core import Area, Decision, SpecEntry, Tree

START = datetime(2026, 10, 29, 9, 30, tzinfo=timezone(timedelta(hours=1)))


class MemoryStore:
    """One tree, or with `staged=True` a working tree and a published one that stays put.

    Another session's change lands as `moves_after_read` (after the next `trees()`) or as one of
    `reject_next`'s changes (applied, then the publish is rejected).
    """

    def __init__(self, *items: Area | Decision | SpecEntry, staged: bool = False) -> None:
        self.files = files_of(*items)
        self.published = dict(self.files)
        self.staged = staged
        self.rev = 0
        self.stamp: str | None = "fetched 2026-10-29T08:00:00+00:00"
        self.publishes: list[tuple[dict[str, str], str]] = []
        self.attempts = 0
        self.gate_for: Gate | None = None
        self._moves: list[Mapping[str, str]] = []
        self._rejections: list[Mapping[str, str]] = []

    def trees(self) -> tuple[Tree, Tree]:
        current = Tree(str(self.rev), dict(self.files))
        published = Tree(str(self.rev), dict(self.published)) if self.staged else current
        if self._moves:
            self._land(self._moves.pop(0))
        return current, published

    def freshness(self) -> str | None:
        return self.stamp

    def gate(self, current: Tree) -> Gate:
        if self.gate_for is not None:
            return self.gate_for
        published = Tree(str(self.rev), dict(self.published)) if self.staged else current
        return Gate(published, (("", current),))

    def publish(self, base: Tree, writes: Mapping[str, str], message: str) -> PublishOutcome:
        self.attempts += 1
        if self._rejections:
            self._land(self._rejections.pop(0))
            return PublishOutcome.REJECTED
        if base.rev != str(self.rev):
            return PublishOutcome.REJECTED
        self.publishes.append((dict(writes), message))
        self.files.update(writes)
        self.rev += 1
        if not self.staged:
            self.published = dict(self.files)
        return PublishOutcome.STAGED if self.staged else PublishOutcome.PUBLISHED

    def moves_after_read(self, change: Mapping[str, str]) -> None:
        self._moves.append(change)

    def reject_next(self, *changes: Mapping[str, str]) -> None:
        self._rejections.extend(changes)

    def _land(self, change: Mapping[str, str]) -> None:
        self.files.update(change)
        self.rev += 1
        if not self.staged:
            self.published = dict(self.files)


class FixedClock:
    """The reading `start`, then one `step` later at each further call; sleeping moves it on."""

    def __init__(self, start: datetime = START, step: timedelta = timedelta(0)) -> None:
        self.start = start
        self.step = step
        self.calls = 0
        self.slept: list[float] = []

    def now(self) -> datetime:
        self.calls += 1
        return self.start + self.step * (self.calls - 1)

    def sleep(self, seconds: float) -> None:
        self.slept.append(seconds)
        self.start += timedelta(seconds=seconds)


class CountingIds:
    """Entropy of six equal bytes, counting up from `first`: the IDs `x-111111`, `x-222222`, ..."""

    def __init__(self, first: int = 1, step: int = 1) -> None:
        self.next = first
        self.step = step
        self.draws = 0

    def entropy(self) -> bytes:
        self.draws += 1
        value = self.next
        self.next += self.step
        return bytes([value]) * 6
