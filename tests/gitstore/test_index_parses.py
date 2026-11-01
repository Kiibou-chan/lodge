"""Parse units are content addressed by both their path and their bytes."""

import json
import sqlite3
from collections.abc import Collection, Iterator
from pathlib import Path

import pytest
from builders import decision, snapshot_of

from gitstore.index_helpers import KEY, opened
from lodge.app import FileKey
from lodge.core import (
    CORE_CLASSES,
    Area,
    Parsed,
    Problem,
    derive,
    from_plain,
    level1,
    parse_file,
    to_plain,
)
from lodge.gitstore import index_db, index_parses, index_space


def test_hit_after_keep(tmp_path: Path) -> None:
    index = opened(tmp_path)
    value = parse_file(KEY[0], "broken")
    assert index.parses([KEY]) == {}
    index.keep_parses({KEY: value, ("lodge/spec/.gitkeep", "empty"): None})
    assert index.parses([KEY, ("lodge/spec/.gitkeep", "empty")]) == {
        KEY: value,
        ("lodge/spec/.gitkeep", "empty"): None,
    }
    index.close()
    again = opened(tmp_path)
    assert again.parses([KEY]) == {KEY: value}
    again.close()


def test_key_is_path_and_blob(tmp_path: Path) -> None:
    index = opened(tmp_path)
    text = "---\nkind: area\ntitle: Berths\norder: []\n---\n\nBerths.\n"
    a = ("lodge/spec/berths/_area.md", "same")
    b = ("lodge/spec/cranes/_area.md", "same")
    first, second = parse_file(a[0], text), parse_file(b[0], text)
    assert isinstance(first, Area) and isinstance(second, Area) and first.name != second.name
    index.keep_parses({a: first, b: second})
    assert index.parses([a, b, (a[0], "other")]) == {a: first, b: second}
    index.close()


def test_undecodable_row_is_a_miss(tmp_path: Path) -> None:
    index = opened(tmp_path)
    index.db.execute("INSERT INTO parses(path,blob,value) VALUES(?,?,?)", (*KEY, b"garbage"))
    assert index.parses([KEY]) == {}
    index.close()


def test_unencodable_key_skips_only_that_unit(tmp_path: Path) -> None:
    index = opened(tmp_path)
    bad = ("lodge/decisions/stray-\udcff.md", "blob")
    index.keep_parses({bad: None, KEY: None, ("last", "blob"): None})
    assert index.parses([bad, KEY, ("last", "blob")]) == {KEY: None, ("last", "blob"): None}
    index.close()


@pytest.mark.parametrize("method", ["parses", "keep_parses", "epoch"])
def test_any_adapter_exception_is_a_miss(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, method: str
) -> None:
    index = opened(tmp_path)

    def fail(*args: object, **kwargs: object) -> None:
        raise RuntimeError("injected adapter failure")

    monkeypatch.setattr(index_db, "transaction", fail)
    if method == "parses":
        assert index.parses([KEY]) == {}
    elif method == "keep_parses":
        index.keep_parses({KEY: None})
    else:
        assert index.epoch() == 0
    index.close()


class CountingConnection(sqlite3.Connection):
    selects: list[str]

    def execute(self, sql: str, parameters: object = (), /) -> sqlite3.Cursor:
        if sql.startswith("SELECT") and "FROM parses" in sql:
            self.selects.append(sql)
        return super().execute(sql, parameters)  # type: ignore[arg-type]


@pytest.fixture
def scan_index(tmp_path: Path) -> Iterator[index_db.IndexDB]:
    initial = opened(tmp_path)
    path = initial.db.execute("PRAGMA database_list").fetchone()[2]
    units: dict[FileKey, Parsed | None] = {
        (f"lodge/spec/berths/s-{n:06d}.md", "current"): Problem(str(n), 1, "broken")
        for n in range(1500)
    }
    units[("lodge/spec/berths/s-000000.md", "current")] = None
    units[("lodge/spec/berths/s-000001.md", "current")] = Area("berths", "Berths", "Berths.", ())
    units.update({(key[0], "older"): None for key in list(units)[:500]})
    initial.keep_parses(units)
    initial.close()
    db = sqlite3.connect(path, isolation_level=None, factory=CountingConnection)
    db.selects = []
    index = index_db.IndexDB(db, None)
    try:
        yield index
    finally:
        index.close()


def requested_keys() -> list[FileKey]:
    keys = [(f"lodge/spec/berths/s-{n:06d}.md", "current") for n in range(1480)]
    keys.extend((f"absent-{n}", "current") for n in range(20))
    return keys


def assert_one_scan(db: sqlite3.Connection) -> None:
    assert isinstance(db, CountingConnection)
    assert db.selects == ["SELECT path, blob, value FROM parses ORDER BY rowid"]


def per_key(index: index_db.IndexDB, keys: Collection[FileKey]) -> dict[FileKey, Parsed | None]:
    found: dict[FileKey, Parsed | None] = {}
    for key in keys:
        found.update(index.parses([key]))
    assert isinstance(index.db, CountingConnection)
    index.db.selects.clear()
    return found


def test_scan_equals_per_key(scan_index: index_db.IndexDB) -> None:
    keys = requested_keys()
    keys.extend(keys[:5])
    expected = per_key(scan_index, keys)
    assert len(expected) == 1480 and expected[keys[0]] is None
    assert isinstance(expected[keys[2]], Problem)
    assert scan_index.parses(keys) == expected
    assert_one_scan(scan_index.db)


@pytest.mark.parametrize(
    "bad_values",
    [
        pytest.param(['["Problem"'], id="truncated"),
        pytest.param(["null,null"], id="joined-nulls"),
        pytest.param(['null,"foo', 'bar"'], id="joined-adjacent"),
        pytest.param(['["Problem",123,1,"broken",null]'], id="validator"),
        pytest.param(["123"], id="integer"),
        pytest.param(['"text"'], id="text"),
        pytest.param(["{}"], id="mapping"),
        pytest.param(['[""]'], id="tuple"),
        pytest.param(["level1"], id="non-parse-dataclass"),
    ],
)
def test_one_bad_value_is_one_miss(scan_index: index_db.IndexDB, bad_values: list[str]) -> None:
    keys = requested_keys()
    damaged = keys[10 : 10 + len(bad_values)]
    for key, raw in zip(damaged, bad_values, strict=True):
        if raw == "level1":
            record = decision()
            snapshot = snapshot_of(record)
            value = level1(snapshot, derive(snapshot), record.id, frozenset())
            raw = json.dumps(to_plain(value))
            assert from_plain(json.loads(raw), CORE_CLASSES) == value
        scan_index.db.execute("UPDATE parses SET value=? WHERE path=? AND blob=?", (raw, *key))
    expected = per_key(scan_index, keys)
    assert len(expected) == 1480 - len(damaged)
    assert all(key not in expected for key in damaged)
    assert scan_index.parses(keys) == expected
    assert_one_scan(scan_index.db)


@pytest.mark.parametrize("count", [999, 1000, 1500])
def test_scan_reads_once(scan_index: index_db.IndexDB, count: int) -> None:
    keys = requested_keys()[:count]
    scan_index.parses(keys)
    assert isinstance(scan_index.db, CountingConnection)
    if count < 1000:
        assert len(scan_index.db.selects) == count
        # Exercise the new branch in this case too before implementing it.
        scan_index.db.selects.clear()
        scan_index.parses(requested_keys())
    assert_one_scan(scan_index.db)


@pytest.mark.parametrize("pin_snapshot", [True, False], ids=["after-select", "before-select"])
def test_scan_inside_one_read_transaction(
    scan_index: index_db.IndexDB, monkeypatch: pytest.MonkeyPatch, pin_snapshot: bool
) -> None:
    keys = requested_keys()
    expected = per_key(scan_index, keys)
    path = scan_index.db.execute("PRAGMA database_list").fetchone()[2]
    writer = sqlite3.connect(path, isolation_level=None)
    original = index_parses.find_parses

    def interleaved(
        db: sqlite3.Connection, requested: Collection[FileKey]
    ) -> dict[FileKey, Parsed | None]:
        assert db.in_transaction
        if pin_snapshot:
            db.execute("SELECT epoch FROM meta").fetchone()
        with index_db.transaction(writer, write=True):
            index_space.clear(writer)
        return original(db, requested)

    try:
        with monkeypatch.context() as patch:
            patch.setattr(index_db, "find_parses", interleaved)
            assert scan_index.parses(keys) == (expected if pin_snapshot else {})
        assert_one_scan(scan_index.db)
        assert not scan_index.db.in_transaction
        assert scan_index.parses(keys) == {}
        assert scan_index.epoch() == 2
    finally:
        writer.close()
