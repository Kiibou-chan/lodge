"""What the operations return."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from enum import StrEnum

from lodge.core import CheckResult, Feedback, Level1, Level3, Problem


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
