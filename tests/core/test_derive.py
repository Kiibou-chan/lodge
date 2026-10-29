from builders import at, decision, entry, files_of
from derivation import IMPORTED, snapshot_of

from lodge.core import (
    Action,
    Change,
    Tree,
    derive,
    is_author,
    load,
)


def test_is_author() -> None:
    assert is_author(decision(decided_by="author"))
    assert not is_author(decision(decided_by="coordinator"))


def test_replaced_and_successor() -> None:
    old = decision(id="d-aaaaaa", date=at(0))
    new = decision(id="d-bbbbbb", date=at(1), replaces=("d-aaaaaa",))
    got = derive(snapshot_of(old, new))
    assert got.status == {"d-aaaaaa": "replaced", "d-bbbbbb": "current"}
    assert got.replaced_by == {"d-aaaaaa": ("d-bbbbbb",)}


def test_narrowed_stays_current() -> None:
    old = decision(id="d-aaaaaa", date=at(0))
    new = decision(id="d-bbbbbb", date=at(1), narrows=("d-aaaaaa",))
    got = derive(snapshot_of(old, new))
    assert got.status["d-aaaaaa"] == "current"
    assert got.narrowed_by == {"d-aaaaaa": ("d-bbbbbb",)}
    assert got.replaced_by == {}


def test_retired_entry() -> None:
    spec = entry(id="s-aaaaaa")
    make = decision(id="d-aaaaaa", date=at(0), changes=(Change("s-aaaaaa", Action.CREATE),))
    kill = decision(id="d-bbbbbb", date=at(1), changes=(Change("s-aaaaaa", Action.RETIRE),))
    assert derive(snapshot_of(spec, make)).status["s-aaaaaa"] == "current"
    assert derive(snapshot_of(spec, make, kill)).status["s-aaaaaa"] == "retired"


def test_changed_by_newest_first() -> None:
    spec = entry(id="s-aaaaaa")
    change = (Change("s-aaaaaa", Action.EDIT),)
    ds = [
        decision(id="d-aaaaaa", date=at(5), changes=change),
        decision(id="d-bbbbbb", date=at(9), changes=change),
        decision(id="d-cccccc", date=at(1), changes=change),
        decision(id="d-dddddd", date=at(9), changes=change),
    ]
    got = derive(snapshot_of(spec, *ds))
    assert got.changed_by == {"s-aaaaaa": ("d-dddddd", "d-bbbbbb", "d-aaaaaa", "d-cccccc")}


def test_agent_replacing_author_flagged() -> None:
    author = decision(id="d-aaaaaa", decided_by="author", date=at(0))
    agent = decision(id="d-bbbbbb", date=at(1), replaces=("d-aaaaaa",))
    assert derive(snapshot_of(author, agent)).awaiting_author == {"d-bbbbbb"}


def test_agent_narrowing_author_flagged() -> None:
    author = decision(id="d-aaaaaa", decided_by="author", date=at(0))
    agent = decision(id="d-bbbbbb", date=at(1), narrows=("d-aaaaaa",))
    assert derive(snapshot_of(author, agent)).awaiting_author == {"d-bbbbbb"}


def test_author_decisions_are_never_flagged() -> None:
    first = decision(id="d-aaaaaa", decided_by="author", date=at(0))
    second = decision(id="d-bbbbbb", decided_by="author", date=at(1), replaces=("d-aaaaaa",))
    assert derive(snapshot_of(first, second)).awaiting_author == frozenset()


def test_agent_after_author_edit_flagged() -> None:
    spec = entry(id="s-aaaaaa")
    change = (Change("s-aaaaaa", Action.EDIT),)
    author = decision(id="d-aaaaaa", decided_by="author", date=at(0), changes=change)
    agent = decision(id="d-bbbbbb", date=at(1), changes=change)
    assert derive(snapshot_of(spec, author, agent)).awaiting_author == {"d-bbbbbb"}


def test_agent_after_agent_edit_not_flagged() -> None:
    spec = entry(id="s-aaaaaa")
    change = (Change("s-aaaaaa", Action.EDIT),)
    author = decision(id="d-aaaaaa", decided_by="author", date=at(0), changes=change)
    first = decision(id="d-bbbbbb", date=at(1), changes=change)
    second = decision(id="d-cccccc", date=at(2), changes=change)
    assert derive(snapshot_of(spec, author, first, second)).awaiting_author == {"d-bbbbbb"}


def test_author_edit_dated_after_the_agent_does_not_flag_it() -> None:
    spec = entry(id="s-aaaaaa")
    change = (Change("s-aaaaaa", Action.EDIT),)
    agent = decision(id="d-aaaaaa", date=at(0), changes=change)
    author = decision(id="d-bbbbbb", decided_by="author", date=at(1), changes=change)
    assert derive(snapshot_of(spec, agent, author)).awaiting_author == frozenset()


def test_flag_clears_on_confirm() -> None:
    author = decision(id="d-aaaaaa", decided_by="author", date=at(0))
    agent = decision(id="d-bbbbbb", date=at(1), replaces=("d-aaaaaa",))
    confirm = decision(id="d-cccccc", decided_by="author", date=at(2), confirms=("d-bbbbbb",))
    got = derive(snapshot_of(author, agent, confirm))
    assert got.awaiting_author == frozenset()
    assert got.confirmed_by == {"d-bbbbbb": ("d-cccccc",)}


def test_confirm_by_an_agent_does_not_clear() -> None:
    author = decision(id="d-aaaaaa", decided_by="author", date=at(0))
    agent = decision(id="d-bbbbbb", date=at(1), replaces=("d-aaaaaa",))
    other = decision(id="d-cccccc", date=at(2), confirms=("d-bbbbbb",))
    got = derive(snapshot_of(author, agent, other))
    assert got.awaiting_author == {"d-bbbbbb"}
    assert got.confirmed_by == {}


def test_flag_clears_on_author_replace() -> None:
    author = decision(id="d-aaaaaa", decided_by="author", date=at(0))
    agent = decision(id="d-bbbbbb", date=at(1), replaces=("d-aaaaaa",))
    again = decision(id="d-cccccc", decided_by="author", date=at(2), replaces=("d-bbbbbb",))
    assert derive(snapshot_of(author, agent, again)).awaiting_author == frozenset()


def test_flag_shows_on_targets() -> None:
    spec = entry(id="s-aaaaaa")
    change = (Change("s-aaaaaa", Action.EDIT),)
    author = decision(id="d-aaaaaa", decided_by="author", date=at(0), changes=change)
    agent = decision(id="d-bbbbbb", date=at(1), changes=change, narrows=("d-aaaaaa",))
    got = derive(snapshot_of(spec, author, agent))
    assert got.touched_by_flagged == {"s-aaaaaa": ("d-bbbbbb",), "d-aaaaaa": ("d-bbbbbb",)}
    cleared = decision(id="d-cccccc", decided_by="author", date=at(2), confirms=("d-bbbbbb",))
    assert derive(snapshot_of(spec, author, agent, cleared)).touched_by_flagged == {}


def test_imported_touching_only_imported_not_flagged() -> None:
    old = decision(
        id="d-aaaaaa", decided_by="author", date="2026-01-01T00:00:00+00:00", imported_from=IMPORTED
    )
    new = decision(
        id="d-bbbbbb",
        date="2026-02-01T00:00:00+00:00",
        replaces=("d-aaaaaa",),
        imported_from=IMPORTED,
    )
    assert derive(snapshot_of(old, new)).awaiting_author == frozenset()


def test_imported_after_imported_author_edit_not_flagged() -> None:
    spec = entry(id="s-aaaaaa", imported_from=IMPORTED)
    change = (Change("s-aaaaaa", Action.EDIT),)
    old = decision(
        id="d-aaaaaa",
        decided_by="author",
        date="2026-01-01T00:00:00+00:00",
        changes=change,
        imported_from=IMPORTED,
    )
    new = decision(
        id="d-bbbbbb", date="2026-02-01T00:00:00+00:00", changes=change, imported_from=IMPORTED
    )
    assert derive(snapshot_of(spec, old, new)).awaiting_author == frozenset()


def test_imported_replacing_live_author_decision_flagged() -> None:
    old = decision(id="d-aaaaaa", decided_by="author", date=at(0))
    new = decision(
        id="d-bbbbbb",
        date="2026-11-01T00:00:00+00:00",
        replaces=("d-aaaaaa",),
        imported_from=IMPORTED,
    )
    assert derive(snapshot_of(old, new)).awaiting_author == {"d-bbbbbb"}


def test_agent_change_to_missing_entry_does_not_crash() -> None:
    change = (Change("s-zzzzzz", Action.EDIT),)
    agent = decision(id="d-aaaaaa", date=at(0), changes=change)
    got = derive(load(Tree(None, files_of(agent), frozenset())))
    assert got.awaiting_author == frozenset()
    assert got.changed_by == {}
    assert got.touched_by_flagged == {}


def test_agent_after_author_edit_of_unparsable_entry_flagged() -> None:
    change = (Change("s-aaaaaa", Action.EDIT),)
    author = decision(id="d-aaaaaa", decided_by="author", date=at(0), changes=change)
    agent = decision(id="d-bbbbbb", date=at(1), changes=change)
    files = files_of(author, agent)
    files["lodge/spec/storage/s-aaaaaa-broken.md"] = "---\nid: s-aaaaaa\nkind: spec\n---\n\nText.\n"
    snap = load(Tree(None, files, frozenset()))
    assert len(snap.problems) == 1
    got = derive(snap)
    assert got.awaiting_author == {"d-bbbbbb"}
    assert got.changed_by == {}


def test_imported_author_replacing_live_author_decision_flagged() -> None:
    old = decision(id="d-aaaaaa", decided_by="author", date=at(0))
    new = decision(
        id="d-bbbbbb",
        decided_by="author",
        date="2026-01-01T00:00:00+00:00",
        replaces=("d-aaaaaa",),
        imported_from=IMPORTED,
    )
    assert derive(snapshot_of(old, new)).awaiting_author == {"d-bbbbbb"}


def test_imported_author_editing_live_author_entry_flagged() -> None:
    spec = entry(id="s-aaaaaa")
    change = (Change("s-aaaaaa", Action.EDIT),)
    old = decision(id="d-aaaaaa", decided_by="author", date=at(0), changes=change)
    new = decision(
        id="d-bbbbbb",
        decided_by="author",
        date="2026-11-01T00:00:00+00:00",
        changes=change,
        imported_from=IMPORTED,
    )
    assert derive(snapshot_of(spec, old, new)).awaiting_author == {"d-bbbbbb"}


def test_imported_author_confirm_does_not_clear() -> None:
    author = decision(id="d-aaaaaa", decided_by="author", date=at(0))
    agent = decision(id="d-bbbbbb", date=at(1), replaces=("d-aaaaaa",))
    confirm = decision(
        id="d-cccccc",
        decided_by="author",
        date="2026-11-01T00:00:00+00:00",
        confirms=("d-bbbbbb",),
        imported_from=IMPORTED,
    )
    assert derive(snapshot_of(author, agent, confirm)).awaiting_author == {"d-bbbbbb"}


def test_confirm_dated_before_does_not_clear() -> None:
    author = decision(id="d-aaaaaa", decided_by="author", date=at(0))
    agent = decision(id="d-bbbbbb", date=at(5), replaces=("d-aaaaaa",))
    early = decision(id="d-cccccc", decided_by="author", date=at(2), confirms=("d-bbbbbb",))
    assert derive(snapshot_of(author, agent, early)).awaiting_author == {"d-bbbbbb"}


def test_imported_author_creation_not_flagged_by_her_later_live_edit() -> None:
    spec = entry(id="s-aaaaaa", imported_from=IMPORTED)
    created = decision(
        id="d-aaaaaa",
        decided_by="author",
        date="2026-01-01T00:00:00+00:00",
        changes=(Change("s-aaaaaa", Action.CREATE),),
        imported_from=IMPORTED,
    )
    edit = decision(
        id="d-bbbbbb", decided_by="author", date=at(0), changes=(Change("s-aaaaaa", Action.EDIT),)
    )
    assert derive(snapshot_of(spec, created, edit)).awaiting_author == frozenset()


def test_imported_agent_edit_before_her_later_live_edit_not_flagged() -> None:
    spec = entry(id="s-aaaaaa", imported_from=IMPORTED)
    created = decision(
        id="d-aaaaaa",
        decided_by="author",
        date="2026-01-01T00:00:00+00:00",
        changes=(Change("s-aaaaaa", Action.CREATE),),
        imported_from=IMPORTED,
    )
    change = (Change("s-aaaaaa", Action.EDIT),)
    between = decision(
        id="d-cccccc", date="2026-02-01T00:00:00+00:00", changes=change, imported_from=IMPORTED
    )
    edit = decision(id="d-bbbbbb", decided_by="author", date=at(0), changes=change)
    assert derive(snapshot_of(spec, created, between, edit)).awaiting_author == frozenset()
