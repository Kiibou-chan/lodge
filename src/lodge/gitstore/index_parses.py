"""Immutable parse units keyed by path and blob ID."""

import marshal
import sqlite3
from collections.abc import Collection, Mapping

from lodge.app import FileKey
from lodge.core import (
    CORE_CLASSES,
    Area,
    Decision,
    Parsed,
    Problem,
    SpecEntry,
    Thread,
    from_plain,
    to_plain,
)


def find_parses(db: sqlite3.Connection, keys: Collection[FileKey]) -> dict[FileKey, Parsed | None]:
    found: dict[FileKey, Parsed | None] = {}
    for key in keys:
        row = db.execute("SELECT value FROM parses WHERE path=? AND blob=?", key).fetchone()
        if row is not None:
            try:
                value = from_plain(marshal.loads(row[0]), CORE_CLASSES)
                if value is None or isinstance(value, (Area, Decision, Problem, SpecEntry, Thread)):
                    found[key] = value
            except (ValueError, TypeError, EOFError, RecursionError):
                pass
    return found


def insert_parses(db: sqlite3.Connection, parsed: Mapping[FileKey, Parsed | None]) -> None:
    for (path, blob), value in parsed.items():
        db.execute(
            "INSERT OR IGNORE INTO parses(path,blob,value) VALUES(?,?,?)",
            (path, blob, marshal.dumps(to_plain(value))),  # type: ignore[arg-type]
        )
