"""The record kinds: decisions, specification entries, areas, and the problems found in files."""

from dataclasses import dataclass
from enum import StrEnum


class Scope(StrEnum):
    PRODUCT = "product"
    PROCESS = "process"


class Action(StrEnum):
    CREATE = "create"
    EDIT = "edit"
    RETIRE = "retire"


@dataclass(frozen=True)
class Quote:
    text: str
    where: str
    when: str


@dataclass(frozen=True)
class Change:
    entry: str
    action: Action


@dataclass(frozen=True)
class NumberHandle:
    value: str
    handle: str


@dataclass(frozen=True)
class Imported:
    file: str
    heading: str


@dataclass(frozen=True)
class Decision:
    id: str
    title: str
    scope: Scope
    decided_by: str
    date: str
    statement: str
    reasoning: str = ""
    code: str | None = None
    changes: tuple[Change, ...] = ()
    replaces: tuple[str, ...] = ()
    narrows: tuple[str, ...] = ()
    confirms: tuple[str, ...] = ()
    work_item: str | None = None
    quote: Quote | None = None
    numbers: tuple[NumberHandle, ...] = ()
    attachments: tuple[str, ...] = ()
    imported_from: Imported | None = None


@dataclass(frozen=True)
class SpecEntry:
    id: str
    area: str
    title: str
    statement: str
    code: str | None = None
    imported_from: Imported | None = None


@dataclass(frozen=True)
class Area:
    name: str
    title: str
    intro: str
    order: tuple[str, ...]


Record = Decision | SpecEntry


@dataclass(frozen=True)
class Problem:
    path: str
    check: int
    message: str
    line: int | None = None
