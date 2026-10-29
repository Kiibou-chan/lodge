from typing import Any

from builders import at, decision
from checks import NOW, SETTINGS, SPEC, published, state

from lodge.core import Action, Change, Decision, check_change


def edits(**kw: Any) -> Decision:
    return decision(changes=(Change(SPEC, Action.EDIT),), **kw)


def test_new_decision_must_be_after_an_unpublished_one_it_shares_an_entry_with() -> None:
    unpublished = edits(id="d-bbbbbb", date=at(10))
    current = state(unpublished)
    tie = edits(id="d-cccccc", date=at(10))
    result = check_change(published(), state(unpublished, tie), SETTINGS, NOW, current)
    assert [(p.check, p.message) for p in result.problems] == [
        (1, f"d-cccccc: dated {at(10)}, no later than d-bbbbbb, which shares {SPEC} with it")
    ]


def test_new_decision_after_an_unpublished_one_passes() -> None:
    unpublished = edits(id="d-bbbbbb", date=at(10))
    later = edits(id="d-cccccc", date=at(11))
    after = state(unpublished, later)
    assert check_change(published(), after, SETTINGS, NOW, state(unpublished)).ok


def test_without_the_current_state_only_published_decisions_count() -> None:
    unpublished = edits(id="d-bbbbbb", date=at(10))
    tie = edits(id="d-cccccc", date=at(10))
    assert check_change(published(), state(unpublished, tie), SETTINGS, NOW).ok


def test_an_unpublished_decision_is_not_held_to_a_newer_one() -> None:
    older = edits(id="d-bbbbbb", date=at(10))
    newer = edits(id="d-cccccc", date=at(11))
    third = edits(id="d-dddddd", date=at(12))
    current = state(older, newer)
    assert check_change(published(), state(older, newer, third), SETTINGS, NOW, current).ok
