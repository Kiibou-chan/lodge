"""Published statuses, minimal facts, and the boundary of exact readers."""

from dataclasses import fields, replace
from unittest.mock import patch

import pytest
from builders import at, decision, files_of
from fakes import MemoryIndex, MemoryStore
from indexed_support import app, printed, seed
from support import FIRST, project
from test_published_facts import build, changed, published_facts

from lodge import core
from lodge.app import StateFacts, StoredState


@pytest.mark.parametrize("code", ["d-x", "S-1"])
@pytest.mark.parametrize("ambiguous", [False, True])
def test_id_shaped_codes_match_memory(code: str, ambiguous: bool) -> None:
    root = replace(FIRST, code=code)
    others = (decision(id="d-bbbbbb", code=code),) if ambiguous else ()
    store, index = MemoryStore(root, *others), MemoryIndex()
    seed(store, index)
    with patch.object(core, "assemble", side_effect=AssertionError("cached read fell back")):
        actual = printed(app(store, index), ["show", code])
    assert actual == printed(app(store), ["show", code])


def test_published_statuses_differ_from_current() -> None:
    replacement = decision(id="d-bbbbbb", replaces=(FIRST.id,), date=at(1))
    store = MemoryStore(FIRST, replacement, staged=True)
    ident, facts = published_facts(store)
    path = next(p for p in store.files if replacement.id in p)
    del store.files[path]
    addition = decision(id="d-cccccc", narrows=(FIRST.id,), date=at(2))
    store.files.update(files_of(addition))
    full = build(store, MemoryIndex())
    assert facts.status[FIRST.id] == "replaced"
    assert full.derived.status[FIRST.id] == "current"
    assert any(p.check == 6 and "which is replaced" in p.message for p in full.result.problems)
    index = MemoryIndex()
    index.fact_values[ident] = facts
    assert build(store, index).result == full.result


def test_facts_store_only_published_statuses() -> None:
    store, index = project(True), MemoryIndex()
    changed(store, "new logs")
    current, published = store.identities()
    with patch.object(core, "check_state", wraps=core.check_state) as check:
        printed(app(store, index), ["show", FIRST.id])
    assert current != published
    assert set(index.fact_values) == {published}
    assert check.call_count == 1
    assert [f.name for f in fields(StateFacts)] == ["status"]


def test_stored_threads_are_required() -> None:
    store, index = project(True), MemoryIndex()
    seed(store, index)
    values = vars(next(iter(index.states.values()))).copy()
    values.pop("threads")
    with pytest.raises(TypeError, match="threads"):
        StoredState(**values)


@pytest.mark.parametrize("args", [["check"], ["check", "--gate"], ["spec"], ["add"]])
def test_exact_commands_ignore_poisoned_facts(args: list[str]) -> None:
    store, index = project(True), MemoryIndex()
    ident, facts = published_facts(store)
    index.fact_values[ident] = replace(facts, status={i: "retired" for i in facts.status})
    changed(store, "new logs")
    if args == ["add"]:
        draft = (
            "---\nkind: decision\ntitle: Synthetic change\nscope: product\n"
            "decided_by: coordinator\n---\n\nBerths hold cranes.\n"
        )
        drafts = [("synthetic.md", draft)]
        expected_add = app(store).add(drafts, dry_run=True)
        with patch.object(index, "facts", side_effect=AssertionError("exact reader used facts")):
            assert app(store, index).add(drafts, dry_run=True) == expected_add
    else:
        expected = printed(app(store), args)
        with patch.object(index, "facts", side_effect=AssertionError("exact reader used facts")):
            assert printed(app(store, index), args) == expected
