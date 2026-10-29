"""Level 1 and 2 views that must not read more settled than the check and the links say."""

from builders import at, decision, entry, snapshot_of
from checks import NOTES

from lodge.core import Action, Change, Quote, derive, format_level1, level1, level2, level3

NONE: frozenset[str] = frozenset()
CHANGE = (Change("s-aaaaaa", Action.EDIT),)


def test_level1_quote_on_decision_and_entry_when_author() -> None:
    spec = entry(id="s-aaaaaa", title="Spec", statement="Holds.")
    quote = Quote("Do it.", "a session", "2026-10-28 10:00")
    author = decision(id="d-aaaaaa", decided_by="author", date=at(0), changes=CHANGE, quote=quote)
    s = snapshot_of(spec, author)
    d = derive(s)
    assert level1(s, d, "d-aaaaaa", NONE).quote == quote
    assert level1(s, d, "s-aaaaaa", NONE).quote == quote
    assert format_level1(level1(s, d, "s-aaaaaa", NONE)).endswith(
        'Holds.\n\nquote: "Do it." (a session, 2026-10-28 10:00)'
    )
    agent = decision(id="d-bbbbbb", date=at(1), changes=CHANGE)
    s = snapshot_of(spec, author, agent)
    assert level1(s, derive(s), "s-aaaaaa", NONE).quote is None
    assert level1(s, derive(s), "d-bbbbbb", NONE).quote is None


def test_level2_heads_and_entry_name_a_failing_decision() -> None:
    spec = entry(id="s-aaaaaa", title="Spec")
    bad = decision(id="d-aaaaaa", decided_by="author", date=at(0), changes=CHANGE, title="Bad")
    s = snapshot_of(spec, bad)
    d = derive(s)
    failing = frozenset({"d-aaaaaa"})
    assert level1(s, d, "s-aaaaaa", failing).flags == ("decision fails check",)
    assert level2(s, d, "s-aaaaaa", failing).splitlines()[0].endswith("· product · fails check")


def test_entry_whose_decision_is_replaced_or_narrowed() -> None:
    spec = entry(id="s-aaaaaa")
    basis = decision(id="d-aaaaaa", date=at(0), changes=CHANGE)
    s = snapshot_of(spec, basis, decision(id="d-bbbbbb", date=at(1), replaces=("d-aaaaaa",)))
    assert level1(s, derive(s), "s-aaaaaa", NONE).flags == ("its decision replaced by d-bbbbbb",)
    s = snapshot_of(spec, basis, decision(id="d-bbbbbb", date=at(1), narrows=("d-aaaaaa",)))
    assert level1(s, derive(s), "s-aaaaaa", NONE).flags == ("its decision narrowed by d-bbbbbb",)


def test_flag_order_in_full() -> None:
    old = decision(id="d-aaaaaa", decided_by="author", date=at(0), imported_from=NOTES)
    narrower = decision(id="d-bbbbbb", date=at(1), narrows=("d-aaaaaa",))
    newer = decision(id="d-cccccc", date=at(2), replaces=("d-aaaaaa",))
    s = snapshot_of(old, narrower, newer)
    assert level1(s, derive(s), "d-aaaaaa", frozenset({"d-aaaaaa"})).flags == (
        "replaced by d-cccccc",
        "narrowed by d-bbbbbb",
        "awaiting the author on d-cccccc, d-bbbbbb",
        "imported",
        "unquoted",
        "fails check",
    )
    spec = entry(id="s-aaaaaa", imported_from=NOTES)
    basis = decision(id="d-dddddd", date=at(3), changes=(Change("s-aaaaaa", Action.RETIRE),))
    s = snapshot_of(spec, basis, decision(id="d-eeeeee", date=at(4), narrows=("d-dddddd",)))
    failing = frozenset({"s-aaaaaa", "d-dddddd"})
    assert level1(s, derive(s), "s-aaaaaa", failing).flags == (
        "retired by d-dddddd",
        "its decision narrowed by d-eeeeee",
        "imported",
        "fails check",
        "decision fails check",
    )


def test_entry_without_decision_says_so() -> None:
    s = snapshot_of(entry(id="s-dddddd", area="storage"))
    got = format_level1(level1(s, derive(s), "s-dddddd", NONE))
    assert got.splitlines()[0] == "s-dddddd · current · no decision · storage"


def test_level3_changes_carry_the_action() -> None:
    kill = decision(
        id="d-aaaaaa",
        changes=(Change("s-aaaaaa", Action.CREATE), Change("s-bbbbbb", Action.RETIRE)),
    )
    s = snapshot_of(entry(id="s-aaaaaa"), entry(id="s-bbbbbb"), kill)
    assert level3(s, derive(s), "d-aaaaaa").links == (
        ("changes (create)", "s-aaaaaa", "current"),
        ("changes (retire)", "s-bbbbbb", "retired"),
    )


def test_retired_by_names_a_standing_retirement() -> None:
    kill = (Change("s-aaaaaa", Action.RETIRE),)
    first = decision(id="d-bbbbbb", decided_by="author", date=at(1), changes=kill)
    again = decision(id="d-cccccc", date=at(2), changes=kill)
    undo = decision(id="d-dddddd", decided_by="author", date=at(3), replaces=("d-cccccc",))
    s = snapshot_of(entry(id="s-aaaaaa"), first, again, undo)
    assert "retired by d-bbbbbb" in level1(s, derive(s), "s-aaaaaa", NONE).flags
