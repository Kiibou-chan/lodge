"""Rows and saved answers agree with the complete core views."""

import pytest
from fakes import MemoryIndex, MemoryStore
from indexed_support import app, checked, printed, samples, seed

from lodge import core
from lodge.app import level1_of, read_model


@pytest.mark.parametrize("store", samples())
def test_level1_of_row_equals_core_level1(store: MemoryStore) -> None:
    state = checked(store)
    rows = read_model.build_rows(state)
    for ident, row in rows.items():
        record = state.snapshot.decisions.get(ident) or state.snapshot.entries[ident]
        assert level1_of(row, record) == core.level1(
            state.snapshot, state.derived, ident, state.failing
        )
        assert row.key == (
            state.snapshot.paths[ident],
            state.current.blobs[state.snapshot.paths[ident]],
        )


@pytest.mark.parametrize("store", samples())
def test_level3_links_equal(store: MemoryStore) -> None:
    state = checked(store)
    rows = read_model.build_rows(state)
    for ident, row in rows.items():
        assert row.links == core.level3(state.snapshot, state.derived, ident).links
        assert row.changed_by == state.derived.changed_by.get(ident, ())


@pytest.mark.parametrize("store", samples())
def test_answers_print_as_in_memory(store: MemoryStore) -> None:
    index = MemoryIndex()
    seed(store, index)
    for args in (["waiting"], ["threads"], ["thread", "q-aaaaaa"]):
        assert printed(app(store, index), args) == printed(app(store), args)
