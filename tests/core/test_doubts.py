"""Doubts propagate through specification dependencies, questions stay local."""

from collections.abc import Mapping

from builders import at, decision, entry, snapshot_of, thread

from lodge.core import (
    Action,
    Change,
    Decision,
    Imported,
    Raises,
    SpecEntry,
    Thread,
    ThreadState,
    derive,
    level1,
)


def marks(*items: Decision | SpecEntry | Thread) -> Mapping[str, tuple[str, ...]]:
    return derive(snapshot_of(*items)).doubts


def test_open_doubt_marks_its_record() -> None:
    e = entry()
    assert marks(e, thread(about=e.id))[e.id] == ("in doubt",)


def test_closed_doubt_marks_nothing() -> None:
    e = entry()
    assert not marks(e, thread(about=e.id, state=ThreadState.CLOSED))


def test_question_open_mark_and_no_propagation() -> None:
    a = entry()
    b = entry(rests_on=(a.id,))
    assert marks(a, b, thread(about=a.id, raises=Raises.QUESTION)) == {a.id: ("question open",)}


def chain() -> tuple[SpecEntry, SpecEntry, SpecEntry]:
    a = entry()
    b = entry(rests_on=(a.id,))
    c = entry(rests_on=(b.id,))
    return a, b, c


def test_doubt_reaches_entries_resting_on_it_further_down() -> None:
    a, b, c = chain()
    m = marks(a, b, c, thread(about=a.id))
    assert m[b.id] == m[c.id] == (f"rests on {a.id}, in doubt",)


def test_doubt_on_decision_marks_entries_it_created_and_last_changed() -> None:
    a, b, c = chain()
    d = decision(changes=(Change(a.id, Action.CREATE), Change(b.id, Action.EDIT)))
    old = entry(rests_on=())
    d = decision(id=d.id, changes=(*d.changes, Change(old.id, Action.EDIT)), date=at(0))
    later = decision(changes=(Change(old.id, Action.EDIT),), date=at(1))
    m = marks(a, b, c, old, d, later, thread(about=d.id))
    assert old.id not in m
    assert f"changed by {d.id}, in doubt" in m[a.id]
    assert f"changed by {d.id}, in doubt" in m[b.id]


def test_doubt_on_decision_reaches_what_rests_on_its_entries() -> None:
    a, b, c = chain()
    d = decision(changes=(Change(a.id, Action.CREATE),))
    assert marks(a, b, c, d, thread(about=d.id))[c.id] == (f"rests on {a.id}, in doubt",)


def test_cycle_of_rests_on_does_not_hang() -> None:
    a = entry(id="s-aaaaaa", rests_on=("s-bbbbbb",))
    b = entry(id="s-bbbbbb", rests_on=(a.id,))
    m = marks(a, b, thread(about=a.id))
    assert m[b.id] == (f"rests on {a.id}, in doubt",)


def test_confirmed_decision_shows_confirmation_and_keeps_decided_by() -> None:
    a = decision()
    b = decision(id="d-bbbbbb", decided_by="author", confirms=(a.id,))
    s = snapshot_of(a, b)
    v = level1(s, derive(s), a.id, frozenset())
    assert "confirmed by the author (d-bbbbbb)" in v.flags
    assert v.decided_by == "coordinator"


def test_flag_order() -> None:
    a = entry()
    b = entry(rests_on=(a.id,), imported_from=Imported("storage.md", "Storage"))
    first = decision(decided_by="author", changes=(Change(b.id, Action.CREATE),), date=at(0))
    edit = decision(changes=(Change(b.id, Action.EDIT), Change(a.id, Action.RETIRE)), date=at(1))
    s = snapshot_of(a, b, first, edit, thread(about=b.id))
    assert level1(s, derive(s), b.id, frozenset()).flags == (
        f"awaiting the author on {edit.id}",
        "in doubt",
        f"rests on {a.id}, retired",
        "imported",
    )
