import pytest
from builders import area, at, decision, entry
from checks import (
    LATER,
    NOTES,
    NOW,
    OLD,
    REMEDY_CHECK_3,
    SPEC,
    check,
    creates,
    published,
    state,
    verdict,
)

from lodge.core import Action, Change, Decision


def test_clean_change_passes() -> None:
    new = entry(id="s-bbbbbb", title="Another")
    after = state(
        area(order=(SPEC, "s-bbbbbb")), new, creates("s-bbbbbb", id="d-bbbbbb", date=LATER)
    )
    result = check(published(), after)
    assert result.ok
    assert result.notes == ("area storage: order changed",)


def test_nothing_changed_is_clean() -> None:
    result = check(published(), state())
    assert result.ok
    assert result.notes == ()


def test_published_problem_is_note_not_failure() -> None:
    bad = decision(id="d-bbbbbb", decided_by="author", quote=None, date=at(1))
    before = state(bad)
    same = check(before, state(bad))
    assert same.ok
    assert len(same.notes) == 1
    assert "d-bbbbbb: decided_by is author, but there is no quote" + REMEDY_CHECK_3 in same.notes[0]
    worse = state(bad, decision(id="d-cccccc", replaces=("d-zzzzzz",), date=LATER))
    assert verdict(before, worse) == [(2, "d-cccccc: replaces d-zzzzzz, which does not exist")]


def test_new_state_problem_fails() -> None:
    after = state(decision(id="d-bbbbbb", replaces=("d-zzzzzz",), date=LATER))
    assert verdict(published(), after) == [(2, "d-bbbbbb: replaces d-zzzzzz, which does not exist")]


def test_check_2_published_record_missing_from_after() -> None:
    problems = check(published(), state(drop=(OLD,))).problems
    assert [(p.check, p.message) for p in problems] == [
        (2, "d-aaaaaa: was published and is missing from this state")
    ]
    assert problems[0].path == published().paths[OLD]


@pytest.mark.parametrize("verb", ["replaces", "narrows", "confirms"])
def test_check_1_new_decision_dated_no_later_than_its_target(verb: str) -> None:
    for date in (at(0), "2026-10-28T09:00:00+00:00"):
        new = decision(id="d-bbbbbb", date=date, decided_by="author", **{verb: (OLD,)})
        found = verdict(published(), state(new))
        assert found == [(1, f"d-bbbbbb: dated {date}, no later than {OLD}, which it {verb}")]
    later = decision(id="d-bbbbbb", date=LATER, decided_by="author", **{verb: (OLD,)})
    assert verdict(published(), state(later)) == []


def test_check_1_dates_compare_as_instants() -> None:
    new = decision(id="d-bbbbbb", date="2026-10-28T09:30:00+00:00", replaces=(OLD,))
    assert verdict(published(), state(new)) == []


def test_check_1_new_decision_sharing_an_entry_with_a_later_one() -> None:
    new = decision(id="d-bbbbbb", date=at(0), changes=(Change(SPEC, Action.EDIT),))
    changed = entry(id=SPEC, statement="Now this.")
    assert verdict(published(), state(new, changed)) == [
        (1, f"d-bbbbbb: dated {at(0)}, no later than {OLD}, which shares {SPEC} with it")
    ]


def test_check_1_imported_decision_is_exempt_from_the_date_rule() -> None:
    new = decision(
        id="d-bbbbbb", date="2026-01-01T00:00:00+00:00", replaces=(OLD,), imported_from=NOTES
    )
    assert verdict(published(), state(new)) == []


def test_check_1_published_decisions_are_not_dated_again() -> None:
    before = state(decision(id="d-bbbbbb", date=at(0), replaces=(OLD,)))
    assert verdict(before, state(decision(id="d-bbbbbb", date=at(0), replaces=(OLD,)))) == []


def live_edit() -> Decision:
    return decision(id="d-bbbbbb", date=at(5), changes=(Change(SPEC, Action.EDIT),))


def test_check_1_import_changes_entry_changed_live() -> None:
    imported = decision(
        id="d-cccccc", date=at(1), changes=(Change(SPEC, Action.EDIT),), imported_from=NOTES
    )
    found = verdict(state(live_edit()), state(live_edit(), imported))
    assert found == [
        (1, "d-cccccc: imported, changes s-aaaaaa, which a live decision already changed")
    ]


def test_check_1_import_changes_entry_only_imports_changed() -> None:
    spec = entry(id="s-bbbbbb", imported_from=NOTES)
    first = decision(
        id="d-bbbbbb", date=at(5), changes=(Change(spec.id, Action.CREATE),), imported_from=NOTES
    )
    second = decision(
        id="d-cccccc", date=at(1), changes=(Change(spec.id, Action.EDIT),), imported_from=NOTES
    )
    placed = area(order=(SPEC, spec.id))
    assert verdict(state(placed, spec, first), state(placed, spec, first, second)) == []


def test_area_title_change_is_note() -> None:
    result = check(published(), state(area(order=(SPEC,), title="Renamed")))
    assert result.ok
    assert result.notes == ("area storage: title changed",)


def test_area_intro_change_is_note() -> None:
    result = check(published(), state(area(order=(SPEC,), intro="Words.")))
    assert result.ok
    assert result.notes == ("area storage: intro changed",)


def test_area_order_change_is_note() -> None:
    retire = decision(id="d-bbbbbb", date=LATER, changes=(Change(SPEC, Action.RETIRE),))
    result = check(published(), state(area(order=()), retire))
    assert result.ok
    assert result.notes == ("area storage: order changed",)


def test_check_1_new_decision_dated_after_the_time_of_the_change() -> None:
    future = "2027-10-28T11:00:00+01:00"
    message = f"d-bbbbbb: dated {future}, which is after the time of this change"
    live = decision(id="d-bbbbbb", date=future, changes=(Change(SPEC, Action.EDIT),))
    assert (1, message) in verdict(published(), state(live, entry(id=SPEC, statement="Now.")))
    imported = decision(id="d-bbbbbb", date=future, imported_from=NOTES)
    assert verdict(published(), state(imported)) == [(1, message)]


def test_check_1_a_decision_dated_exactly_now_passes() -> None:
    now = decision(id="d-bbbbbb", date=NOW.isoformat())
    assert verdict(published(), state(now)) == []
    elsewhere = decision(id="d-cccccc", date="2026-10-29T11:00:00+00:00")
    assert verdict(published(), state(elsewhere)) == []


def test_published_future_dated_decision_is_not_dated_again() -> None:
    future = decision(id="d-bbbbbb", date="2027-10-28T11:00:00+01:00")
    assert verdict(state(future), state(future)) == []


def test_area_added_and_removed_are_notes() -> None:
    other = area(name="other")
    added = check(published(), state(other))
    assert added.ok
    assert added.notes == ("area other: added",)
    assert check(state(other), published()).notes == ("area other: removed",)
