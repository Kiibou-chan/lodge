"""Exact reads may reuse only parses keyed by the bytes they actually read."""

from dataclasses import replace

import pytest
from builders import area, decision, entry
from fakes import CountingIds, FixedClock, MemoryIndex, MemoryStore

from lodge import core
from lodge.app import Gate, Lodge, state
from lodge.core import CoreSettings, Filters, Parsed, Raises


def application(store: MemoryStore, index: MemoryIndex | None) -> Lodge:
    return Lodge(store, FixedClock(), CountingIds(), CoreSettings(), index=index)


def test_second_read_parses_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    record = decision(id="d-aaaaaa")
    store, index = MemoryStore(record), MemoryIndex()
    app = application(store, index)
    app.show(record.id)
    assert index.lookups and index.epochs == 1

    def forbidden(path: str, text: str) -> Parsed | None:
        raise AssertionError("second read parsed a cached file")

    monkeypatch.setattr(core, "parse_file", forbidden)
    app.show(record.id)
    assert index.epochs == 2


def test_gate_uses_only_parses_keyed_by_read_bytes() -> None:
    record = decision(id="d-aaaaaa")
    store, index = MemoryStore(record, staged=True), MemoryIndex()
    tree, _ = store.trees()
    path = next(iter(tree.files))
    index.values[(path, tree.blobs[path])] = record
    store.files[path] = store.files[path].replace(record.statement, "A forbidden hand edit.")
    without = application(store, None).check(gate=True)
    with_index = application(store, index).check(gate=True)
    assert with_index == without and with_index[0].problems
    assert index.lookups and len(index.values) > 1


@pytest.mark.parametrize("variant", ["clean", "changed", "broken", "stray"])
def test_read_output_same_with_and_without_index(variant: str) -> None:
    record, spec = decision(id="d-aaaaaa"), entry(id="s-aaaaaa")
    store = MemoryStore(record, spec, area(order=(spec.id,)), staged=True)
    if variant == "changed":
        store.files.update(MemoryStore(replace(record, title="Changed")).files)
    elif variant == "broken":
        store.files["lodge/decisions/d-bbbbbb-broken.md"] = "broken"
    elif variant == "stray":
        store.files["lodge/notes.txt"] = "a stray file"
    index = MemoryIndex()
    before, after = application(store, None), application(store, index)
    for _ in range(2):
        assert after.show(record.id, True, True) == before.show(record.id, True, True)
        assert after.search("statement", Filters()) == before.search("statement", Filters())
        assert after.waiting_all() == before.waiting_all()
        assert after.check(gate=True) == before.check(gate=True)
    assert index.lookups and index.values


@pytest.mark.parametrize("operation", ["draft", "mint", "add", "ask", "behind", "confirm"])
def test_every_app_snapshot_uses_cache(operation: str, monkeypatch: pytest.MonkeyPatch) -> None:
    record, spec = decision(id="d-aaaaaa"), entry(id="s-aaaaaa")
    store = MemoryStore(record, spec, area(order=(spec.id,)), staged=True)
    index = MemoryIndex()
    app = application(store, index)
    draft = app.draft(record.id)
    app.show(record.id)
    lookups = index.lookups

    # A direct load bypasses the shared cache, even for a newly derived, unkeyed tree.
    def forbidden(tree: core.Tree) -> core.Snapshot:
        raise AssertionError("snapshot bypassed the parse cache")

    monkeypatch.setattr(core, "load", forbidden)
    monkeypatch.setattr(state, "load", forbidden)
    if operation == "draft":
        app.draft(record.id)
    elif operation == "mint":
        app.mint("d")
    elif operation == "add":
        app.add([("draft", draft)], dry_run=True)
    elif operation == "ask":
        app.ask(record.id, Raises.QUESTION, "builder", "Which berth?")
    elif operation == "behind":
        app.behind_area(spec.area)
    else:
        app.confirm([record.id], "Read.")
    assert index.lookups > lookups


def test_gate_caches_each_exact_tree(monkeypatch: pytest.MonkeyPatch) -> None:
    record = decision(id="d-aaaaaa")
    store, index = MemoryStore(record, staged=True), MemoryIndex()
    old = MemoryStore(replace(record, title="Earlier title"))
    extra = MemoryStore(replace(record, statement="A forbidden hand edit."))
    published, checked = old.trees()[0], extra.trees()[0]
    store.gate_for = Gate(published, (("staged", checked),))
    app = application(store, index)
    without = application(store, None).check(gate=True)
    assert app.check(gate=True) == without
    keys = {(p, b) for tree in (published, checked) for p, b in tree.blobs.items()}
    assert keys <= index.values.keys()

    def forbidden(path: str, text: str) -> Parsed | None:
        raise AssertionError("gate reparsed a cached exact tree")

    monkeypatch.setattr(core, "parse_file", forbidden)
    assert app.check(gate=True) == without
