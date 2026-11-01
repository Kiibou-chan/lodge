"""Transactional state storage and bounded first-sighting markers."""

import json
import sqlite3
from collections.abc import Collection, Mapping
from contextlib import AbstractContextManager
from hashlib import sha1

from lodge.app import (
    FileKey,
    Listed,
    Read,
    Row,
    StateFacts,
    StoredState,
    ThreadList,
    ThreadShown,
    ThreadsWaiting,
)
from lodge.core import CORE_CLASSES, Parsed, from_plain, to_plain
from lodge.gitstore.index_parses import insert_parses
from lodge.gitstore.index_space import prepare_keep
from lodge.gitstore.index_transactions import transaction

KEPT_STATES = 4
_ALPHABET = "0123456789abcdefghjkmnpqrstvwxyz"
_CLASSES = {
    **CORE_CLASSES,
    **{
        c.__name__: c
        for c in (
            Row,
            StateFacts,
            StoredState,
            Listed,
            Read,
            ThreadList,
            ThreadShown,
            ThreadsWaiting,
        )
    },
}


def encode(value: object) -> str:
    return json.dumps(to_plain(value), ensure_ascii=True, separators=(",", ":"))


def decode(raw: str) -> object:
    return from_plain(json.loads(raw), _CLASSES)


def buckets(rows: Mapping[str, Row]) -> dict[str, str]:
    grouped: dict[str, dict[str, Row]] = {a + b: {} for a in _ALPHABET for b in _ALPHABET}
    for ident, row in rows.items():
        grouped[ident[-2:]][ident] = row
    return {name: encode(value) for name, value in grouped.items()}


def insert_facts(db: sqlite3.Connection, facts: Mapping[str, StateFacts]) -> None:
    written = 0
    for ident, value in facts.items():
        written += db.execute(
            "INSERT OR IGNORE INTO facts VALUES(?,?)", (ident, encode(value))
        ).rowcount
    db.execute("UPDATE meta SET written=written+?", (written,))


class IndexStates:
    db: sqlite3.Connection

    def reading(self) -> AbstractContextManager[None]:
        return transaction(self.db)

    def _value(self, table: str, where: str, params: tuple[str, ...]) -> object | None:
        try:
            with transaction(self.db):
                row = self.db.execute(f"SELECT value FROM {table} WHERE {where}", params).fetchone()
                return decode(row[0]) if row is not None else None
        except Exception:
            return None

    def state(self, key: str) -> StoredState | None:
        try:
            with transaction(self.db):
                value = self._value("states", "key=?", (key,))
                if not isinstance(value, StoredState) or value.key != key:
                    return None
                counts = tuple(
                    self.db.execute(f"SELECT count(*) FROM {table} WHERE key=?", (key,)).fetchone()[
                        0
                    ]
                    for table in ("buckets JOIN bucket_blobs USING(hash)", "answers", "citers")
                )
                return value if counts == value.promised else None
        except Exception:
            return None

    def rows(self, key: str, ids: Collection[str]) -> dict[str, Row] | None:
        try:
            with transaction(self.db):
                found: dict[str, Row] = {}
                for name in {i[-2:] for i in ids}:
                    value = self._value(
                        "buckets JOIN bucket_blobs USING(hash)", "key=? AND name=?", (key, name)
                    )
                    if not isinstance(value, dict) or not all(
                        isinstance(i, str) and isinstance(r, Row) and i[-2:] == name
                        for i, r in value.items()
                    ):
                        return None
                    found.update(value)
                return {i: found[i] for i in ids if i in found}
        except Exception:
            return None

    def all_rows(self, key: str) -> dict[str, Row]:
        try:
            with transaction(self.db):
                state = self.state(key)
                if state is None:
                    return {}
                rows: dict[str, Row] = {}
                for name, raw in self.db.execute(
                    "SELECT name,value FROM buckets JOIN bucket_blobs USING(hash) WHERE key=?",
                    (key,),
                ):
                    value = decode(raw)
                    if not isinstance(value, dict) or not all(
                        isinstance(i, str) and isinstance(r, Row) and i[-2:] == name
                        for i, r in value.items()
                    ):
                        return {}
                    rows.update(value)
                return rows
        except Exception:
            return {}

    def answer(self, key: str, name: str) -> object | None:
        return self._value("answers", "key=? AND name=?", (key, name))

    def citing(self, key: str, code: str, limit: int | None) -> tuple[str, ...] | None:
        value = self._value("citers", "key=? AND name=?", (key, code.lower()))
        if isinstance(value, tuple) and all(isinstance(i, str) for i in value):
            return value if limit is None else value[:limit]
        return None

    def facts(self, ident: str) -> StateFacts | None:
        value = self._value("facts", "ident=?", (ident,))
        return value if isinstance(value, StateFacts) else None

    def seen(self, key: str) -> bool:
        try:
            with transaction(self.db):
                return (
                    self.db.execute("SELECT 1 FROM seen WHERE key=?", (key,)).fetchone() is not None
                )
        except Exception:
            return False

    def mark_seen(
        self,
        key: str,
        parses: Mapping[FileKey, Parsed | None],
        facts: Mapping[str, StateFacts],
        *,
        files: int,
        used: Mapping[FileKey, Parsed | None] | None = None,
        epoch: int | None = None,
    ) -> None:
        try:
            with transaction(self.db, write=True):
                prepare_keep(self.db, files)
                changed = self.db.execute("SELECT epoch FROM meta").fetchone()[0] != epoch
                insert_parses(self.db, used if changed and used is not None else parses)
                insert_facts(self.db, facts)
                self.db.execute(
                    "INSERT OR REPLACE INTO seen SELECT ?,coalesce(max(at),0)+1 FROM seen", (key,)
                )
                self.db.execute(
                    "DELETE FROM seen WHERE key IN (SELECT key FROM seen "
                    "ORDER BY at DESC LIMIT -1 OFFSET 64)"
                )
        except Exception:
            pass

    def keep_state(
        self,
        state: StoredState,
        rows: Mapping[str, Row],
        answers: Mapping[str, object],
        citing: Mapping[str, tuple[str, ...]],
        facts: Mapping[str, StateFacts],
        parses: Mapping[FileKey, Parsed | None],
        misses: Collection[FileKey],
        epoch: int,
        *,
        files: int,
    ) -> None:
        try:
            encoded = buckets(rows)
            hashes = {raw: sha1(raw.encode()).hexdigest() for raw in set(encoded.values())}
            with transaction(self.db, write=True):
                prepare_keep(self.db, files)
                changed = self.db.execute("SELECT epoch FROM meta").fetchone()[0] != epoch
                insert_parses(self.db, parses if changed else {k: parses[k] for k in misses})
                insert_facts(self.db, facts)
                at = self.db.execute("SELECT coalesce(max(at),0)+1 FROM states").fetchone()[0]
                self._remove(state.key)
                evicted = self.db.execute(
                    "SELECT key FROM states ORDER BY at DESC LIMIT -1 OFFSET ?", (KEPT_STATES - 1,)
                ).fetchall()
                for (key,) in evicted:
                    self._remove(key)
                for raw, digest in hashes.items():
                    self.db.execute("INSERT OR IGNORE INTO bucket_blobs VALUES(?,?)", (digest, raw))
                for name, raw in encoded.items():
                    self.db.execute(
                        "INSERT INTO buckets VALUES(?,?,?)", (state.key, name, hashes[raw])
                    )
                self.db.execute(
                    "DELETE FROM bucket_blobs WHERE hash NOT IN (SELECT hash FROM buckets)"
                )
                for table, values in (("answers", answers), ("citers", citing)):
                    for name, value in values.items():
                        self.db.execute(
                            f"INSERT INTO {table} VALUES(?,?,?)", (state.key, name, encode(value))
                        )
                self.db.execute("UPDATE meta SET kept=1")
                self.db.execute("INSERT INTO states VALUES(?,?,?)", (state.key, at, encode(state)))
        except Exception:
            pass

    def _remove(self, key: str) -> None:
        for table in ("states", "buckets", "answers", "citers"):
            self.db.execute(f"DELETE FROM {table} WHERE key=?", (key,))
