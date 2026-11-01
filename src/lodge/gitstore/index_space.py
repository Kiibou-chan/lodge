"""Space bounds, in-place clears, and locks protecting build files."""

import os
import sqlite3
import time
from contextlib import suppress
from pathlib import Path
from typing import IO

try:
    import fcntl
except ImportError:
    fcntl = None  # type: ignore[assignment]

INDEX_BYTES_PER_FILE = 1_500
MIN_FILE_CAP = 16 * 1024 * 1024


def open_lock(path: Path) -> IO[bytes] | None:
    lock: IO[bytes] | None = None
    try:
        try:
            lock = path.open("a+b")
        except OSError:
            lock = path.open("rb")
        share(lock)
        with suppress(OSError):
            os.utime(path, None)
        return lock
    except OSError:
        if lock is not None:
            lock.close()
        return None


def share(lock: IO[bytes] | None) -> None:
    if fcntl is not None and lock is not None:
        fcntl.flock(lock, fcntl.LOCK_SH)


def exclusive(lock: IO[bytes] | None) -> bool:
    if fcntl is None or lock is None:
        return False
    try:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return True
    except OSError:
        return False


def prune(folder: Path, current: Path) -> None:
    """Delete old builds only while their persistent lock is exclusively held."""
    if fcntl is None:
        return
    builds: list[tuple[float, Path]] = []
    for path in {*folder.glob("index-*.sqlite"), current}:
        try:
            age = path.with_suffix(".lock").stat().st_mtime
        except FileNotFoundError:
            age = 0.0
        except OSError:
            continue
        builds.append((age, path))
    for number, (age, path) in enumerate(sorted(builds, reverse=True)):
        if path == current or (number < 4 and time.time() - age < 7 * 86400):
            continue
        try:
            with path.with_suffix(".lock").open("a+b") as lock:
                if exclusive(lock):
                    for suffix in ("", "-wal", "-shm"):
                        Path(str(path) + suffix).unlink(missing_ok=True)
        except OSError:
            continue


def used_bytes(db: sqlite3.Connection) -> int:
    return int(
        (
            db.execute("PRAGMA page_count").fetchone()[0]
            - db.execute("PRAGMA freelist_count").fetchone()[0]
        )
        * int(db.execute("PRAGMA page_size").fetchone()[0])
    )


def clear(db: sqlite3.Connection) -> None:
    """Clear inside the caller's write transaction, preserving WAL snapshots and file identity."""
    tables = db.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
    for (name,) in tables:
        if name != "meta" and not name.startswith("sqlite_"):
            escaped = name.replace('"', '""')
            db.execute(f'DELETE FROM "{escaped}"')
    db.execute("UPDATE meta SET epoch=epoch+1, kept=0, written=0")


def prepare_keep(db: sqlite3.Connection, files: int) -> None:
    """Check used pages while holding BEGIN IMMEDIATE, before writing a state's units."""
    INDEX_FILE_CAP = max(MIN_FILE_CAP, INDEX_BYTES_PER_FILE * files)
    over = used_bytes(db) > INDEX_FILE_CAP
    kept, written = db.execute("SELECT kept,written FROM meta").fetchone()
    if over and (kept or written >= files):
        clear(db)
