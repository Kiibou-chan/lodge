"""An unavailable index is a miss; it cannot change or fail a read."""

import fcntl
import os
import sqlite3
import time
from pathlib import Path

import pytest

from gitstore.index_helpers import KEY, filename, opened, shared_elsewhere
from lodge.core import Problem
from lodge.gitstore import index_db, open_index
from lodge.gitstore.index_db import IndexDB


def test_read_only_folder_reads_or_skips(tmp_path: Path) -> None:
    if os.geteuid() == 0:
        pytest.skip("root bypasses permission bits")
    index = opened(tmp_path)
    index.keep_parses({KEY: None})
    index.close()
    path = filename(tmp_path)
    before = path.read_bytes()
    path.chmod(0o400)
    path.parent.chmod(0o500)
    try:
        again = open_index(tmp_path)
        if again is not None:
            assert again.parses([KEY]) == {KEY: None}
            again.keep_parses({("other", "blob"): None})
            assert again.parses([("other", "blob")]) == {}
            assert isinstance(again, IndexDB)
            again.close()
        assert path.read_bytes() == before
    finally:
        path.parent.chmod(0o700)
        path.chmod(0o600)


def test_read_only_and_missing_returns_none(tmp_path: Path) -> None:
    if os.geteuid() == 0:
        pytest.skip("root bypasses permission bits")
    tmp_path.chmod(0o500)
    try:
        assert open_index(tmp_path) is None
        assert not (tmp_path / "lodge").exists()
    finally:
        tmp_path.chmod(0o700)


def test_locked_at_open_does_not_delete(tmp_path: Path) -> None:
    index = opened(tmp_path)
    index.keep_parses({KEY: None})
    index.db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    before = filename(tmp_path).read_bytes()
    index.db.execute("BEGIN IMMEDIATE")
    start = time.monotonic()
    other = open_index(tmp_path)
    assert time.monotonic() - start < 1
    assert isinstance(other, IndexDB)
    other.keep_parses({("locked", "blob"): None})
    assert other.parses([("locked", "blob")]) == {}
    assert filename(tmp_path).read_bytes() == before
    index.db.execute("ROLLBACK")
    if isinstance(other, IndexDB):
        other.close()
    assert index.parses([KEY]) == {KEY: None}
    index.close()


def test_locked_write_is_skipped(tmp_path: Path) -> None:
    first, second = opened(tmp_path), opened(tmp_path)
    first.db.execute("BEGIN IMMEDIATE")
    second.keep_parses({KEY: None})
    assert not second.db.in_transaction
    first.db.execute("COMMIT")
    assert second.parses([KEY]) == {}
    first.close()
    second.close()


def garbage(folder: Path) -> Path:
    index = opened(folder)
    index.close()
    path = filename(folder)
    path.write_bytes(b"garbage")
    return path


def test_corrupt_file_is_rebuilt(tmp_path: Path) -> None:
    path = garbage(tmp_path)
    index = opened(tmp_path)
    assert path.read_bytes() != b"garbage"
    index.keep_parses({KEY: None})
    assert index.parses([KEY]) == {KEY: None}
    index.close()


def test_corrupt_file_held_by_another_reader_is_not_deleted(tmp_path: Path) -> None:
    path = garbage(tmp_path)
    with shared_elsewhere(path.with_suffix(".lock")):
        assert open_index(tmp_path) is None
        assert path.read_bytes() == b"garbage"


def test_corrupt_file_read_only_returns_none(tmp_path: Path) -> None:
    if os.geteuid() == 0:
        pytest.skip("root bypasses permission bits")
    path = garbage(tmp_path)
    path.chmod(0o400)
    try:
        assert open_index(tmp_path) is None
        assert path.read_bytes() == b"garbage"
    finally:
        path.chmod(0o600)


class Interrupted(sqlite3.Connection):
    """Raise once after the chosen statement actually executes, including COMMIT's boundary."""

    after = 0
    count = 0

    def execute(self, sql: str, parameters: object = (), /) -> sqlite3.Cursor:
        # A failed COMMIT must be injected before it commits, like a SQLite commit error.
        self.count += 1
        fail = self.after == self.count
        if fail and sql == "COMMIT":
            raise sqlite3.OperationalError("injected commit failure")
        cursor = super().execute(sql, parameters)  # type: ignore[arg-type]
        if fail:
            raise sqlite3.OperationalError("injected statement failure")
        return cursor


@pytest.mark.parametrize("after", range(1, 5))
def test_keep_parses_interrupted_at_each_statement(tmp_path: Path, after: int) -> None:
    initial = opened(tmp_path)
    initial.keep_parses({KEY: None})
    initial.close()
    db = sqlite3.connect(filename(tmp_path), isolation_level=None, factory=Interrupted)
    index = IndexDB(db, None)
    db.after = after
    values = {("one", "blob"): Problem("one", 1, "bad"), ("two", "blob"): None}
    index.keep_parses(values)
    assert not db.in_transaction
    assert index.parses([KEY, *values]) == {KEY: None}
    index.close()


def test_concurrent_keep_parses(tmp_path: Path) -> None:
    first, second = opened(tmp_path), opened(tmp_path)
    values = {KEY: Problem("first", 1, "bad"), ("second", "blob"): None}
    attempted: list[bool] = []

    def interleave(sql: str) -> None:
        if sql.startswith("INSERT") and not attempted:
            attempted.append(True)
            second.keep_parses({KEY: values[KEY], ("third", "blob"): None})

    first.db.set_trace_callback(interleave)
    first.keep_parses(values)
    assert attempted and first.parses(list(values)) == values
    assert second.parses([("third", "blob")]) == {}
    second.keep_parses({KEY: values[KEY], ("third", "blob"): None})
    assert first.parses([*values, ("third", "blob")]) == {**values, ("third", "blob"): None}
    first.close()
    second.close()


def test_parse_units_are_immutable(tmp_path: Path) -> None:
    index = opened(tmp_path)
    index.keep_parses({KEY: None})
    rowid = index.db.execute("SELECT rowid FROM parses").fetchone()[0]
    index.keep_parses({KEY: Problem("different", 1, "bad")})
    assert index.parses([KEY]) == {KEY: None}
    assert index.db.execute("SELECT rowid FROM parses").fetchone()[0] == rowid
    index.close()


def test_non_corruption_open_error_never_deletes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    index = opened(tmp_path)
    index.close()
    path = filename(tmp_path)
    before = path.read_bytes()

    def fail(*args: object, **kwargs: object) -> sqlite3.Connection:
        raise sqlite3.OperationalError("I/O error")

    monkeypatch.setattr(sqlite3, "connect", fail)
    assert open_index(tmp_path) is None
    assert path.read_bytes() == before


def test_rebuilt_file_releases_exclusive_upgrade(tmp_path: Path) -> None:
    path = garbage(tmp_path)
    index = opened(tmp_path)
    # A recovered index must admit another reader before this reader closes.
    with path.with_suffix(".lock").open("rb") as probe:
        fcntl.flock(probe, fcntl.LOCK_SH | fcntl.LOCK_NB)
    index.close()


def test_missing_own_lock_does_not_prune(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    index = opened(tmp_path)
    index.close()
    old = filename(tmp_path).with_name("index-" + "a" * 16 + ".sqlite")
    old.write_bytes(b"old build")
    lock = old.with_suffix(".lock")
    lock.write_bytes(b"")
    os.utime(lock, (time.time() - 8 * 86400,) * 2)
    monkeypatch.setattr(index_db, "open_lock", lambda path: None)
    again = opened(tmp_path)
    assert old.exists()
    again.close()
