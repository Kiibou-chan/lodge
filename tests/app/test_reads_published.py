"""Reads run checks 4, 5, and 6 against the published state too (LODGE-9)."""

from builders import at, decision
from fakes import MemoryStore
from support import AREA, ENTRY, FIRST, wired

from lodge.app import Lodge
from lodge.core import Action, Change, Filters


def _statement_edited() -> MemoryStore:
    store = MemoryStore(AREA, ENTRY, FIRST, staged=True)
    path = next(p for p in store.files if "d-aaaaaa" in p)
    old = FIRST.statement
    assert old in store.files[path]
    store.files[path] = store.files[path].replace(old, "Transcripts are deleted after a day.")
    return store


def test_show_flags_a_hand_edited_published_decision() -> None:
    shown = wired(_statement_edited()).show("ITEM-1")
    assert "fails check" in shown.level1.flags


def test_search_and_timeline_flag_it_too() -> None:
    lodge = wired(_statement_edited())
    found = lodge.search("deleted", Filters()).items
    assert [v.id for v in found] == ["d-aaaaaa"] and "fails check" in found[0].flags
    assert "fails check" in lodge.timeline().items[0].flags


def test_plain_check_lists_the_problem_and_fails() -> None:
    result, _ = wired(_statement_edited()).problems()
    assert [p.check for p in result.problems] == [5]
    assert not result.ok


def test_gate_still_reports_it_once() -> None:
    result, _ = wired(_statement_edited()).check(gate=True)
    assert [p.check for p in result.problems] == [5]


def test_an_unedited_published_state_reads_clean() -> None:
    lodge = wired(MemoryStore(AREA, ENTRY, FIRST, staged=True))
    assert "fails check" not in lodge.show("ITEM-1").level1.flags
    assert lodge.problems()[0].ok


def test_a_shrunk_agent_reasoning_fails_on_a_read() -> None:
    agent = decision(
        id="d-bbbbbb",
        title="Reword",
        reasoning="one two three four five",
        changes=(Change("s-aaaaaa", Action.EDIT),),
        date=at(10),
    )
    store = MemoryStore(AREA, ENTRY, FIRST, agent, staged=True)
    path = next(p for p in store.files if "d-bbbbbb" in p)
    store.files[path] = store.files[path].replace("one two three four five", "one two")
    lodge: Lodge = wired(store)
    assert "fails check" in lodge.show("d-bbbbbb").level1.flags
    assert [p.check for p in lodge.problems()[0].problems] == [5]
