"""Deterministic WAL interleavings and failure at every write statement."""

import sqlite3
from collections.abc import Collection, Mapping
from pathlib import Path
from unittest.mock import patch

import pytest
from indexed_support import app, printed
from support import FIRST, project

from gitstore.index_helpers import KEY, filename, opened
from gitstore.state_helpers import ROW, changed_rows, keep
from gitstore.test_index_failures import Interrupted
from lodge.app import FileKey, Row, StateFacts, StoredState
from lodge.core import Parsed
from lodge.gitstore.index_db import IndexDB


def test_reader_keeps_its_snapshot_across_a_commit(tmp_path: Path) -> None:
    reader, writer = opened(tmp_path), opened(tmp_path)
    original = {"s-aaaaaa": ROW, "s-bbbbbb": ROW}
    keep(reader, rows=original)
    with reader.reading():
        assert reader.state("one")
        assert reader.rows("one", ["s-aaaaaa"])
        keep(writer, rows=changed_rows())
        assert reader.db.in_transaction
        assert reader.rows("one", ["s-bbbbbb"]) == {"s-bbbbbb": ROW}
    assert reader.all_rows("one") == changed_rows()
    reader.close()
    writer.close()


def test_eviction_between_lookups_cannot_split_a_read(tmp_path: Path) -> None:
    reader, writer = opened(tmp_path), opened(tmp_path)
    keep(reader)
    with reader.reading():
        assert reader.state("one")
        for n in range(4):
            keep(writer, str(n))
        assert reader.rows("one", ["s-aaaaaa"]) == {"s-aaaaaa": ROW}
        assert reader.answer("one", "waiting") == ((), ())
    assert reader.state("one") is None
    reader.close()
    writer.close()


def test_unit_found_by_one_process_survives_another_keep(tmp_path: Path) -> None:
    a, b = opened(tmp_path), opened(tmp_path)
    keep(a)
    epoch = a.epoch()
    hits = a.parses([KEY])
    for n in range(4):
        keep(b, str(n), changed_rows())
    keep(a, "last", parses=hits, misses=(), epoch=epoch)
    assert a.state("last") and a.parses([KEY]) == hits
    a.close()
    b.close()


@pytest.mark.parametrize("eviction", [False, True])
@pytest.mark.parametrize("unknown", [False, True])
def test_keep_state_interrupted_at_each_statement(
    tmp_path: Path, eviction: bool, unknown: bool
) -> None:
    initial = opened(tmp_path)
    for n in range(4 if eviction else 1):
        keep(initial, str(n))
    initial.close()
    db = sqlite3.connect(filename(tmp_path), isolation_level=None, factory=Interrupted)
    index = IndexDB(db, None)
    store = project()
    lodge = app(store, index)
    args = ["show", FIRST.id, "missing"] if unknown else ["show", FIRST.id]
    expected = printed(app(store), args)
    assert printed(lodge, args) == expected  # first sighting
    statements: list[str] = []
    original = index.keep_state
    after = 0

    def writer(
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
        db.count, db.after = 0, after
        if not after:
            db.set_trace_callback(statements.append)
        try:
            original(state, rows, answers, citing, facts, parses, misses, epoch, files=files)
        finally:
            db.after = 0
            db.set_trace_callback(None)

    with patch.object(index, "keep_state", writer):
        assert printed(lodge, args) == expected  # measure the actual deferred transaction
        count = len(statements)
        key = next(key for (key,) in db.execute("SELECT key FROM states") if len(key) > 1)
        db.execute("BEGIN IMMEDIATE")
        for table in ("states", "buckets", "answers", "citers"):
            db.execute(f"DELETE FROM {table} WHERE key=?", (key,))
        db.execute("COMMIT")
        if eviction:
            keep(index, "0")
        for after in range(1, count + 1):
            assert printed(lodge, args) == expected, after
            assert index.state(key) is None, after
            for n in range(4 if eviction else 1):
                assert index.state(str(n)) is not None, after
                assert index.all_rows(str(n)) == {"s-aaaaaa": ROW}, after
            assert not db.in_transaction
    index.close()


def test_two_builders_of_one_state(tmp_path: Path) -> None:
    a, b = opened(tmp_path), opened(tmp_path)
    keep(a)
    keep(b, rows=changed_rows())
    assert a.all_rows("one") == changed_rows()
    state = a.state("one")
    assert state is not None and state.promised == (1024, 1, 1)
    a.close()
    b.close()
