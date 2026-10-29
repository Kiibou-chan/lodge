from dataclasses import replace

import pytest
from builders import area, at, decision, entry
from checks import (
    LATER,
    NOTES,
    OLD,
    REMEDY_CHECK_4,
    SPEC,
    Item,
    creates,
    published,
    state,
    verdict,
)

from lodge.core import (
    Action,
    Change,
    Imported,
)

NEW = "s-bbbbbb"
NEW_AREA = area(order=(SPEC, NEW))


def test_check_4_new_entry_without_a_decision() -> None:
    assert verdict(published(), state(entry(id=NEW), NEW_AREA)) == [
        (
            4,
            "s-bbbbbb: created, but no new decision in this change lists it with action create"
            + REMEDY_CHECK_4,
        )
    ]


def test_check_4_new_entry_listed_with_the_wrong_action() -> None:
    wrong = decision(id="d-bbbbbb", date=LATER, changes=(Change(NEW, Action.EDIT),))
    found = verdict(published(), state(entry(id=NEW), NEW_AREA, wrong))
    assert [c for c, _ in found] == [4]


def test_check_4_published_decision_does_not_count() -> None:
    early = creates(NEW, id="d-bbbbbb", date=at(1))
    before = state(early)
    found = verdict(before, state(early, entry(id=NEW), NEW_AREA))
    assert [c for c, _ in found] == [4]


@pytest.mark.parametrize("field", ["title", "statement", "code"])
def test_check_4_edited_entry_without_a_decision(field: str) -> None:
    changed = replace(entry(id=SPEC), **{field: "Something else"})  # type: ignore[arg-type]
    assert verdict(published(), state(changed)) == [
        (
            4,
            "s-aaaaaa: edited, but no new decision in this change lists it with action edit"
            + REMEDY_CHECK_4,
        )
    ]


def test_check_4_edited_entry_with_a_decision_passes() -> None:
    edit = decision(id="d-bbbbbb", date=LATER, changes=(Change(SPEC, Action.EDIT),))
    assert verdict(published(), state(entry(id=SPEC, statement="Now this."), edit)) == []


def test_check_4_retired_entry_without_a_retiring_decision() -> None:
    both = decision(
        id=OLD,
        date=at(0),
        decided_by="author",
        changes=(
            Change(SPEC, Action.CREATE),
            Change(SPEC, Action.RETIRE),
        ),
    )
    found = verdict(published(), state(both, area(order=())))
    assert (
        4,
        "s-aaaaaa: retired, but no new decision in this change lists it with action retire"
        + REMEDY_CHECK_4,
    ) in found


def test_check_4_retired_entry_with_a_decision_passes() -> None:
    retire = decision(id="d-bbbbbb", date=LATER, changes=(Change(SPEC, Action.RETIRE),))
    assert verdict(published(), state(retire, area(order=()))) == []


def test_check_4_new_imported_entry_needs_no_decision() -> None:
    assert verdict(published(), state(entry(id=NEW, imported_from=NOTES), NEW_AREA)) == []


def imported_entry_state() -> tuple[Item, ...]:
    return (entry(id=NEW, imported_from=NOTES), NEW_AREA)


def test_check_4_imported_entry_edit_needs_a_decision() -> None:
    before = state(*imported_entry_state())
    edited = entry(id=NEW, imported_from=NOTES, statement="Rewritten by hand.")
    assert verdict(before, state(edited, NEW_AREA)) == [
        (
            4,
            "s-bbbbbb: edited, but no new decision in this change lists it with action edit"
            + REMEDY_CHECK_4,
        )
    ]


def test_check_4_imported_entry_edit_through_an_import_passes() -> None:
    before = state(*imported_entry_state())
    edit = decision(
        id="d-cccccc", date=LATER, changes=(Change(NEW, Action.EDIT),), imported_from=NOTES
    )
    edited = entry(id=NEW, imported_from=NOTES, statement="Re-imported.")
    assert verdict(before, state(edited, NEW_AREA, edit)) == []


def test_check_4_imported_from_added_to_a_live_entry_is_an_edit() -> None:
    laundered = entry(id=SPEC, imported_from=NOTES)
    assert verdict(published(), state(laundered)) == [
        (
            4,
            "s-aaaaaa: edited, but no new decision in this change lists it with action edit"
            + REMEDY_CHECK_4,
        )
    ]


def test_check_4_laundering_over_two_changes_fails_at_each_step() -> None:
    step_one = state(entry(id=SPEC, imported_from=NOTES))
    step_two = state(entry(id=SPEC, imported_from=NOTES, statement="Rewritten."))
    wanted = [
        (
            4,
            "s-aaaaaa: edited, but no new decision in this change lists it with action edit"
            + REMEDY_CHECK_4,
        )
    ]
    assert verdict(published(), step_one) == wanted
    assert verdict(step_one, step_two) == wanted


def test_check_4_imported_from_removed_is_an_edit() -> None:
    before = state(*imported_entry_state())
    assert verdict(before, state(entry(id=NEW), NEW_AREA)) == [
        (
            4,
            "s-bbbbbb: edited, but no new decision in this change lists it with action edit"
            + REMEDY_CHECK_4,
        )
    ]


def test_check_4_entry_moved_to_another_area_is_an_edit() -> None:
    moved = entry(id=SPEC, area="other")
    after = state(moved, area(order=()), area(name="other", order=(SPEC,)))
    assert verdict(published(), after) == [
        (
            4,
            "s-aaaaaa: edited, but no new decision in this change lists it with action edit"
            + REMEDY_CHECK_4,
        )
    ]


def test_check_4_create_for_an_entry_that_exists() -> None:
    again = creates(SPEC, id="d-bbbbbb", date=LATER)
    assert verdict(published(), state(again)) == [
        (4, "d-bbbbbb: lists create for s-aaaaaa, which already exists")
    ]


def test_check_4_import_from_an_unlisted_file() -> None:
    other = Imported("elsewhere.md", "H")
    found = verdict(published(), state(entry(id=NEW, imported_from=other), NEW_AREA))
    assert found == [
        (4, "s-bbbbbb: imported from elsewhere.md, which is not listed in [import] sources")
    ]
    decision_in = decision(id="d-bbbbbb", date=LATER, imported_from=other)
    assert verdict(published(), state(decision_in)) == [
        (4, "d-bbbbbb: imported from elsewhere.md, which is not listed in [import] sources")
    ]


def test_check_4_published_import_from_an_unlisted_file_is_left_alone() -> None:
    other = Imported("elsewhere.md", "H")
    before = state(entry(id=NEW, imported_from=other), NEW_AREA)
    assert verdict(before, state(entry(id=NEW, imported_from=other), NEW_AREA)) == []
