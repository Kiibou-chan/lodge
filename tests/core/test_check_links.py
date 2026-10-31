from dataclasses import replace

from builders import area, at, decision, entry, snapshot_of
from checks import check

from lodge.core import Action, Change, CheckResult, check_state

A = entry(id="s-aaaaaa")
B = entry(id="s-bbbbbb")


def trial(action: str | None, *, statement: str = A.statement, new: bool = False) -> CheckResult:
    before = snapshot_of(area(), B, *(() if new else (A,)))
    changed = replace(A, rests_on=(B.id,), statement=statement)
    decisions = (
        ()
        if action is None
        else (decision(id="d-cccccc", date=at(30), changes=(Change(A.id, Action(action)),)),)
    )
    return check(before, snapshot_of(area(), B, changed, *decisions))


def test_link_changing_rests_on_only_passes() -> None:
    assert trial("link").ok


def test_rests_on_change_without_decision_fails_check_4() -> None:
    assert [(p.check, p.message) for p in trial(None).problems] == [
        (
            4,
            "s-aaaaaa: edited, but no new decision in this change lists it with action "
            "edit or link; list it in the decision's changes",
        )
    ]


def test_edit_may_change_rests_on() -> None:
    assert trial("edit").ok


def test_link_changing_the_statement_fails_check_4() -> None:
    assert any(
        p.check == 4
        and p.message
        == (
            "d-cccccc: lists link for s-aaaaaa, which changes more than rests_on; "
            "list it with action edit"
        )
        for p in trial("link", statement="Changed.").problems
    )


def test_link_for_a_new_entry_fails_check_4() -> None:
    assert any(
        p.check == 4
        and p.message
        == "d-cccccc: lists link for s-aaaaaa, which is new; list it with action create"
        for p in trial("link", new=True).problems
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


def test_two_entry_cycle_fails_check_8_on_both() -> None:
    s = snapshot_of(area(), replace(A, rests_on=(B.id,)), replace(B, rests_on=(A.id,)))
    found = [p for p in check_state(s).problems if p.check == 8]
    assert [(p.path, p.message) for p in found] == [
        (s.paths[A.id], "s-aaaaaa: is in a cycle of rests_on links with s-bbbbbb"),
        (s.paths[B.id], "s-bbbbbb: is in a cycle of rests_on links with s-aaaaaa"),
    ]


def test_three_entry_cycle_names_the_other_two() -> None:
    c = entry(id="s-cccccc", rests_on=(A.id,))
    s = snapshot_of(area(), replace(A, rests_on=(B.id,)), replace(B, rests_on=(c.id,)), c)
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
