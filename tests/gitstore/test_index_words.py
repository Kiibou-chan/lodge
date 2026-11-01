"""FTS candidates use core's words, immutable units, and explicit snapshots."""

import sqlite3
from pathlib import Path
from unittest.mock import patch

import pytest
from builders import area, decision, entry, thread

from gitstore.index_helpers import filename, opened
from lodge.core import Parsed, Problem, parse_words
from lodge.core.words import words
from lodge.gitstore.index_space import clear
from lodge.gitstore.index_transactions import transaction
from lodge.gitstore.index_words import create_words


def test_ascii_tokenizer_returns_core_words(tmp_path: Path) -> None:
    index = opened(tmp_path)
    record = decision(
        title="Crane 123 café İ Σ ﬃ a_b e\u0301lan", statement="Ångström 42 船舶 Straße"
    )
    key = ("lodge/decisions/arbitrary.md", "blob")
    index.keep_parses({key: record}, files=1)
    title, statement = words(record.title), words(record.statement)
    for word in title | statement:
        assert index.candidates([word], False) == {key: (frozenset(title), frozenset(statement))}
    assert parse_words(record) == (" ".join(sorted(title)), " ".join(sorted(statement)))
    for parsed in (None, area(), thread(), Problem("x", 1, "crane")):
        assert parse_words(parsed) == ("", "")
    assert parse_words(entry(title="Berth", statement="Crane")) == ("berth", "crane")
    index.close()


def test_any_and_every(tmp_path: Path) -> None:
    index = opened(tmp_path)
    a, b = ("a", "1"), ("b", "2")
    index.keep_parses(
        {a: decision(title="Berth", statement="Crane"), b: decision(title="Crane")}, files=2
    )
    assert set(index.candidates(["berth", "crane"], False) or {}) == {a, b}
    assert set(index.candidates(["berth", "crane"], True) or {}) == {a}
    assert index.candidates(["absent"], False) == {}
    assert index.candidates([], False) == index.candidates([], True) == {}
    index.close()


def test_path_words_are_not_candidates(tmp_path: Path) -> None:
    index = opened(tmp_path)
    index.keep_parses({("lodge/decisions/berth.md", "blob"): decision(title="Crane")}, files=1)
    for word in ("lodge", "decisions", "md", "berth"):
        assert index.candidates([word], False) == {}
    index.close()


def test_words_row_shares_the_parse_rowid(tmp_path: Path) -> None:
    index = opened(tmp_path)
    values: dict[tuple[str, str], Parsed | None] = {
        (str(n), "blob"): decision(title=f"Crane {n}") for n in range(3)
    }
    values["empty", "blob"] = None
    index.keep_parses(values, files=4)
    assert index.db.execute(
        "SELECT p.rowid,w.rowid FROM parses p JOIN words w ON p.rowid=w.rowid ORDER BY p.rowid"
    ).fetchall() == [(n, n) for n in range(1, 5)]
    index.keep_parses({("0", "blob"): decision(title="Changed")}, files=4)
    assert index.candidates(["changed"], False) == {}
    assert len(index.candidates(["crane"], False) or {}) == 3
    index.close()


def test_without_fts5_and_sql_errors_are_misses(tmp_path: Path) -> None:
    class NoFTS(sqlite3.Connection):
        def execute(self, sql: str, parameters: object = (), /) -> sqlite3.Cursor:
            if "CREATE VIRTUAL TABLE" in sql:
                raise sqlite3.OperationalError("no such module: fts5")
            return super().execute(sql, parameters)  # type: ignore[arg-type]

    db = sqlite3.connect(":memory:", factory=NoFTS)
    create_words(db)
    assert db.execute("SELECT name FROM sqlite_master").fetchall() == []
    db.close()
    index = opened(tmp_path)
    index.db.execute("DROP TABLE words")
    index.keep_parses({("a", "blob"): decision(title="Crane")}, files=1)
    assert index.parses([("a", "blob")])
    assert index.candidates(["crane"], False) is None
    with patch("lodge.gitstore.index_db.find_candidates", side_effect=sqlite3.OperationalError):
        assert index.candidates(["crane"], False) is None
    assert not index.db.in_transaction
    index.close()


def test_clear_preserves_word_snapshot_and_recreates_fts(tmp_path: Path) -> None:
    a, b = opened(tmp_path), opened(tmp_path)
    key = ("a", "blob")
    a.keep_parses({key: decision(title="Crane")}, files=1)
    epoch = a.epoch()
    with a.reading():
        assert a.candidates(["crane"], False)
        b.db.execute("BEGIN IMMEDIATE")
        clear(b.db)
        b.db.execute("COMMIT")
        assert a.candidates(["crane"], False)
    assert a.epoch() == epoch + 1
    assert a.candidates(["crane"], False) == {}
    a.keep_parses({key: decision(title="Crane")}, files=1)
    assert a.candidates(["crane"], False)
    a.close()
    b.close()


def test_fts_creation_error_rolls_back_the_clear(tmp_path: Path) -> None:
    class FailedCreate(sqlite3.Connection):
        def execute(self, sql: str, parameters: object = (), /) -> sqlite3.Cursor:
            if "CREATE VIRTUAL TABLE" in sql:
                raise sqlite3.OperationalError("injected FTS creation failure")
            return super().execute(sql, parameters)  # type: ignore[arg-type]

    index = opened(tmp_path)
    key = ("a", "blob")
    index.keep_parses({key: decision(title="Uniquequay")}, files=1)
    epoch = index.epoch()
    db = sqlite3.connect(filename(tmp_path), isolation_level=None, factory=FailedCreate)
    try:
        with (
            pytest.raises(sqlite3.OperationalError, match="injected FTS creation failure"),
            transaction(db, write=True),
        ):
            clear(db)
        assert index.epoch() == epoch
        assert index.candidates(["uniquequay"], False)
    finally:
        db.close()
        index.close()
