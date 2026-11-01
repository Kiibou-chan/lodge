"""Small complete state units and callers with explicit tree sizes."""

from collections.abc import Collection, Mapping
from dataclasses import replace

from gitstore.index_helpers import KEY
from lodge.app import FileKey, Index, Row, StateFacts, StoredState
from lodge.core import Parsed, Problem

ROW = Row(
    KEY,
    "current",
    "coordinator",
    "2026-10-28T09:00:00+00:00",
    "product",
    None,
    (),
    None,
    (),
    (),
    frozenset(),
)
FACT = StateFacts({"s-aaaaaa": "current"}, (Problem("x", 1, "synthetic"),))


def stored(key: str = "one", rows: Mapping[str, Row] | None = None) -> StoredState:
    rows = rows or {"s-aaaaaa": ROW}
    return StoredState(
        key, key, "published", (1024, 1, 1), None, None, {"a": tuple(rows)}, {"a": 0}, ()
    )


def keep(
    index: Index,
    key: str = "one",
    rows: Mapping[str, Row] | None = None,
    *,
    parses: Mapping[FileKey, Parsed | None] | None = None,
    facts: Mapping[str, StateFacts] | None = None,
    misses: Collection[FileKey] | None = None,
    epoch: int | None = None,
) -> None:
    rows = {"s-aaaaaa": ROW} if rows is None else rows
    parses = {r.key: None for r in rows.values()} if parses is None else parses
    index.keep_state(
        stored(key, rows),
        rows,
        {"waiting": ((), ())},
        {"a": ()},
        {"published": FACT} if facts is None else facts,
        parses,
        tuple(parses) if misses is None else misses,
        index.epoch() if epoch is None else epoch,
        files=len(rows),
    )


def changed_rows() -> dict[str, Row]:
    return {"s-bbbbbb": replace(ROW, key=("other", "blob"))}
