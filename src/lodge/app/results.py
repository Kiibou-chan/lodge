"""What the operations return."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum

from lodge.app.ports import Committed
from lodge.core import CheckResult, Feedback, Level1, Level3, Problem, Thread


class AddOutcome(StrEnum):
    PUBLISHED = "published"
    STAGED = "staged"
    CHECK_FAILED = "check failed"
    DRY_RUN = "dry run"
    UNCHANGED = "nothing changed"


@dataclass(frozen=True)
class Read:
    """What every read carries: freshness, the problems no record holds, and every status."""

    freshness: str | None
    unrecorded: tuple[Problem, ...]
    statuses: Mapping[str, str] = field(default_factory=dict)


@dataclass(frozen=True)
class Shown:
    level1: Level1
    level2: str | None
    level3: Level3 | None
    read: Read
    changing: tuple[Level1, ...] = ()
    threads: tuple[Thread, ...] = ()


@dataclass(frozen=True)
class Listed:
    items: tuple[Level1, ...]
    read: Read
    more: int = 0


@dataclass(frozen=True)
class Added:
    ids: tuple[str, ...]
    feedback: tuple[Feedback, ...]
    check: CheckResult
    outcome: AddOutcome
    freshness: str | None = None
    minted: tuple[str, ...] = ()
    paths: tuple[str, ...] = ()


@dataclass(frozen=True)
class Written:
    ids: tuple[str, ...]
    outcome: AddOutcome
    check: CheckResult
    committed: Committed | None = None
    about: str | None = None


@dataclass(frozen=True)
class ThreadList:
    items: tuple[Thread, ...]
    titles: Mapping[str, str]
    read: Read


@dataclass(frozen=True)
class ThreadShown:
    thread: Thread
    about: Level1
    read: Read


@dataclass(frozen=True)
class ThreadsWaiting:
    for_agent: tuple[Thread, ...]
    for_author: tuple[Thread, ...]
    titles: Mapping[str, str]
    read: Read
