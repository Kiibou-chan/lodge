"""SQLite-backed command ordering, encoding failures, and incomplete-cache fallbacks."""

import io
from collections.abc import Callable
from contextlib import ExitStack, redirect_stdout
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import pytest
from indexed_support import app, printed, seed
from support import FIRST, project

from gitstore.index_helpers import opened
from gitstore.state_helpers import keep
from lodge import core
from lodge.app import FileKey, StateFacts, read_model
from lodge.app.state import snapshot_of
from lodge.cli import run
from lodge.gitstore import index_states


def test_marker_write_is_one_short_transaction(tmp_path: Path) -> None:
    index, store = opened(tmp_path), project()
    sql: list[str] = []
    index.db.set_trace_callback(sql.append)
    printed(app(store, index), ["show", FIRST.id])
    assert sql.count("BEGIN IMMEDIATE") == 1
    for table in ("states", "buckets", "answers", "citers"):
        assert index.db.execute(f"SELECT count(*) FROM {table}").fetchone()[0] == 0
    assert index.db.execute("SELECT count(*) FROM parses").fetchone()[0] == len(store.files)
    assert index.db.execute("SELECT count(*) FROM seen").fetchone()[0] == 1
    assert index.db.execute("SELECT kept FROM meta").fetchone()[0] == 0
    index.close()


def test_sql_and_every_constructor_follow_flush(tmp_path: Path) -> None:
    index, store = opened(tmp_path), project()
    lodge = app(store, index)
    printed(lodge, ["show", FIRST.id])
    events: list[str] = []

    class Stream(io.StringIO):
        def flush(self) -> None:
            events.append("flush")

    stream = Stream()

    def sql(statement: str) -> None:
        if statement == "BEGIN IMMEDIATE":
            assert events and events[0] == "flush" and FIRST.id in stream.getvalue()
            events.append("SQL")

    index.db.set_trace_callback(sql)
    constructors = ("build_rows", "build_answers", "build_citers", "build_facts", "build_state")
    originals = {name: getattr(read_model, name) for name in constructors}

    def wrapped(name: str) -> Callable[..., object]:
        def call(*args: object, **kwargs: object) -> object:
            assert events and events[0] == "flush"
            events.append(name)
            return originals[name](*args, **kwargs)

        return call

    with ExitStack() as stack, redirect_stdout(stream):
        for name in constructors:
            stack.enter_context(patch.object(read_model, name, wrapped(name)))
        assert run(["show", FIRST.id], lambda: lodge, lambda: "", lambda *_: 0, lambda: 0) == 0
    assert "SQL" in events and all(name in events for name in constructors)
    writes: list[str] = []
    index.db.set_trace_callback(writes.append)
    printed(lodge, ["show", FIRST.id])
    assert "BEGIN IMMEDIATE" not in writes
    index.close()


@pytest.mark.parametrize("table", ["states", "buckets", "answers", "citers", "parses"])
@pytest.mark.parametrize("damage", ["delete", "decode"])
def test_incomplete_rows_discard_the_whole_cached_answer(
    tmp_path: Path, table: str, damage: str
) -> None:
    store, index = project(), opened(tmp_path)
    seed(store, index)
    if damage == "delete":
        index.db.execute(f"DELETE FROM {table}")
    else:
        damaged = "bucket_blobs" if table == "buckets" else table
        index.db.execute(f"UPDATE {damaged} SET value='not JSON'")
    args = ["waiting"] if table == "answers" else ["show", FIRST.id, "--reasoning", "--provenance"]
    expected = printed(app(store), args)
    with patch.object(core, "assemble", wraps=core.assemble) as assembled:
        assert printed(app(store, index), args) == expected
    assert assembled.called
    index.close()


@pytest.mark.parametrize("eviction", [False, True])
@pytest.mark.parametrize("unknown", [False, True])
@pytest.mark.parametrize("failure", ["buckets", "facts"])
def test_encoding_failure_preserves_command_output(
    tmp_path: Path, eviction: bool, unknown: bool, failure: str
) -> None:
    store, index = project(), opened(tmp_path)
    if eviction:
        for n in range(4):
            keep(index, str(n))
    lodge = app(store, index)
    printed(lodge, ["show", FIRST.id])
    args = ["show", FIRST.id, "missing"] if unknown else ["show", FIRST.id]
    expected = printed(app(store), args)
    original = index_states.encode

    def encode(value: object) -> str:
        if failure == "facts" and isinstance(value, StateFacts):
            raise ValueError("injected facts encoding failure")
        return original(value)

    target = "buckets" if failure == "buckets" else "encode"
    replacement = (
        (lambda _: (_ for _ in ()).throw(ValueError("injected bucket encoding failure")))
        if failure == "buckets"
        else encode
    )
    with patch.object(index_states, target, replacement):
        assert printed(lodge, args) == expected
    assert index.db.execute("SELECT count(*) FROM states").fetchone()[0] == (4 if eviction else 0)
    index.close()


def test_tree_count_reaches_parse_only_writer(tmp_path: Path) -> None:
    store, index = project(), opened(tmp_path)
    tree = store.trees()[0]
    captured: list[int] = []
    original = index.keep_parses

    def writer(
        parses: dict[FileKey, core.Parsed | None],
        *,
        files: int,
        used: object = None,
        epoch: int | None = None,
    ) -> None:
        captured.append(files)
        original(parses, files=files)

    with patch.object(index, "keep_parses", writer):
        snapshot_of(tree, index)
        changed = replace(tree, blobs={p: b for p, b in tree.blobs.items() if FIRST.id in p})
        snapshot_of(changed, index)
    assert captured == [len(tree.files), len(tree.files)]
    index.close()
