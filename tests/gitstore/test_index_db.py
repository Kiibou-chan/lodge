"""Build naming, lock lifetime, transactions, and space bounds of the disposable index."""

import fcntl
import os
import sqlite3
import sys
import time
from pathlib import Path
from typing import cast

import pytest
import yaml

from gitstore.index_helpers import KEY, filename, opened, shared_elsewhere
from lodge.core import Problem
from lodge.gitstore import index_db, index_space, open_index


def test_creates_folder_and_file_named_by_digest(tmp_path: Path) -> None:
    index = opened(tmp_path)
    assert filename(tmp_path).is_file() and len(index_db.build_digest()) == 16
    index.close()


def test_digest_changes_with_source_bytes(tmp_path: Path) -> None:
    source = tmp_path / "a.py"
    source.write_text("first")
    before = source.stat()
    first = index_db.build_digest(tmp_path)
    source.write_text("other")
    os.utime(source, ns=(before.st_atime_ns, before.st_mtime_ns))
    assert index_db.build_digest(tmp_path) != first
    source.rename(tmp_path / "b.py")
    assert index_db.build_digest(tmp_path) != first


@pytest.mark.parametrize(
    "module,name,value",
    [
        (sys, "version", "new-python"),
        (yaml, "__version__", "new-yaml"),
        (yaml, "__with_libyaml__", False),
        (sqlite3, "sqlite_version", "new-sqlite"),
    ],
)
def test_digest_names_python_yaml_libyaml_sqlite(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    module: object,
    name: str,
    value: object,
) -> None:
    before = index_db.build_digest(tmp_path)
    target = module
    monkeypatch.setattr(
        target, name, value if name != "__with_libyaml__" else not yaml.__with_libyaml__
    )
    assert index_db.build_digest(tmp_path) != before


def test_two_builds_keep_their_files(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    for digest in ("a" * 16, "b" * 16):
        monkeypatch.setattr(index_db, "build_digest", lambda digest=digest: digest)
        index = opened(tmp_path)
        index.keep_parses({KEY: Problem(digest, 1, "bad")}, files=1)
        index.close()
    for digest in ("a" * 16, "b" * 16):
        monkeypatch.setattr(index_db, "build_digest", lambda digest=digest: digest)
        index = opened(tmp_path)
        assert index.parses([KEY]) == {KEY: Problem(digest, 1, "bad")}
        index.close()


def old_file(folder: Path, digest: str, days: int) -> Path:
    path = folder / f"index-{digest}.sqlite"
    for suffix in ("", "-wal", "-shm", ".lock"):
        target = path.with_suffix(".lock") if suffix == ".lock" else Path(str(path) + suffix)
        target.write_bytes(b"old")
        os.utime(target, (time.time() - days * 86400,) * 2)
    return path


def test_old_build_deleted_after_seven_days_under_the_lock(tmp_path: Path) -> None:
    index = opened(tmp_path)
    folder = filename(tmp_path).parent
    young, old, held = [old_file(folder, s * 16, d) for s, d in (("a", 6), ("b", 8), ("c", 8))]
    with shared_elsewhere(held.with_suffix(".lock")):
        index_space.prune(folder, filename(tmp_path))
        assert held.exists() and young.exists()
        assert not old.exists() and not Path(str(old) + "-wal").exists()
        assert not Path(str(old) + "-shm").exists() and old.with_suffix(".lock").exists()
    index.close()


def test_no_fcntl_deletes_nothing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    index = opened(tmp_path)
    old = old_file(filename(tmp_path).parent, "a" * 16, 8)
    monkeypatch.setattr(index_space, "fcntl", None)
    index_space.prune(old.parent, filename(tmp_path))
    assert old.exists()
    index.close()


def test_lock_taken_before_connect_and_touched(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    connect = sqlite3.connect
    seen: list[bool] = []

    def checked(*args: object, **kw: object) -> sqlite3.Connection:
        path = filename(tmp_path).with_suffix(".lock")
        with path.open("rb") as probe, pytest.raises(BlockingIOError):
            fcntl.flock(probe, fcntl.LOCK_EX | fcntl.LOCK_NB)
        assert abs(path.stat().st_mtime - time.time()) < 2
        seen.append(True)
        return cast(sqlite3.Connection, connect(*args, **kw))  # type: ignore[call-overload]

    monkeypatch.setattr(sqlite3, "connect", checked)
    index = opened(tmp_path)
    assert seen
    index.close()
    with filename(tmp_path).with_suffix(".lock").open("rb") as probe:
        fcntl.flock(probe, fcntl.LOCK_EX | fcntl.LOCK_NB)


def test_read_only_lock_file_is_opened(tmp_path: Path) -> None:
    index = opened(tmp_path)
    index.close()
    lock = filename(tmp_path).with_suffix(".lock")
    lock.chmod(0o400)
    again = opened(tmp_path)
    assert again.lock is not None
    again.close()


def test_fifth_most_recent_build_is_deleted(tmp_path: Path) -> None:
    index = opened(tmp_path)
    files = [old_file(filename(tmp_path).parent, str(n) * 16, 0) for n in range(5)]
    for n, path in enumerate(files):
        os.utime(path.with_suffix(".lock"), (time.time() - 10 + n,) * 2)
    index_space.prune(files[0].parent, filename(tmp_path))
    assert not files[0].exists() and not files[1].exists()
    assert all(p.exists() for p in files[2:])
    index.close()


def corrupt(folder: Path) -> Path:
    index = opened(folder)
    index.close()
    path = filename(folder)
    path.write_bytes(b"not a database")
    return path


def test_refused_upgrade_returns_none_and_holds_no_lock(tmp_path: Path) -> None:
    path = corrupt(tmp_path)
    with shared_elsewhere(path.with_suffix(".lock")):
        assert open_index(tmp_path) is None
        assert path.read_bytes() == b"not a database"
    with path.with_suffix(".lock").open("rb") as probe:
        fcntl.flock(probe, fcntl.LOCK_EX | fcntl.LOCK_NB)


def test_corrupt_without_fcntl_returns_none(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    path = corrupt(tmp_path)
    monkeypatch.setattr(index_space, "fcntl", None)
    assert open_index(tmp_path) is None
    assert path.read_bytes() == b"not a database"


def populate(index: index_db.IndexDB) -> None:
    index.db.execute("INSERT INTO parses(path,blob,value) VALUES('large','x',zeroblob(21000000))")
    index.db.execute("UPDATE meta SET kept=1")


def test_secure_delete_off(tmp_path: Path) -> None:
    index = opened(tmp_path)
    assert index.db.execute("PRAGMA secure_delete").fetchone()[0] == 0
    with sqlite3.connect(":memory:") as probe:
        default = probe.execute("PRAGMA secure_delete").fetchone()[0]
    if default != 1:
        index.close()
        pytest.skip("SQLite does not default secure_delete to 1; pragma assertions passed")
    index.close()


def test_clear_wal_bounded(tmp_path: Path) -> None:
    index = opened(tmp_path)
    assert index.db.execute("PRAGMA journal_size_limit").fetchone()[0] == 16777216
    populate(index)
    index.db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    index.db.execute("BEGIN IMMEDIATE")
    index_space.clear(index.db)
    index.db.execute("COMMIT")
    assert 0 < Path(str(filename(tmp_path)) + "-wal").stat().st_size <= 16777216
    index.db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    index.close()


def test_two_clears_in_a_row_raise_the_epoch(tmp_path: Path) -> None:
    index = opened(tmp_path)
    assert index.epoch() == 1
    value = Problem("x", 1, "bad")
    index.keep_parses({KEY: value}, files=1)
    hits = index.parses([KEY])
    for _ in range(2):
        index.db.execute("BEGIN IMMEDIATE")
        index_space.clear(index.db)
        index.db.execute("COMMIT")
    assert index.epoch() == 3 and index.parses([KEY]) == {}
    index.keep_parses(hits, files=len(hits))
    assert index.parses([KEY]) == hits
    index.close()


def test_connection_is_explicit_and_wal(tmp_path: Path) -> None:
    index = opened(tmp_path)
    assert index.db.isolation_level is None
    assert index.db.execute("PRAGMA journal_mode").fetchone()[0] == "wal"
    statements: list[tuple[str, bool]] = []
    index.db.set_trace_callback(lambda sql: statements.append((sql, index.db.in_transaction)))
    index.keep_parses({KEY: None}, files=1)
    assert index.parses([KEY]) == {KEY: None} and index.epoch() == 1
    selects = [active for sql, active in statements if sql.startswith("SELECT")]
    assert selects and all(selects)
    assert any(sql == "BEGIN IMMEDIATE" for sql, _ in statements)
    assert any(sql == "BEGIN" for sql, _ in statements)
    assert not index.db.in_transaction
    index.close()


def test_cap_counts_used_pages(tmp_path: Path) -> None:
    index = opened(tmp_path)
    populate(index)
    index.db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    size = filename(tmp_path).stat().st_size
    assert index_space.used_bytes(index.db) > index_space.MIN_FILE_CAP
    index.db.execute("BEGIN IMMEDIATE")
    index_space.prepare_keep(index.db, 1)
    index.db.execute("COMMIT")
    index.db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    assert index_space.used_bytes(index.db) < index_space.MIN_FILE_CAP
    assert filename(tmp_path).stat().st_size == size and index.epoch() == 2
    index.close()


def test_clear_keeps_a_readers_snapshot(tmp_path: Path) -> None:
    reader, writer = opened(tmp_path), opened(tmp_path)
    reader.keep_parses({KEY: None}, files=1)
    reader.db.execute("BEGIN")
    old = reader.db.execute("SELECT value FROM parses").fetchall()
    writer.db.execute("BEGIN IMMEDIATE")
    index_space.clear(writer.db)
    writer.db.execute("COMMIT")
    assert reader.db.execute("SELECT value FROM parses").fetchall() == old
    assert reader.db.execute("SELECT epoch FROM meta").fetchone()[0] == 1
    reader.db.execute("COMMIT")
    assert reader.parses([KEY]) == {} and reader.epoch() == 2
    reader.close()
    writer.close()


def test_two_writers_over_the_cap_clear_once(tmp_path: Path) -> None:
    first, second = opened(tmp_path), opened(tmp_path)
    populate(first)
    for index in (first, second):
        index.db.execute("BEGIN IMMEDIATE")
        index_space.prepare_keep(index.db, 1)
        index.db.execute("COMMIT")
        index.keep_parses({KEY: None}, files=1)
    assert first.epoch() == second.epoch() == 2
    assert first.parses([KEY]) == second.parses([KEY]) == {KEY: None}
    first.close()
    second.close()


def test_new_build_counts_towards_four_files(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    for number in range(5):
        monkeypatch.setattr(index_db, "build_digest", lambda number=number: str(number) * 16)
        index = opened(tmp_path)
        index.close()
        lock = tmp_path / "lodge" / ("index-" + str(number) * 16 + ".lock")
        os.utime(lock, (time.time() - 10 + number,) * 2)
    files = list((tmp_path / "lodge").glob("index-*.sqlite"))
    assert len(files) == 4
    assert not (tmp_path / "lodge" / ("index-" + "0" * 16 + ".sqlite")).exists()
