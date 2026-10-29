from datetime import datetime, timedelta

from applying import decision_text
from builders import at
from fakes import START, FixedClock, MemoryStore
from support import FIRST, project, wired

from lodge.app import AddOutcome
from lodge.core import Tree, load

NEWEST = datetime.fromisoformat(FIRST.date)


def edit(store: MemoryStore, statement: str) -> list[tuple[str, str]]:
    """A decision editing `s-aaaaaa`, and the entry draft with `statement`."""
    changes = decision_text("changes:", "  - {entry: s-aaaaaa, action: edit}", body="Edited.")
    held = wired(store).draft("s-aaaaaa").replace("Held.", statement)
    return [("d.md", changes), ("s.md", held)]


def dated(store: MemoryStore) -> list[str]:
    return sorted(d.date for d in load(Tree(None, store.files)).decisions.values())


def test_add_in_the_second_of_the_newest_decision_waits_for_the_next() -> None:
    store = project()
    clock = FixedClock(NEWEST)
    added = wired(store, clock).add(edit(store, "Held, whole."))
    assert added.outcome is AddOutcome.PUBLISHED
    assert clock.slept == [1.0]
    assert dated(store) == [at(0), "2026-10-28T10:00:01+01:00"]


def test_add_sleeps_to_the_next_whole_second() -> None:
    store = project()
    clock = FixedClock(NEWEST + timedelta(microseconds=400_000))
    wired(store, clock).add(edit(store, "Held, whole."))
    assert clock.slept == [0.6]


def test_add_after_the_newest_second_does_not_wait() -> None:
    store = project()
    clock = FixedClock(START)
    added = wired(store, clock).add(edit(store, "Held, whole."))
    assert added.outcome is AddOutcome.PUBLISHED
    assert clock.slept == [] and clock.calls == 1


def test_two_adds_in_one_second_are_dated_a_second_apart() -> None:
    store = project(staged=True)
    clock = FixedClock(START)
    wired(store, clock).add(edit(store, "Held, whole."))
    added = wired(store, clock).add(edit(store, "Held, compressed."))
    assert added.outcome is AddOutcome.STAGED
    assert clock.slept == [1.0]
    assert dated(store)[1:] == ["2026-10-29T09:30:00+01:00", "2026-10-29T09:30:01+01:00"]


def test_a_decision_far_ahead_of_the_clock_is_not_waited_for() -> None:
    store = project()
    clock = FixedClock(NEWEST - timedelta(days=1))
    added = wired(store, clock).add(edit(store, "Held, whole."))
    assert added.outcome is AddOutcome.CHECK_FAILED
    assert clock.slept == []


def test_a_decision_a_few_seconds_ahead_of_the_clock_is_waited_for() -> None:
    store = project()
    clock = FixedClock(NEWEST - timedelta(seconds=2))
    added = wired(store, clock).add(edit(store, "Held, whole."))
    assert added.outcome is AddOutcome.PUBLISHED
    assert len(clock.slept) == 3
