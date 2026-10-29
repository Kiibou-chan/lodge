"""Checks 5 and 6: published decisions are not rewritten, and replaced records stay replaced."""

from dataclasses import replace
from typing import Any

import pytest
from builders import area, at, decision
from checks import (
    LATER,
    NOTES,
    OLD,
    REMEDY_CHECK_5,
    SPEC,
    Item,
    check,
    creates,
    old_decision,
    published,
    state,
    verdict,
)

from lodge.core import (
    Action,
    Change,
    Decision,
    NumberHandle,
    Quote,
    Scope,
)

HEADER_EDITS: dict[str, Any] = {
    "title": "Another title",
    "scope": Scope.PROCESS,
    "decided_by": "coordinator",
    "date": at(99),
    "code": "NEW-1",
    "changes": (Change(SPEC, Action.CREATE), Change(SPEC, Action.EDIT)),
    "replaces": ("d-bbbbbb",),
    "narrows": ("d-bbbbbb",),
    "confirms": ("d-bbbbbb",),
    "work_item": "plans/x.md",
    "quote": Quote("Other.", "a session", "2026-10-28 10:00"),
    "numbers": (NumberHandle("3", "a command"),),
    "attachments": ("d-aaaaaa/run.log",),
    "imported_from": NOTES,
}


@pytest.mark.parametrize("field", list(HEADER_EDITS))
def test_check_5_header_key_of_a_published_decision_changed(field: str) -> None:
    edited = replace(old_decision(), **{field: HEADER_EDITS[field]})
    found = verdict(published(), state(edited))
    assert (
        5,
        f"d-aaaaaa: {field} of a published decision was changed" + REMEDY_CHECK_5,
    ) in found


def test_check_5_statement_changed() -> None:
    edited = replace(old_decision(), statement="Another statement.")
    assert (
        5,
        "d-aaaaaa: statement of a published decision was changed" + REMEDY_CHECK_5,
    ) in verdict(published(), state(edited))


def test_author_reasoning_edit_fails() -> None:
    before = state(replace(old_decision(), reasoning="Because it is so."))
    after = state(replace(old_decision(), reasoning="Because it was so."))
    assert verdict(before, after) == [
        (
            5,
            "d-aaaaaa: reasoning of a published author decision was changed" + REMEDY_CHECK_5,
        )
    ]


def agent(reasoning: str) -> Decision:
    return creates(SPEC, id=OLD, date=at(0), reasoning=reasoning)


@pytest.mark.parametrize(
    ("before", "after"),
    [
        ("Two words", "Now three words"),
        ("Now three words", "Two words"),
        ("one two three four five six", "six five four three two one"),
        ("Two\nwords", "Two   words"),
    ],
    ids=["grew", "shrank", "reworded", "reflowed"],
)
def test_check_5_agent_reasoning_changed_in_any_way_fails(before: str, after: str) -> None:
    assert verdict(state(agent(before)), state(agent(after))) == [
        (
            5,
            "d-aaaaaa: reasoning of a published agent decision was changed" + REMEDY_CHECK_5,
        )
    ]


def test_check_5_agent_reasoning_unchanged_passes() -> None:
    result = check(state(agent("Two words")), state(agent("Two words")))
    assert result.ok and result.notes == ()


def test_check_5_author_reasoning_reflowed_fails() -> None:
    before = state(replace(old_decision(), reasoning="Two\nwords"))
    after = state(replace(old_decision(), reasoning="Two words"))
    assert verdict(before, after) == [
        (
            5,
            "d-aaaaaa: reasoning of a published author decision was changed" + REMEDY_CHECK_5,
        )
    ]


def test_check_5_new_decisions_are_not_compared() -> None:
    new = decision(id="d-bbbbbb", date=LATER, reasoning="Long enough to be a few words.")
    assert verdict(published(), state(new)) == []


def retired_and_replaced() -> list[Item]:
    retire = decision(id="d-cccccc", date=at(2), changes=(Change(SPEC, Action.RETIRE),))
    newer = decision(id="d-bbbbbb", date=at(1), replaces=(OLD,))
    return [newer, retire, area(order=())]


@pytest.mark.parametrize("verb", ["narrows", "confirms"])
def test_check_6_new_decision_links_to_a_replaced_decision(verb: str) -> None:
    before = state(*retired_and_replaced())
    new = decision(id="d-dddddd", date=LATER, decided_by="author", **{verb: (OLD,)})
    found = verdict(before, state(*retired_and_replaced(), new))
    assert found == [(6, f"d-dddddd: {verb} {OLD}, which is replaced")]


def test_replacing_a_decision_passes_check_6() -> None:
    before = state(*retired_and_replaced())
    new = decision(id="d-dddddd", date=LATER, replaces=(OLD,))
    assert verdict(before, state(*retired_and_replaced(), new)) == []


def test_check_6_new_decision_changes_a_retired_entry() -> None:
    before = state(*retired_and_replaced())
    new = decision(id="d-dddddd", date=LATER, changes=(Change(SPEC, Action.EDIT),))
    found = verdict(before, state(*retired_and_replaced(), new))
    assert (6, "d-dddddd: changes s-aaaaaa with action edit, but the entry is retired") in found


def test_check_6_retiring_a_retired_entry_passes() -> None:
    before = state(*retired_and_replaced())
    new = decision(id="d-dddddd", date=LATER, changes=(Change(SPEC, Action.RETIRE),))
    assert verdict(before, state(*retired_and_replaced(), new)) == []


def test_check_6_older_records_keep_their_links() -> None:
    old_link = decision(id="d-eeeeee", date=at(3), narrows=(OLD,))
    before = state(*retired_and_replaced(), old_link)
    assert verdict(before, before) == []
