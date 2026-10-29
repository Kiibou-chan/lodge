from builders import area, at, decision, entry
from checks import LATER, SPEC, Item, state, verdict

from lodge.core import Action, Change


def retired() -> list[Item]:
    retire = decision(id="d-cccccc", date=at(2), changes=(Change(SPEC, Action.RETIRE),))
    return [retire, area(order=())]


def test_check_6_replacing_the_retirement_lets_the_decision_edit_the_entry_again() -> None:
    before = state(*retired())
    back = decision(
        id="d-dddddd",
        date=LATER,
        replaces=("d-cccccc",),
        changes=(Change(SPEC, Action.EDIT),),
    )
    restored = entry(id=SPEC, statement="Restored.")
    after = state(*retired(), back, restored, area(order=(SPEC,)))
    assert verdict(before, after) == []


def test_check_6_a_later_decision_may_edit_an_entry_whose_retirement_was_replaced() -> None:
    back = decision(id="d-dddddd", date=at(5), replaces=("d-cccccc",))
    items = [*retired(), back, area(order=(SPEC,))]
    new = decision(id="d-eeeeee", date=LATER, changes=(Change(SPEC, Action.EDIT),))
    after = state(*items, new, entry(id=SPEC, statement="Edited."))
    assert verdict(state(*items), after) == []
