"""Shared buckets, negative lookups, and working sets retained across clears."""

from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import pytest
from indexed_support import app, printed, seed
from support import FIRST, project

from gitstore.index_helpers import opened
from gitstore.state_helpers import ROW, keep
from lodge import core
from lodge.app.state import snapshot_of
from lodge.gitstore import index_space


def test_bucket_blobs_are_shared_and_collected(tmp_path: Path) -> None:
    index = opened(tmp_path)
    keep(index, "one")
    before = index.db.execute("SELECT count(*) FROM bucket_blobs").fetchone()[0]
    assert before == 2  # One populated bucket and one shared empty bucket.
    original = index.db.execute(
        "SELECT hash FROM buckets WHERE key=? AND name=?", ("one", "aa")
    ).fetchone()[0]
    shared = index.db.execute(
        "SELECT hash FROM buckets WHERE key=? AND name=?", ("one", "bb")
    ).fetchone()[0]
    rows = {"s-aaaaaa": replace(ROW, status="retired")}
    for key in ("two", "three", "four"):
        keep(index, key, rows)
    assert index.db.execute("SELECT count(*) FROM bucket_blobs").fetchone()[0] == before + 1
    with index.reading():
        assert index.all_rows("one") == {"s-aaaaaa": ROW}
        assert index.all_rows("two") == rows
    keep(index, "five", rows)
    assert index.state("one") is None
    assert not index.db.execute("SELECT 1 FROM bucket_blobs WHERE hash=?", (original,)).fetchone()
    assert index.db.execute("SELECT 1 FROM bucket_blobs WHERE hash=?", (shared,)).fetchone()
    assert index.db.execute("SELECT count(*) FROM bucket_blobs").fetchone()[0] == before
    assert index.all_rows("two") == rows
    index.close()


def test_bucket_rekeep_and_eviction_are_atomic(tmp_path: Path) -> None:
    index = opened(tmp_path)
    keep(index)
    before = index.db.execute("SELECT * FROM bucket_blobs ORDER BY hash").fetchall()
    statements: list[str] = []
    index.db.set_trace_callback(statements.append)
    keep(index, "two")
    assert index.db.execute("SELECT * FROM bucket_blobs ORDER BY hash").fetchall() == before
    assert not any(s.startswith("UPDATE bucket_blobs") for s in statements)
    index.db.execute(
        "CREATE TRIGGER fail_state BEFORE INSERT ON states "
        "BEGIN SELECT RAISE(ABORT,'injected'); END"
    )
    keep(index, "one", {"s-aaaaaa": replace(ROW, status="retired")})
    assert index.all_rows("one") == {"s-aaaaaa": ROW}
    assert index.db.execute("SELECT * FROM bucket_blobs ORDER BY hash").fetchall() == before
    index.close()


@pytest.mark.parametrize("writer", ["marker", "parses"])
@pytest.mark.parametrize("clear_at", ["inside_write", "another_connection"])
def test_nonstate_writer_retains_hits_after_clear(
    tmp_path: Path, writer: str, clear_at: str
) -> None:
    index = opened(tmp_path)
    values = {("old", "blob"): core.Problem("old", 1, "synthetic"), ("new", "blob"): None}
    index.keep_parses({("old", "blob"): values["old", "blob"]}, files=2)
    epoch = index.epoch()
    if clear_at == "another_connection":
        other = opened(tmp_path)
        with other.reading():
            assert other.parses([("old", "blob")])
        other.db.execute("BEGIN IMMEDIATE")
        index_space.clear(other.db)
        other.db.execute("COMMIT")
        other.close()
    with patch.object(index_space, "used_bytes", return_value=index_space.MIN_FILE_CAP + 1):
        if writer == "marker":
            index.mark_seen(
                "changed", {("new", "blob"): None}, {}, files=1, used=values, epoch=epoch
            )
        else:
            index.keep_parses({("new", "blob"): None}, files=1, used=values, epoch=epoch)
    assert index.epoch() > epoch
    assert index.parses(list(values)) == values
    index.close()


def test_app_marker_clear_retains_its_whole_working_set(tmp_path: Path) -> None:
    store, index = project(True), opened(tmp_path)
    seed(store, index)
    path = next(p for p in store.files if FIRST.id in p)
    store.files[path] = store.files[path].replace("evidence", "logs")
    with patch.object(index_space, "used_bytes", return_value=index_space.MIN_FILE_CAP + 1):
        assert printed(app(store, index), ["show", FIRST.id]) == printed(
            app(store), ["show", FIRST.id]
        )
    keys = {(p, b) for tree in store.trees() for p, b in tree.blobs.items()}
    assert set(index.parses(keys)) == keys
    index.close()


def test_parse_snapshot_clear_retains_its_whole_working_set(tmp_path: Path) -> None:
    store, index = project(), opened(tmp_path)
    snapshot_of(store.trees()[0], index)
    path = next(p for p in store.files if FIRST.id in p)
    store.files[path] = store.files[path].replace("evidence", "logs")
    with patch.object(index_space, "used_bytes", return_value=index_space.MIN_FILE_CAP + 1):
        snapshot_of(store.trees()[0], index)
    tree = store.trees()[0]
    keys = list(tree.blobs.items())
    assert set(index.parses(keys)) == set(keys)
    index.close()


def test_cap_is_named_and_used(tmp_path: Path) -> None:
    assert index_space.index_file_cap(1) == index_space.MIN_FILE_CAP
    assert index_space.index_file_cap(160801) == 160801 * index_space.INDEX_BYTES_PER_FILE
    index = opened(tmp_path)
    keep(index)
    epoch = index.epoch()
    with patch.object(index_space, "index_file_cap", return_value=0):
        index.mark_seen("clear", {}, {}, files=1)
    assert index.epoch() > epoch
    index.close()


@pytest.mark.parametrize("ref", ["d-zzzzzz", "nosuchcode", "q-zzzzzz"])
@pytest.mark.parametrize("broken", [False, True])
def test_unknown_ref_uses_complete_stored_state(tmp_path: Path, ref: str, broken: bool) -> None:
    store, index = project(True), opened(tmp_path)
    if broken:
        store.files["lodge/decisions/broken.md"] = "broken"
    seed(store, index)
    args = ["thread" if ref.startswith("q-") else "show", ref]
    expected = printed(app(store), args)
    with patch.object(core, "assemble", side_effect=AssertionError("rebuilt unknown ref")):
        assert printed(app(store, index), args) == expected
    index.close()


def test_unknown_id_with_damaged_bucket_rebuilds(tmp_path: Path) -> None:
    store, index = project(), opened(tmp_path)
    seed(store, index)
    index.db.execute("UPDATE buckets SET hash='missing' WHERE name='zz'")
    expected = printed(app(store), ["show", "d-zzzzzz"])
    with patch.object(core, "assemble", wraps=core.assemble) as assembled:
        assert printed(app(store, index), ["show", "d-zzzzzz"]) == expected
    assert assembled.called
    index.close()


def test_missing_blob_invalidates_completeness(tmp_path: Path) -> None:
    index = opened(tmp_path)
    keep(index)
    index.db.execute(
        "DELETE FROM bucket_blobs WHERE hash IN (SELECT hash FROM buckets WHERE name='aa')"
    )
    assert index.state("one") is None
    assert index.all_rows("one") == {}
    index.close()


def test_known_id_reads_its_bucket_once(tmp_path: Path) -> None:
    store, index = project(), opened(tmp_path)
    seed(store, index)
    expected = printed(app(store), ["show", FIRST.id])
    with patch.object(index, "rows", wraps=index.rows) as rows:
        assert printed(app(store, index), ["show", FIRST.id]) == expected
    assert rows.call_count == 1
    index.close()
