"""The disposable SQLite index, with one file for each source and dependency build."""

import os
import sqlite3
import sys
from collections.abc import Collection, Iterator, Mapping
from contextlib import contextmanager, suppress
from hashlib import sha1
from pathlib import Path
from typing import IO

import yaml

from lodge.app import FileKey, Index
from lodge.core import CoreSettings, Parsed, to_plain
from lodge.gitstore.git import run
from lodge.gitstore.index_parses import find_parses, insert_parses
from lodge.gitstore.index_space import exclusive, open_lock, prune, share

SCHEMA = 1


def build_digest(source: Path | None = None) -> str:
    source = source or Path(__file__).resolve().parents[1]
    digest = sha1()
    for value in (
        SCHEMA,
        sys.version,
        yaml.__version__,
        yaml.__with_libyaml__,
        sqlite3.sqlite_version,
    ):
        digest.update(repr(value).encode() + b"\0")
    for path in sorted(source.rglob("*")):
        if path.is_file() and path.suffix in {".py", ".md"}:
            digest.update(path.relative_to(source).as_posix().encode() + b"\0")
            raw = path.read_bytes()
            digest.update(str(len(raw)).encode() + b"\0" + raw)
    return digest.hexdigest()[:16]


def settings_key(settings: CoreSettings) -> str:
    return sha1(repr(to_plain(settings)).encode()).hexdigest()


def project_index(root: Path, settings: CoreSettings) -> Index | None:
    common = Path(run(["rev-parse", "--path-format=absolute", "--git-common-dir"], root))
    return open_index(common, settings_key(settings))


@contextmanager
def transaction(db: sqlite3.Connection, *, write: bool = False) -> Iterator[None]:
    try:
        db.execute("BEGIN IMMEDIATE" if write else "BEGIN")
        yield
        db.execute("COMMIT")
    finally:
        if db.in_transaction:
            db.execute("ROLLBACK")


def _connect(path: Path, readonly: bool) -> sqlite3.Connection:
    db = sqlite3.connect(
        path.as_uri() + ("?mode=ro" if readonly else "?mode=rwc"),
        uri=True,
        isolation_level=None,
        timeout=0.2,
    )
    try:
        db.execute("PRAGMA busy_timeout=200")
        mode = db.execute(
            "PRAGMA journal_mode" if readonly else "PRAGMA journal_mode=WAL"
        ).fetchone()
        if mode[0] != "wal":
            raise sqlite3.OperationalError("index requires WAL")
        db.execute("PRAGMA synchronous=NORMAL")
        db.execute("PRAGMA secure_delete=OFF")
        db.execute("PRAGMA journal_size_limit=16777216")
        with transaction(db):
            exists = db.execute("SELECT 1 FROM sqlite_master WHERE name='meta'").fetchone()
            if exists:
                db.execute("SELECT epoch,kept FROM meta").fetchone()
        if not exists:
            with transaction(db, write=True):
                db.execute(
                    "CREATE TABLE IF NOT EXISTS meta(epoch INTEGER NOT NULL, kept INTEGER NOT NULL)"
                )
                db.execute("INSERT INTO meta SELECT 1,0 WHERE NOT EXISTS (SELECT 1 FROM meta)")
                db.execute(
                    "CREATE TABLE IF NOT EXISTS parses(rowid INTEGER PRIMARY KEY, "
                    "path TEXT NOT NULL, "
                    "blob TEXT NOT NULL, value BLOB NOT NULL, UNIQUE(path,blob))"
                )
        return db
    except BaseException:
        db.close()
        raise


def open_index(common_dir: Path, settings_digest: str) -> Index | None:
    lock: IO[bytes] | None = None
    try:
        folder = common_dir.resolve() / "lodge"
        with suppress(OSError):
            folder.mkdir(exist_ok=True)
        path = folder / f"index-{build_digest()}.sqlite"
        lock = open_lock(path.with_suffix(".lock"))
        readonly = not os.access(folder, os.W_OK) or (
            path.exists() and not os.access(path, os.W_OK)
        )
        if lock is not None:
            prune(folder, path)
        try:
            db = _connect(path, readonly)
        except sqlite3.Error as error:
            corrupt = getattr(error, "sqlite_errorcode", None) in {
                sqlite3.SQLITE_CORRUPT,
                sqlite3.SQLITE_NOTADB,
            }
            if not corrupt or readonly or not exclusive(lock):
                raise
            for suffix in ("", "-wal", "-shm"):
                Path(str(path) + suffix).unlink(missing_ok=True)
            db = _connect(path, False)
            share(lock)
        return IndexDB(db, lock, settings_digest)
    except (OSError, sqlite3.Error):
        if lock is not None:
            lock.close()
        return None


class IndexDB:
    def __init__(self, db: sqlite3.Connection, lock: IO[bytes] | None, settings: str) -> None:
        self.db = db
        self.lock = lock
        self.settings_digest = settings

    def parses(self, keys: Collection[FileKey]) -> dict[FileKey, Parsed | None]:
        try:
            with transaction(self.db):
                return find_parses(self.db, keys)
        except sqlite3.Error:
            return {}

    def keep_parses(self, parsed: Mapping[FileKey, Parsed | None]) -> None:
        if not parsed:
            return
        try:
            with transaction(self.db, write=True):
                insert_parses(self.db, parsed)
        except (sqlite3.Error, ValueError, TypeError, RecursionError):
            pass

    def epoch(self) -> int:
        try:
            with transaction(self.db):
                return int(self.db.execute("SELECT epoch FROM meta").fetchone()[0])
        except (sqlite3.Error, TypeError, ValueError):
            return 0

    def close(self) -> None:
        try:
            self.db.close()
        finally:
            if self.lock is not None:
                self.lock.close()
                self.lock = None

    def __del__(self) -> None:
        self.close()
