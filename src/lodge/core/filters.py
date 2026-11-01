"""Filters shared by in-memory and indexed search."""

from dataclasses import dataclass
from typing import Literal

from lodge.core.model import Scope


@dataclass(frozen=True)
class Filters:
    """A decision's areas are those of the entries it changes; an entry has no scope."""

    kind: Literal["decision", "spec"] | None = None
    scope: Scope | None = None
    status: Literal["current", "replaced", "retired", "any"] = "current"
    area: str | None = None
    decided_by: str | None = None
