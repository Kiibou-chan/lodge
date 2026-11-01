"""Exact reads may reuse only parses keyed by the bytes they actually read."""

from dataclasses import replace
from pathlib import Path

import pytest
from builders import area, decision, entry
from fakes import CountingIds, FixedClock, MemoryIndex, MemoryStore

from lodge import core
from lodge.app import Gate, Lodge, state
from lodge.core import CoreSettings, Filters, Parsed, Raises
from lodge.gitstore import open_index


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


@pytest.mark.parametrize("operation", ["show", "gate", "add"])
def test_surrogate_path_with_real_index(tmp_path: Path, operation: str) -> None:
    record = decision(id="d-aaaaaa")
    store = MemoryStore(record, staged=True)
    store.files["lodge/decisions/stray-\udcff.md"] = "broken"
    index = open_index(tmp_path, "settings")
    assert index is not None
    before = application(store, None)
    after = Lodge(store, FixedClock(), CountingIds(), CoreSettings(), index=index)
    draft = before.draft(record.id)
    if operation == "show":
        assert after.show(record.id) == before.show(record.id)
    elif operation == "gate":
        assert after.check(gate=True) == before.check(gate=True)
    else:
        assert after.add([("draft", draft)], dry_run=True) == before.add(
            [("draft", draft)], dry_run=True
        )
    tree = store.trees()[0]
    path = next(p for p in tree.files if "stray" not in p)
    assert (path, tree.blobs[path]) in index.parses([(path, tree.blobs[path])])
    index.close()


@pytest.mark.parametrize("operation", ["add", "ask", "reply", "close"])
def test_derived_tree_parses_only_changed_files(
    operation: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    record = decision(id="d-aaaaaa")
    store, index = MemoryStore(record, staged=True), MemoryIndex()
    app = application(store, index)
    draft = app.draft(record.id)
    asked = app.ask(record.id, Raises.QUESTION, "builder", "Which berth?")
    app.show(record.id)
    original = core.parse_file
    parsed: list[str] = []

    def spy(path: str, text: str) -> Parsed | None:
        parsed.append(path)
        return original(path, text)

    monkeypatch.setattr(core, "parse_file", spy)
    if operation == "add":
        app.add([("draft", draft)], dry_run=True)
    elif operation == "ask":
        app.ask(record.id, Raises.QUESTION, "builder", "Which crane?")
    elif operation == "reply":
        app.reply(asked.ids[0], "builder", "Berth one.")
    else:
        app.close(asked.ids[0], "builder", "Resolved.")
    assert all(p.startswith("lodge/threads/") for p in parsed), parsed
    assert len(parsed) <= 1


def test_checked_read_looks_up_shared_keys_once(monkeypatch: pytest.MonkeyPatch) -> None:
    one, two = decision(id="d-aaaaaa"), decision(id="d-bbbbbb")
    store, index = MemoryStore(one, two, staged=True), MemoryIndex()
    store.files.update(MemoryStore(replace(two, title="Changed")).files)
    seen: list[tuple[str, str]] = []
    original = index.parses

    def spy(keys: tuple[tuple[str, str], ...]) -> dict[tuple[str, str], Parsed | None]:
        seen.extend(keys)
        return original(keys)

    monkeypatch.setattr(index, "parses", spy)
    application(store, index).show(one.id)
    assert len(seen) == len(set(seen))


def test_epoch_is_kept_for_the_build() -> None:
    store, index = MemoryStore(decision()), MemoryIndex()
    built = state.read_state(store, index)
    assert built.epoch == 1 and index.epochs == 1
