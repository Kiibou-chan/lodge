"""State completeness, immutable shared units, eviction, and bounded growth."""

import json
from dataclasses import fields, replace
from pathlib import Path

import pytest

from gitstore.index_helpers import KEY, filename, opened
from gitstore.state_helpers import FACT, ROW, changed_rows, keep
from lodge.app import StateFacts, StoredState
from lodge.core import Problem
from lodge.gitstore import index_space
from lodge.gitstore.index_states import KEPT_STATES, decode


def test_stored_row_without_threads_is_refused(tmp_path: Path) -> None:
    index = opened(tmp_path)
    keep(index)
    raw = index.db.execute("SELECT value FROM states WHERE key='one'").fetchone()[0]
    assert isinstance(decode(raw), StoredState)
    plain = json.loads(raw)
    plain.pop(1 + [field.name for field in fields(StoredState)].index("threads"))
    raw = json.dumps(plain)
    index.db.execute("UPDATE states SET value=? WHERE key='one'", (raw,))
    stored_raw = index.db.execute("SELECT value FROM states WHERE key='one'").fetchone()[0]
    with pytest.raises(ValueError, match="invalid cached arity"):
        decode(stored_raw)
    assert index.state("one") is None
    index.close()


def test_kept_states_constant(tmp_path: Path) -> None:
    assert KEPT_STATES == 4
    index = opened(tmp_path)
    for n in range(5):
        keep(index, str(n))
    assert index.db.execute("SELECT count(*) FROM states").fetchone()[0] == KEPT_STATES
    index.close()


def test_bucket_by_last_two_characters(tmp_path: Path) -> None:
    index = opened(tmp_path)
    rows = {"s-aaaaaa": ROW, "d-bbbbaa": ROW, "d-bbbbbb": ROW}
    keep(index, rows=rows)
    assert index.rows("one", ["s-aaaaaa", "d-bbbbaa"]) == {
        i: rows[i] for i in rows if i.endswith("aa")
    }
    assert index.all_rows("one") == rows
    assert index.db.execute("SELECT count(*) FROM buckets WHERE key='one'").fetchone()[0] == 1024
    index.close()


def test_seen_read_writes_nothing(tmp_path: Path) -> None:
    index = opened(tmp_path)
    keep(index)
    index.db.execute("PRAGMA wal_checkpoint(TRUNCATE)")
    before = filename(tmp_path).read_bytes()
    wal = filename(tmp_path).with_name(filename(tmp_path).name + "-wal")
    before_wal = wal.read_bytes()
    sql: list[str] = []
    index.db.set_trace_callback(sql.append)
    with index.reading():
        assert index.state("one") is not None
        assert index.rows("one", ["s-aaaaaa"])
        assert index.answer("one", "waiting") is not None
    assert not any(s == "BEGIN IMMEDIATE" for s in sql)
    assert filename(tmp_path).read_bytes() == before and wal.read_bytes() == before_wal
    index.close()


def test_eviction_deletes_only_the_states_own_rows(tmp_path: Path) -> None:
    index = opened(tmp_path)
    for n in range(KEPT_STATES + 1):
        keep(
            index,
            str(n),
            rows={f"s-{n:06x}": replace(ROW, key=(str(n), "blob"))},
            facts={str(n): FACT},
        )
    with index.reading():
        assert index.state("0") is None
        assert index.facts("0") == FACT
        assert index.parses([("0", "blob")]) == {("0", "blob"): None}
    for table in ("states", "buckets", "answers", "citers"):
        assert index.db.execute(f"SELECT count(*) FROM {table} WHERE key='0'").fetchone()[0] == 0
    index.close()


def test_revert_to_the_evicted_states_contents(tmp_path: Path) -> None:
    index = opened(tmp_path)
    keep(index, "0")
    rowid = index.db.execute("SELECT rowid FROM parses WHERE path=?", (KEY[0],)).fetchone()
    for n in range(1, KEPT_STATES + 1):
        keep(index, str(n), changed_rows())
    keep(index, "reverted", misses=())
    assert index.parses([KEY]) == {KEY: None}
    assert index.facts("published") == FACT
    assert index.db.execute("SELECT rowid FROM parses WHERE path=?", (KEY[0],)).fetchone() == rowid
    index.close()


def test_rekeep_replaces_the_state_whole(tmp_path: Path) -> None:
    index = opened(tmp_path)
    for key in ("one", "two", "three", "four"):
        keep(index, key)
    keep(index, "one", changed_rows())
    keep(index, "five")
    assert index.state("two") is None and index.state("one") is not None
    assert index.all_rows("one") == changed_rows()
    assert index.facts("published") == FACT
    keep(index, "six", facts={"published": StateFacts({})})
    assert index.facts("published") == FACT
    index.close()


@pytest.mark.parametrize("clear_at", ["after_hits", "between_lookups"])
def test_keep_after_another_process_cleared(tmp_path: Path, clear_at: str) -> None:
    a, b = opened(tmp_path), opened(tmp_path)
    keep(a)
    epoch = a.epoch()
    parses = a.parses([KEY])
    facts = a.facts("published") if clear_at == "after_hits" else None
    with b.reading():
        assert b.state("one")
    b.db.execute("BEGIN IMMEDIATE")
    index_space.clear(b.db)
    b.db.execute("COMMIT")
    if clear_at == "between_lookups":
        assert a.facts("published") is None
        facts = FACT
    assert facts is not None
    keep(a, "after", parses=parses, facts={"published": facts}, misses=(), epoch=epoch)
    assert a.parses([KEY]) == parses and a.facts("published") == FACT
    assert a.state("after") is not None
    a.close()
    b.close()


def test_clear_between_the_parses_and_facts_lookups(tmp_path: Path) -> None:
    test_keep_after_another_process_cleared(tmp_path, "between_lookups")


@pytest.mark.parametrize("initial_clear", [False, True])
def test_first_sightings_alone_stay_under_the_cap(tmp_path: Path, initial_clear: bool) -> None:
    index = opened(tmp_path)
    if initial_clear:
        index.db.execute("BEGIN IMMEDIATE")
        index_space.clear(index.db)
        index.db.execute("COMMIT")
    epoch = index.epoch()

    for n in range(50):
        index.mark_seen(str(n), {(str(n), "blob"): Problem("x", 1, "x" * 600000)}, {}, files=1)
        assert index_space.used_bytes(index.db) <= index_space.index_file_cap(1) + 700000
        assert index.db.execute("SELECT kept FROM meta").fetchone()[0] == 0
    assert index.epoch() > epoch and index.seen("49")
    keep(index, "49")
    assert index.state("49")
    index.close()


@pytest.mark.parametrize("with_state", [False, True])
def test_parse_only_writers_cross_the_cap(tmp_path: Path, with_state: bool) -> None:
    index = opened(tmp_path)
    if with_state:
        keep(index)

    epoch = index.epoch()
    for n in range(50):
        index.keep_parses({(str(n), "blob"): Problem("x", 1, "x" * 600000)}, files=1)
        assert index_space.used_bytes(index.db) < index_space.index_file_cap(1) + 700000
    assert index.epoch() > epoch
    assert index.db.execute("SELECT kept FROM meta").fetchone()[0] == 0
    index.close()


def test_marker_bounded_and_cleared(tmp_path: Path) -> None:
    index = opened(tmp_path)
    for n in range(65):
        index.mark_seen(str(n), {}, {}, files=1)
    assert not index.seen("0") and index.seen("1") and index.seen("64")
    assert index.db.execute("SELECT count(*) FROM seen").fetchone()[0] == 64
    index.db.execute("BEGIN IMMEDIATE")
    index_space.clear(index.db)
    index.db.execute("COMMIT")
    assert not index.seen("64")
    index.close()
