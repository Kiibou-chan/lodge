from builders import at, decision, entry
from derivation import IMPORTED, snapshot_of

from lodge.core import Action, Change, Decision, SpecEntry, derive


def test_agent_rewrites_an_edit_she_confirmed() -> None:
    spec = entry(id="s-aaaaaa")
    change = (Change("s-aaaaaa", Action.EDIT),)
    author = decision(id="d-aaaaaa", decided_by="author", date=at(0), changes=change)
    first = decision(id="d-bbbbbb", date=at(1), changes=change)
    confirm = decision(id="d-cccccc", decided_by="author", date=at(2), confirms=("d-bbbbbb",))
    second = decision(id="d-dddddd", date=at(3), changes=change)
    got = derive(snapshot_of(spec, author, first, confirm, second))
    assert got.awaiting_author == {"d-dddddd"}


def test_agent_replaces_a_decision_she_confirmed() -> None:
    author = decision(id="d-aaaaaa", decided_by="author", date=at(0))
    first = decision(id="d-bbbbbb", date=at(1), narrows=("d-aaaaaa",))
    confirm = decision(id="d-cccccc", decided_by="author", date=at(2), confirms=("d-bbbbbb",))
    second = decision(id="d-dddddd", date=at(3), replaces=("d-bbbbbb",))
    assert derive(snapshot_of(author, first, confirm, second)).awaiting_author == {"d-dddddd"}


def test_confirmation_dated_after_the_later_agent_change_still_counts() -> None:
    spec = entry(id="s-aaaaaa")
    change = (Change("s-aaaaaa", Action.EDIT),)
    author = decision(id="d-aaaaaa", decided_by="author", date=at(0), changes=change)
    first = decision(id="d-bbbbbb", date=at(1), changes=change)
    second = decision(id="d-cccccc", date=at(2), changes=change)
    confirm = decision(id="d-dddddd", decided_by="author", date=at(9), confirms=("d-bbbbbb",))
    got = derive(snapshot_of(spec, author, first, second, confirm))
    assert got.awaiting_author == {"d-cccccc"}


def test_imported_confirmation_does_not_make_a_decision_hers() -> None:
    spec = entry(id="s-aaaaaa")
    change = (Change("s-aaaaaa", Action.EDIT),)
    author = decision(id="d-aaaaaa", decided_by="author", date=at(0), changes=change)
    first = decision(id="d-bbbbbb", date=at(1), changes=change)
    confirm = decision(
        id="d-cccccc",
        decided_by="author",
        date="2026-11-01T00:00:00+00:00",
        confirms=("d-bbbbbb",),
        imported_from=IMPORTED,
    )
    second = decision(id="d-dddddd", date=at(3), changes=change)
    got = derive(snapshot_of(spec, author, first, confirm, second))
    assert got.awaiting_author == {"d-bbbbbb"}


def retired_by_an_agent() -> list[Decision | SpecEntry]:
    create = (Change("s-aaaaaa", Action.CREATE),)
    return [
        entry(id="s-aaaaaa"),
        decision(id="d-aaaaaa", decided_by="author", date=at(0), changes=create),
        decision(id="d-bbbbbb", date=at(1), changes=(Change("s-aaaaaa", Action.RETIRE),)),
    ]


def test_replacing_the_retirement_makes_the_entry_current() -> None:
    rejected = decision(id="d-cccccc", decided_by="author", date=at(2), replaces=("d-bbbbbb",))
    kept = derive(snapshot_of(*retired_by_an_agent()))
    back = derive(snapshot_of(*retired_by_an_agent(), rejected))
    assert kept.status["s-aaaaaa"] == "retired"
    assert (back.status["s-aaaaaa"], back.status["d-bbbbbb"]) == ("current", "replaced")
    assert back.awaiting_author == frozenset()


def test_entry_stays_retired_while_another_retirement_stands() -> None:
    again = decision(id="d-cccccc", date=at(2), changes=(Change("s-aaaaaa", Action.RETIRE),))
    rejected = decision(id="d-dddddd", decided_by="author", date=at(3), replaces=("d-bbbbbb",))
    got = derive(snapshot_of(*retired_by_an_agent(), again, rejected))
    assert got.status["s-aaaaaa"] == "retired"


def test_agent_edit_after_she_replaced_an_agent_retirement_flagged() -> None:
    rejected = decision(id="d-cccccc", decided_by="author", date=at(2), replaces=("d-bbbbbb",))
    edit = decision(id="d-dddddd", date=at(3), changes=(Change("s-aaaaaa", Action.EDIT),))
    got = derive(snapshot_of(*retired_by_an_agent(), rejected, edit))
    assert got.awaiting_author == {"d-dddddd"}


def test_agent_edit_after_she_replaced_an_agent_edit_flagged() -> None:
    change = (Change("s-aaaaaa", Action.EDIT),)
    first = decision(id="d-bbbbbb", date=at(1), changes=change)
    rejected = decision(id="d-cccccc", decided_by="author", date=at(2), replaces=("d-bbbbbb",))
    second = decision(id="d-dddddd", date=at(3), changes=change)
    items = [*retired_by_an_agent()[:2], first, rejected, second]
    assert derive(snapshot_of(*items)).awaiting_author == {"d-dddddd"}


def test_agent_edit_after_an_agent_replaced_by_an_agent_is_as_before() -> None:
    change = (Change("s-aaaaaa", Action.EDIT),)
    first = decision(id="d-bbbbbb", date=at(1), changes=change)
    second = decision(id="d-cccccc", date=at(2), replaces=("d-bbbbbb",), changes=change)
    third = decision(id="d-dddddd", date=at(3), changes=change)
    items = [*retired_by_an_agent()[:2], first, second, third]
    assert derive(snapshot_of(*items)).awaiting_author == {"d-bbbbbb"}


def test_agent_edit_after_she_corrected_her_own_decision_flagged() -> None:
    change = (Change("s-aaaaaa", Action.EDIT),)
    created = [*retired_by_an_agent()[:2]]
    correction = decision(id="d-cccccc", decided_by="author", date=at(2), replaces=("d-aaaaaa",))
    edit = decision(id="d-dddddd", date=at(3), changes=change)
    assert derive(snapshot_of(*created, correction, edit)).awaiting_author == {"d-dddddd"}


def test_agent_edit_after_she_corrected_her_own_edit_flagged() -> None:
    change = (Change("s-aaaaaa", Action.EDIT),)
    start = decision(id="d-aaaaaa", date=at(0), changes=(Change("s-aaaaaa", Action.CREATE),))
    hers = decision(id="d-bbbbbb", decided_by="author", date=at(1), changes=change)
    correction = decision(id="d-cccccc", decided_by="author", date=at(2), replaces=("d-bbbbbb",))
    edit = decision(id="d-dddddd", date=at(3), changes=change)
    got = derive(snapshot_of(entry(id="s-aaaaaa"), start, hers, correction, edit))
    assert got.awaiting_author == {"d-dddddd"}


def retired_by_her() -> list[Decision | SpecEntry]:
    kill = (Change("s-aaaaaa", Action.RETIRE),)
    author = decision(id="d-bbbbbb", decided_by="author", date=at(1), changes=kill)
    return [*retired_by_an_agent()[:2], author]


def test_agent_reviving_her_retired_entry_flags_the_entry() -> None:
    revive = decision(id="d-cccccc", date=at(2), replaces=("d-bbbbbb",))
    got = derive(snapshot_of(*retired_by_her(), revive))
    assert got.status["s-aaaaaa"] == "current"
    assert got.awaiting_author == {"d-cccccc"}
    assert got.touched_by_flagged["s-aaaaaa"] == ("d-cccccc",)
    assert got.changed_by["s-aaaaaa"][0] == "d-cccccc"


def test_agent_reviving_an_entry_an_agent_retired_is_not_flagged() -> None:
    revive = decision(id="d-cccccc", date=at(2), replaces=("d-bbbbbb",))
    got = derive(snapshot_of(*retired_by_an_agent(), revive))
    assert got.awaiting_author == {"d-bbbbbb"}
    assert got.touched_by_flagged["s-aaaaaa"] == ("d-bbbbbb",)
