from dataclasses import replace

import pytest
from builders import area, at, decision, entry, snapshot_of
from checks import check

from lodge.core import Action, Change, CheckResult, check_state

A = entry(id="s-aaaaaa")
B = entry(id="s-bbbbbb")


def trial(action: Action | None, *, statement: str = A.statement, new: bool = False) -> CheckResult:
    before = snapshot_of(area(), B, *(() if new else (A,)))
    changed = replace(A, rests_on=(B.id,), statement=statement)
    decisions = (
        ()
        if action is None
        else (decision(id="d-cccccc", date=at(30), changes=(Change(A.id, action),)),)
    )
    return check(before, snapshot_of(area(), B, changed, *decisions))


def test_link_changing_rests_on_only_passes() -> None:
    assert trial(Action.LINK).ok


def test_rests_on_change_without_decision_fails_check_4() -> None:
    assert [(p.check, p.message) for p in trial(None).problems] == [
        (
            4,
            "s-aaaaaa: edited, but no new decision in this change lists it with action "
            "edit or link; list it in the decision's changes",
        )
    ]


def test_edit_may_change_rests_on() -> None:
    assert trial(Action.EDIT).ok


def test_link_changing_the_statement_fails_check_4() -> None:
    assert any(
        p.check == 4
        and p.message
        == (
            "d-cccccc: lists link for s-aaaaaa, which changes more than rests_on; "
            "list it with action edit in another decision of this change"
        )
        for p in trial(Action.LINK, statement="Changed.").problems
    )


def test_link_for_a_new_entry_fails_check_4() -> None:
    assert any(
        p.check == 4
        and p.message
        == "d-cccccc: lists link for s-aaaaaa, which is new; list it with action create "
        "in another decision of this change"
        for p in trial(Action.LINK, new=True).problems
    )


def test_unknown_rests_on_fails_check_2() -> None:
    found = check_state(snapshot_of(area(), replace(A, rests_on=(B.id,)))).problems
    assert any(
        p.check == 2 and p.message == "s-aaaaaa: rests_on s-bbbbbb, which does not exist"
        for p in found
    )


def test_rests_on_itself_fails_check_2() -> None:
    found = check_state(snapshot_of(area(), replace(A, rests_on=(A.id,)))).problems
    assert any(p.check == 2 and p.message == "s-aaaaaa: rests_on itself" for p in found)
    assert not any(p.check == 8 for p in found)


def test_two_entry_cycle_fails_check_8_on_both() -> None:
    s = snapshot_of(area(), replace(A, rests_on=(B.id,)), replace(B, rests_on=(A.id,)))
    found = [p for p in check_state(s).problems if p.check == 8]
    assert [(p.path, p.message) for p in found] == [
        (s.paths[A.id], "s-aaaaaa: is in a cycle of rests_on links with s-bbbbbb"),
        (s.paths[B.id], "s-bbbbbb: is in a cycle of rests_on links with s-aaaaaa"),
    ]


def test_three_entry_cycle_names_the_other_two() -> None:
    c = entry(id="s-cccccc", rests_on=(A.id,))
    d = entry(id="s-dddddd", rests_on=(A.id,))
    e = entry(id="s-eeeeee")
    s = snapshot_of(
        area(), replace(A, rests_on=(B.id, e.id)), replace(B, rests_on=(c.id,)), c, d, e
    )
    found = [p for p in check_state(s).problems if p.check == 8]
    assert [p.message for p in found] == [
        f"{i}: is in a cycle of rests_on links with "
        + ", ".join(t for t in (A.id, B.id, c.id) if t != i)
        for i in (A.id, B.id, c.id)
    ]


def test_new_rest_on_retired_entry_fails_check_6() -> None:
    retired = decision(changes=(Change(B.id, Action.RETIRE),))
    before = snapshot_of(area(), A, B, retired)
    after = snapshot_of(area(), replace(A, rests_on=(B.id,)), B, retired)
    assert any(
        p.check == 6 and p.message == "s-aaaaaa: rests on s-bbbbbb, which is retired"
        for p in check(before, after).problems
    )


def test_kept_rest_on_retired_entry_passes_check_6() -> None:
    retired = decision(changes=(Change(B.id, Action.RETIRE),))
    before = snapshot_of(area(), replace(A, rests_on=(B.id,)), B, retired)
    assert not any(p.check == 6 for p in check(before, before).problems)


@pytest.mark.parametrize("new, action", [(False, Action.EDIT), (True, Action.CREATE)])
def test_link_with_another_decision_accounting_for_text_passes(new: bool, action: Action) -> None:
    before = snapshot_of(area(order=(B.id,) if new else (B.id, A.id)), B, *(() if new else (A,)))
    changed = replace(A, statement="Changed.", rests_on=(B.id,))
    link = decision(id="d-cccccc", date=at(30), changes=(Change(A.id, Action.LINK),))
    edit = decision(id="d-dddddd", date=at(31), changes=(Change(A.id, action),))
    assert check(before, snapshot_of(area(order=(B.id, A.id)), B, changed, link, edit)).ok


@pytest.mark.parametrize("field", ["statement", "title"])
def test_link_without_another_decision_accounting_for_text_fails(field: str) -> None:
    changed = replace(A, rests_on=(B.id,))
    changed = (
        replace(changed, statement="Changed.")
        if field == "statement"
        else replace(changed, title="Changed.")
    )
    link = decision(id="d-cccccc", date=at(30), changes=(Change(A.id, Action.LINK),))
    unrelated = decision(id="d-dddddd", date=at(31), changes=(Change(B.id, Action.EDIT),))
    result = check(snapshot_of(area(), A, B), snapshot_of(area(), changed, B, link, unrelated))
    assert any(
        p.check == 4
        and p.message
        == "d-cccccc: lists link for s-aaaaaa, which changes more than rests_on; "
        "list it with action edit in another decision of this change"
        for p in result.problems
    )
