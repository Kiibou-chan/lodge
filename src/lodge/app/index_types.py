"""Leaf value types shared by the index port and its adapter."""

from collections.abc import Mapping
from dataclasses import dataclass

from lodge.core import Decision, Level1, Problem, Quote, SpecEntry

FileKey = tuple[str, str]


@dataclass(frozen=True)
class Row:
    key: FileKey
    status: str
    decided_by: str | None
    date: str | None
    scope: str | None
    area: str | None
    flags: tuple[str, ...]
    quote: Quote | None
    links: tuple[tuple[str, str, str], ...]
    changed_by: tuple[str, ...]
    areas: frozenset[str]


@dataclass(frozen=True)
class StateFacts:
    status: Mapping[str, str]


@dataclass(frozen=True)
class StoredState:
    key: str
    current: str
    published: str
    promised: tuple[int, int, int]
    valid_from: str | None
    valid_until: str | None
    codes: Mapping[str, tuple[str, ...]]
    citers: Mapping[str, int]
    unrecorded: tuple[Problem, ...]
    threads: tuple[str, ...]


def level1_of(row: Row, record: Decision | SpecEntry) -> Level1:
    return Level1(
        record.id,
        "decision" if isinstance(record, Decision) else "spec",
        record.code,
        record.title,
        record.statement,
        row.status,
        row.decided_by,
        row.date,
        row.scope,
        row.area,
        row.flags,
        row.quote,
    )
