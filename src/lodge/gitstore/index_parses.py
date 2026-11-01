"""Immutable parse units keyed by path and blob ID."""

import json
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
        try:
            row = db.execute("SELECT value FROM parses WHERE path=? AND blob=?", key).fetchone()
            if row is not None:
                value = from_plain(json.loads(row[0]), CORE_CLASSES)
                if value is None or isinstance(value, (Area, Decision, Problem, SpecEntry, Thread)):
                    found[key] = value
        except Exception:
            continue
    return found


def insert_parses(db: sqlite3.Connection, parsed: Mapping[FileKey, Parsed | None]) -> None:
    for (path, blob), value in parsed.items():
        try:
            db.execute(
                "INSERT OR IGNORE INTO parses(path,blob,value) VALUES(?,?,?)",
                (path, blob, json.dumps(to_plain(value), ensure_ascii=True, separators=(",", ":"))),
            )
        except UnicodeEncodeError:
            continue
