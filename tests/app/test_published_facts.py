"""Published facts replace only derivation and one-state checks, never snapshots or comparisons."""

from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import pytest
from builders import decision, files_of
from builders import entry as make_entry
from fakes import CountingIds, FixedClock, MemoryIndex, MemoryStore
from indexed_support import app, printed
from support import AREA, ENTRY, FIRST, project

from lodge import core
from lodge.app import StateFacts, indexed, read_model
from lodge.app.state import State, Wiring
from lodge.gitstore import open_index


def build(store: MemoryStore, index: MemoryIndex) -> State:
    store.identities()
    return indexed._built(
        Wiring(store, FixedClock(), CountingIds(), core.CoreSettings(), index),
        FixedClock().now(),
        index.epoch(),
    )[0]


def published_facts(store: MemoryStore) -> tuple[str, StateFacts]:
    ident = store.identities()[1]
    snapshot = core.load(store.trees()[1])
    derived = core.derive(snapshot)
    return ident, StateFacts(derived.status, core.check_state(snapshot, derived=derived).problems)


def changed(store: MemoryStore, text: str) -> None:
    path = next(p for p in store.files if FIRST.id in p)
    record = core.parse_file(path, store.published[path])
    assert isinstance(record, core.Decision)
    store.files[path] = core.write_record(replace(record, reasoning=f"Because they are {text}."))


def problematic(case: str) -> tuple[MemoryStore, str]:
    root = FIRST
    other = decision(id="d-bbbbbb", code="OTHER")
    selected: core.Decision | core.SpecEntry = root
    area, entry = AREA, ENTRY
    extra: tuple[core.SpecEntry, ...] = ()
    if case == "duplicate_code":
        root, other = replace(root, code="DUPE"), replace(other, code="DUPE")
    elif case == "hand_edited":
        root = replace(root, narrows=("d-yyyyyy",))
    elif case == "out_of_order":
        area = replace(AREA, order=())
        selected = entry
    else:
        peer = make_entry(id="s-bbbbbb", rests_on=(ENTRY.id,))
        entry = replace(ENTRY, rests_on=(peer.id,))
        area = replace(AREA, order=(entry.id, peer.id))
        selected, extra = entry, (peer,)
    store = MemoryStore(area, entry, root, other, *extra, staged=True)
    edited: core.Decision | core.SpecEntry
    if isinstance(selected, core.SpecEntry):
        edited = replace(entry, rests_on=(*entry.rests_on, "s-zzzzzz"))
    else:
        edited = replace(root, confirms=("d-zzzzzz",), statement="A hand-edited statement.")
    path = next(p for p in store.files if edited.id in p)
    store.files[path] = next(iter(files_of(edited).values()))
    return store, path


@pytest.mark.parametrize("case", ["duplicate_code", "hand_edited", "out_of_order", "cycle"])
def test_published_facts_equal_full(case: str) -> None:
    store, path = problematic(case)
    ident, facts = published_facts(store)
    assert any(p.path == path for p in facts.problems)
    full = build(store, MemoryIndex())
    assert any(
        p.path == path
        and (p.path, p.check, p.message)
        not in {(q.path, q.check, q.message) for q in facts.problems}
        for p in full.result.problems
    )
    index = MemoryIndex()
    # Problem identity excludes source lines, exactly as core's sort keys do.
    index.fact_values[ident] = replace(
        facts, problems=tuple(replace(p, line=99) for p in facts.problems)
    )
    with (
        patch.object(core, "derive", wraps=core.derive) as derive,
        patch.object(core, "check_state", wraps=core.check_state) as check,
        patch.object(core, "check_change", wraps=core.check_change) as compare,
    ):
        cached = build(store, index)
    assert cached.result == full.result
    assert cached.read == full.read and cached.failing == full.failing
    assert cached.published_state is not None and full.published_state is not None
    assert cached.published_state.snapshot == full.published_state.snapshot
    assert derive.call_count == check.call_count == compare.call_count == 1


def test_facts_keyed_by_ident_alone() -> None:
    store, index = project(True), MemoryIndex()
    ident, facts = published_facts(store)
    index.fact_values[ident] = facts
    with patch.object(index, "facts", wraps=index.facts) as lookup:
        for text in ("first logs", "second logs"):
            changed(store, text)
            for _ in range(2):
                printed(app(store, index), ["show", FIRST.id])
    assert len(index.states) == 2
    assert {s.published for s in index.states.values()} == {ident}
    assert lookup.call_count == 4 and all(c.args == (ident,) for c in lookup.call_args_list)
    assert index.fact_values[ident] is facts


def test_absent_facts_are_computed_and_kept() -> None:
    store, index = project(True), MemoryIndex()
    ident, expected = published_facts(store)
    changed(store, "first logs")
    printed(app(store, index), ["show", FIRST.id])
    assert index.facts(ident) == expected
    with patch.object(core, "derive", wraps=core.derive) as derive:
        printed(app(store, index), ["show", FIRST.id])
    assert derive.call_count == 1 and len(index.states) == 1
    first = next(iter(index.states))
    for n in range(5):
        changed(store, f"new logs {n}")
        for _ in range(2):
            printed(app(store, index), ["show", FIRST.id])
    assert first not in index.states and index.facts(ident) == expected
    assert all(index.facts(s.current) is not None for s in index.states.values())


def test_facts_written_on_the_first_read() -> None:
    store, index = project(True), MemoryIndex()
    ident, expected = published_facts(store)
    changed(store, "first logs")
    expected_output = printed(app(store), ["show", FIRST.id])
    with patch.object(core, "derive", wraps=core.derive) as derive:
        assert printed(app(store, index), ["show", FIRST.id]) == expected_output
    assert derive.call_count == 2 and not index.states
    assert index.facts(ident) == expected
    current = store.identities()[0]
    current_snapshot = core.load(store.trees()[0])
    own = core.derive(current_snapshot)
    assert index.facts(current) == StateFacts(
        own.status, core.check_state(current_snapshot, derived=own).problems
    )
    changed(store, "second logs")
    expected_output = printed(app(store), ["show", FIRST.id])
    with patch.object(core, "derive", wraps=core.derive) as derive:
        assert printed(app(store, index), ["show", FIRST.id]) == expected_output
    assert derive.call_count == 1 and not index.states


def test_other_published_ident_reads_other_facts() -> None:
    store, index = project(True), MemoryIndex()
    old, old_facts = published_facts(store)
    index.fact_values[old] = old_facts
    changed(store, "accepted logs")
    # A new accepted commit moves the fake store's published tree.
    store.published = dict(store.files)
    store.rev += 1
    new, expected = published_facts(store)
    assert new != old
    changed(store, "different current logs")
    with (
        patch.object(index, "facts", wraps=index.facts) as lookup,
        patch.object(core, "derive", wraps=core.derive) as derive,
    ):
        printed(app(store, index), ["show", FIRST.id])
    assert lookup.call_args_list and all(c.args == (new,) for c in lookup.call_args_list)
    assert derive.call_count == 2
    assert index.facts(new) == expected and index.facts(old) is old_facts


@pytest.mark.parametrize("writer", ["marker", "keep"])
def test_used_facts_are_carried_through_a_clear(
    writer: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    store, index = project(True), MemoryIndex()
    ident, facts = published_facts(store)
    index.fact_values[ident] = facts
    changed(store, "new logs")
    if writer == "keep":
        printed(app(store, index), ["show", FIRST.id])
    original = index.mark_seen if writer == "marker" else index.keep_state

    def cleared(*args: object, **kwargs: object) -> None:
        index.fact_values.clear()
        original(*args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(index, "mark_seen" if writer == "marker" else "keep_state", cleared)
    with patch.object(core, "derive", wraps=core.derive) as derive:
        printed(app(store, index), ["show", FIRST.id])
    assert derive.call_count == 1
    assert index.facts(ident) == facts


def test_invalid_status_is_a_miss() -> None:
    store, index = project(True), MemoryIndex()
    changed(store, "new logs")
    state = build(store, index)
    assert read_model.change_facts_of(state, StateFacts({FIRST.id: "invalid"}, ())) is None
    ident, _ = published_facts(store)
    index.fact_values[ident] = StateFacts({FIRST.id: "invalid"}, ())
    with patch.object(core, "derive", wraps=core.derive) as derive:
        rebuilt = build(store, index)
    assert rebuilt.result == state.result and derive.call_count == 2


@pytest.mark.parametrize("damage", ["missing", "extra"])
def test_incomplete_status_facts_are_a_miss(damage: str) -> None:
    store, index = project(True), MemoryIndex()
    ident, facts = published_facts(store)
    status = dict(facts.status)
    if damage == "missing":
        status.pop(ENTRY.id)
    else:
        status["d-zzzzzz"] = "current"
    index.fact_values[ident] = replace(facts, status=status)
    changed(store, "new logs")
    expected = build(store, MemoryIndex())
    with patch.object(core, "derive", wraps=core.derive) as derive:
        rebuilt = build(store, index)
    assert rebuilt.result == expected.result and derive.call_count == 2


def test_unencodable_facts_do_not_discard_parses(tmp_path: Path) -> None:
    index = open_index(tmp_path)
    assert index is not None
    key = ("lodge/decisions/d-aaaaaa-synthetic.md", "blob")
    fact = StateFacts({FIRST.id: "current"}, ())
    index.mark_seen("marker", {key: None}, {"bad\udcff": fact, "good": fact}, files=1)
    assert index.parses([key]) == {key: None}
    assert index.facts("good") == fact and index.facts("bad\udcff") is None
    assert index.seen("marker")
    index.close()
