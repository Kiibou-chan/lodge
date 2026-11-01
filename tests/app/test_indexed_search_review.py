"""Review regressions for complete stored searches and historical parse units."""

from pathlib import Path
from unittest.mock import patch

import pytest
from builders import decision
from fakes import MemoryStore
from indexed_support import app, printed, seed

from lodge.gitstore.index_db import IndexDB, open_index


@pytest.mark.parametrize("args", [["THE"], ["--phrase", "of the"], ["d-zzzzzz"]])
def test_query_fallback_does_not_keep_or_change_epoch(tmp_path: Path, args: list[str]) -> None:
    index = open_index(tmp_path)
    assert isinstance(index, IndexDB)
    store = MemoryStore(decision(id="d-aaaaaa", code="THE"))
    seed(store, index)
    before = index.epoch()
    expected = printed(app(store), ["search", *args])
    with (
        patch.object(index, "keep_state", wraps=index.keep_state) as keeps,
        patch("lodge.gitstore.index_space.index_file_cap", return_value=1),
    ):
        for _ in range(6):
            assert printed(app(store, index), ["search", *args]) == expected
        assert keeps.call_count == 0
    assert index.epoch() == before
    index.close()


def test_deleted_record_does_not_send_search_to_memory(tmp_path: Path) -> None:
    index = open_index(tmp_path)
    assert isinstance(index, IndexDB)
    store = MemoryStore(
        decision(id="d-aaaaaa", title="Crane"), decision(id="d-bbbbbb", title="Crane berth")
    )
    seed(store, index)
    del store.files[next(p for p in store.files if "d-aaaaaa" in p)]
    seed(store, index)
    expected = printed(app(store), ["search", "crane", "--brief"])
    with (
        patch("lodge.app.reads.search_many", side_effect=AssertionError("must use stored rows")),
        patch.object(index, "keep_state", wraps=index.keep_state) as keeps,
    ):
        for _ in range(6):
            assert printed(app(store, index), ["search", "crane", "--brief"]) == expected
        assert keeps.call_count == 0
    index.close()


def test_empty_search_fetches_only_displayed_parses(tmp_path: Path) -> None:
    index = open_index(tmp_path)
    assert isinstance(index, IndexDB)
    store = MemoryStore(*(decision(id=f"d-{n:06x}") for n in range(100)))
    seed(store, index)
    args = ["search", "--kind", "decision", "--limit", "3", "--brief"]
    expected = printed(app(store), args)
    with patch.object(index, "parses", wraps=index.parses) as parses:
        assert printed(app(store, index), args) == expected
        assert sum(len(c.args[0]) for c in parses.call_args_list) <= 3
    index.close()


def test_unknown_exact_id_uses_stored_absence(tmp_path: Path) -> None:
    index = open_index(tmp_path)
    assert isinstance(index, IndexDB)
    store = MemoryStore(decision())
    seed(store, index)
    expected = printed(app(store), ["search", "d-zzzzzz"])
    with patch("lodge.app.reads.search_many", side_effect=AssertionError("must use stored rows")):
        assert printed(app(store, index), ["search", "d-zzzzzz"]) == expected
    index.close()


def test_unavailable_fts_does_not_keep_complete_state(tmp_path: Path) -> None:
    index = open_index(tmp_path)
    assert isinstance(index, IndexDB)
    store = MemoryStore(decision(title="Crane"))
    seed(store, index)
    expected = printed(app(store), ["search", "crane"])
    before = index.epoch()
    with (
        patch.object(index, "candidates", return_value=None),
        patch.object(index, "keep_state", wraps=index.keep_state) as keeps,
        patch("lodge.gitstore.index_space.index_file_cap", return_value=1),
    ):
        for _ in range(6):
            assert printed(app(store, index), ["search", "crane"]) == expected
        assert keeps.call_count == 0
    assert index.epoch() == before
    index.close()
