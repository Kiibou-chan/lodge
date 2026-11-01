"""Search uses the stored state, while sharing core's exact ranking and output."""

import multiprocessing
import random
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import pytest
from builders import decision
from fake_index import MemoryIndex
from fakes import MemoryStore
from indexed_support import app, large_store, printed, seed

from lodge import core
from lodge.gitstore.index_db import IndexDB, open_index
from lodge.gitstore.index_space import clear
from lodge.gitstore.index_states import KEPT_STATES


def opened(folder: Path) -> IndexDB:
    index = open_index(folder)
    assert isinstance(index, IndexDB)
    return index


def search_store() -> MemoryStore:
    store = large_store()
    rng = random.Random(1042)
    for n, (path, text) in enumerate(list(store.files.items())):
        record = core.parse_file(path, text)
        if isinstance(record, (core.Decision, core.SpecEntry)):
            record = replace(
                record,
                title=f"{rng.choice(['Berth crane', 'Crane berth', 'Tide', 'Quay'])} {n}",
                statement=f"See B.1, E, THE, and A. {rng.choice(['berth', 'crane', 'tide'])}.",
            )
            if isinstance(record, core.Decision) and n == 490:
                record = replace(record, code="THE")
            store.files[path] = core.write_record(record)
    store.published = dict(store.files)
    return store


def test_search_prints_as_in_memory() -> None:
    store, index = search_store(), MemoryIndex()
    seed(store, index)
    rng = random.Random(1042)
    queries = [
        "berth",
        "berth crane",
        "tide",
        "B.1",
        "B",
        "E",
        "MISSING",
        "THE",
        "of the",
        "",
        "d-000001",
    ]
    filters = [
        [],
        ["--kind", "spec"],
        ["--kind", "decision"],
        ["--scope", "process"],
        ["--scope", "product"],
        ["--status", "any"],
        ["--status", "replaced"],
        ["--status", "retired"],
        ["--area", "storage"],
        ["--area", "missing"],
        ["--by", "author"],
        ["--by", "coordinator"],
    ]
    with patch.object(index, "candidates", wraps=index.candidates) as calls:
        for n in range(300):
            query = queries[n % len(queries)]
            args = ["search", *(["--phrase", query] if n % 4 == 0 else [query])]
            args += filters[n % len(filters)] + ["--limit", str(rng.randrange(1, 35))]
            if n % 2:
                args += ["--brief"]
            if n % 5 == 0:
                args += [rng.choice(queries)]
            assert printed(app(store, index), args) == printed(app(store), args), (1042, n, args)
        assert calls.call_count > 100
    with patch.object(
        store, "listings", side_effect=AssertionError("stored search must not build")
    ):
        assert (
            app(store, index).search("berth", core.Filters()).items
            == app(store).search("berth", core.Filters()).items
        )


def test_older_parse_of_a_record_is_not_a_candidate() -> None:
    store = MemoryStore(decision(id="d-aaaaaa", title="Crane"))
    index = MemoryIndex()
    seed(store, index)
    path = next(iter(store.files))
    store.files[path] = core.write_record(decision(id="d-aaaaaa", title="Tide"))
    seed(store, index)
    with patch("lodge.app.reads.search_many", side_effect=AssertionError("must use stored rows")):
        assert app(store, index).search("crane", core.Filters()).items == ()


@pytest.mark.parametrize("query,phrase", [("THE", False), ("of the", True)])
def test_needs_memory_queries_run_in_memory(query: str, phrase: bool) -> None:
    store, index = search_store(), MemoryIndex()
    seed(store, index)
    expected = printed(app(store), ["search", *(["--phrase"] if phrase else []), query])
    with patch.object(index, "candidates", side_effect=AssertionError("memory query")) as calls:
        assert (
            printed(app(store, index), ["search", *(["--phrase"] if phrase else []), query])
            == expected
        )
        assert calls.call_count == 0
    assert index.epochs > 1


def test_without_fts5_runs_in_memory() -> None:
    store, index = search_store(), MemoryIndex()
    seed(store, index)
    with patch.object(index, "candidates", return_value=None) as calls:
        assert printed(app(store, index), ["search", "berth"]) == printed(
            app(store), ["search", "berth"]
        )
        assert calls.call_count == 1


def test_revert_after_eviction_is_found(tmp_path: Path) -> None:
    index = opened(tmp_path)
    store = MemoryStore(decision(id="d-aaaaaa", title="Uniquequay"))
    original = dict(store.files)
    old = seed(store, index)
    for n in range(KEPT_STATES + 1):
        store.files[next(iter(original))] = core.write_record(
            decision(id="d-aaaaaa", title=f"Crane {n}")
        )
        seed(store, index)
    assert index.state(old) is None
    store.files = original
    seed(store, index)
    assert index.candidates(["uniquequay"], False)
    with patch("lodge.app.reads.search_many", side_effect=AssertionError("must use index")):
        result = printed(app(store, index), ["search", "uniquequay"])
    assert result == printed(app(store), ["search", "uniquequay"])
    index.close()


def another_writer(folder: Path, clearing: bool) -> None:
    index = opened(folder)
    if clearing:
        index.db.execute("BEGIN IMMEDIATE")
        clear(index.db)
        index.db.execute("COMMIT")
    for n in range(KEPT_STATES + 1):
        seed(MemoryStore(decision(id="d-bbbbbb", title=f"Other {n}")), index)
    index.close()


@pytest.mark.parametrize("clearing", [True, False])
def test_words_rows_after_a_clear_and_another_keep(tmp_path: Path, clearing: bool) -> None:
    a = opened(tmp_path)
    store = MemoryStore(decision(id="d-aaaaaa", title="Uniquequay"))
    with patch.object(a, "keep_state", wraps=a.keep_state) as calls:
        seed(store, a)
    args, kwargs = calls.call_args
    epoch, hits = a.epoch(), a.parses(list(args[5]))
    process = multiprocessing.get_context("fork").Process(
        target=another_writer, args=(tmp_path, clearing)
    )
    process.start()
    process.join(10)
    assert process.exitcode == 0
    a.keep_state(
        args[0], args[1], args[2], args[3], args[4], hits, (), epoch, files=kwargs["files"]
    )
    found = a.candidates(["uniquequay"], False)
    assert found is not None and set(hits) <= set(found)
    assert printed(app(store, a), ["search", "uniquequay"]) == printed(
        app(store), ["search", "uniquequay"]
    )
    a.close()


def test_search_keeps_only_after_second_output_flush() -> None:
    store, index = search_store(), MemoryIndex()
    args = ["search", "berth", "--brief"]
    assert printed(app(store, index), args) == printed(app(store), args)
    assert not index.states and index.markers
    assert printed(app(store, index), args) == printed(app(store), args)
    assert len(index.states) == 1


@pytest.mark.parametrize("empty", [False, True])
def test_incomplete_rows_discard_the_cached_search(empty: bool) -> None:
    store, index = search_store(), MemoryIndex()
    seed(store, index)
    args = ["search", "" if empty else "berth", "--brief"]
    expected = printed(app(store), args)
    method = "all_rows" if empty else "rows"
    with patch.object(index, method, return_value={}):
        assert printed(app(store, index), args) == expected


@pytest.mark.parametrize("query", ["BERTH-1", "ROOT"])
def test_sqlite_code_search_uses_stored_rows(tmp_path: Path, query: str) -> None:
    index = opened(tmp_path)
    store = MemoryStore(
        decision(id="d-aaaaaa", code="BERTH-1", title="Quay"),
        decision(id="d-bbbbbb", code="ROOT.why", title="Pilot"),
        decision(id="d-cccccc", statement="See ROOT and BERTH-1."),
    )
    seed(store, index)
    args = ["search", query, "--brief"]
    expected = printed(app(store), args)
    with patch.object(store, "listings", side_effect=AssertionError("code search rebuilt")):
        assert printed(app(store, index), args) == expected
    index.close()


def test_missing_exact_id_row_discards_the_cached_search() -> None:
    store = MemoryStore(decision(id="d-aaaaaa", title="Quay"))
    index = MemoryIndex()
    seed(store, index)
    args = ["search", "d-aaaaaa", "--brief"]
    expected = printed(app(store), args)
    with patch.object(index, "rows", return_value={}):
        assert printed(app(store, index), args) == expected
