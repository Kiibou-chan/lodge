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
from lodge.gitstore.index_words import has_words, insert_words

SCAN_FROM = 1_000


def _parse_value(raw: str) -> Parsed | None:
    value = from_plain(json.loads(raw), CORE_CLASSES)
    if value is None or isinstance(value, (Area, Decision, Problem, SpecEntry, Thread)):
        return value
    raise ValueError("cached value is not a parse")


def find_parses(db: sqlite3.Connection, keys: Collection[FileKey]) -> dict[FileKey, Parsed | None]:
    found: dict[FileKey, Parsed | None] = {}
    if len(keys) >= SCAN_FROM and len(keys) * 4 >= (
        db.execute("SELECT max(rowid) FROM parses").fetchone()[0] or 0
    ):
        requested = set(keys)
        try:
            for path, blob, raw in db.execute(
                "SELECT path, blob, value FROM parses ORDER BY rowid"
            ):
                key = (path, blob)
                if key in requested:
                    try:
                        found[key] = _parse_value(raw)
                    except Exception:
                        continue
        except sqlite3.Error:
            pass
        return found
    for key in keys:
        try:
            row = db.execute("SELECT value FROM parses WHERE path=? AND blob=?", key).fetchone()
            if row is not None:
                found[key] = _parse_value(row[0])
        except Exception:
            continue
    return found


def insert_parses(db: sqlite3.Connection, parsed: Mapping[FileKey, Parsed | None]) -> None:
    written = 0
    fts = has_words(db)
    for (path, blob), value in parsed.items():
        try:
            cursor = db.execute(
                "INSERT OR IGNORE INTO parses(path,blob,value) VALUES(?,?,?)",
                (path, blob, json.dumps(to_plain(value), ensure_ascii=True, separators=(",", ":"))),
            )
            written += cursor.rowcount
            if cursor.rowcount and fts:
                assert cursor.lastrowid is not None
                insert_words(db, cursor.lastrowid, value)
        except UnicodeEncodeError:
            continue
    db.execute("UPDATE meta SET written=written+?", (written,))
