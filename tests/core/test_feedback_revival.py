from builders import at, decision, entry, files_of, snapshot_of

from lodge.core import (
    Action,
    Change,
    Feedback,
    LengthGuidance,
    Record,
    Snapshot,
    Tree,
    derive,
    load,
    new_record_path,
)
from lodge.core import feedback as give_feedback

CREATE = (Change("s-aaaaaa", Action.CREATE),)
EDIT = (Change("s-aaaaaa", Action.EDIT),)
RETIRE = (Change("s-aaaaaa", Action.RETIRE),)


def given(snapshot: Snapshot, added: Record) -> list[Feedback]:
    return give_feedback([added], snapshot, derive(snapshot), LengthGuidance())


def her_creation() -> list[Record]:
    return [
        entry(id="s-aaaaaa"),
        decision(id="d-aaaaaa", decided_by="author", date=at(0), changes=CREATE),
    ]


def test_dangling_replaces_leaves_the_revival_line_and_does_not_raise() -> None:
    retire = decision(id="d-bbbbbb", decided_by="author", date=at(1), changes=RETIRE)
    new = decision(
        id="d-cccccc", decided_by="author", date=at(2), replaces=("d-zzzzzz", "d-bbbbbb")
    )
    found = given(snapshot_of(*her_creation(), retire, new), new)
    assert [f.message[:30] for f in found] == ["it replaces d-bbbbbb, the last"]


def test_rejecting_an_agent_edit_and_a_later_agent_retirement_asks_to_edit_back() -> None:
    edit = decision(id="d-bbbbbb", date=at(1), changes=EDIT)
    retire = decision(id="d-cccccc", date=at(2), changes=RETIRE)
    new = decision(
        id="d-dddddd", decided_by="author", date=at(3), replaces=("d-bbbbbb", "d-cccccc")
    )
    found = given(snapshot_of(*her_creation(), edit, retire, new), new)
    assert found == [
        Feedback(
            "d-dddddd",
            "it replaces d-bbbbbb, whose edit of s-aaaaaa is still the latest edit of that "
            "entry; does d-dddddd edit s-aaaaaa back? If so, add an edit draft of s-aaaaaa "
            "and list it in changes with action edit",
        ),
        Feedback(
            "d-dddddd",
            "it replaces d-cccccc, the last standing retirement of s-aaaaaa, so s-aaaaaa "
            "becomes current again; to keep it retired, list it in changes with action retire",
        ),
    ]


def test_one_revival_line_names_every_replaced_retirement() -> None:
    first = decision(id="d-bbbbbb", decided_by="author", date=at(1), changes=RETIRE)
    second = decision(id="d-cccccc", decided_by="author", date=at(2), changes=RETIRE)
    new = decision(
        id="d-dddddd", decided_by="author", date=at(3), replaces=("d-bbbbbb", "d-cccccc")
    )
    found = given(snapshot_of(*her_creation(), first, second, new), new)
    assert found == [
        Feedback(
            "d-dddddd",
            "it replaces d-bbbbbb and d-cccccc, the last standing retirements of s-aaaaaa, so "
            "s-aaaaaa becomes current again; to keep it retired, list it in changes with action "
            "retire",
        )
    ]


def test_no_revival_line_when_the_entry_stays_retired() -> None:
    first = decision(id="d-bbbbbb", decided_by="author", date=at(1), changes=RETIRE)
    new = decision(id="d-cccccc", decided_by="author", date=at(2), replaces=("d-bbbbbb",))
    again = decision(id="d-dddddd", decided_by="author", date=at(3), changes=RETIRE)
    assert given(snapshot_of(*her_creation(), first, new, again), new) == []


def given_files(files: dict[str, str], added: Record) -> list[Feedback]:
    return given(load(Tree(None, files, frozenset())), added)


def unparsable(files: dict[str, str], record: Record) -> None:
    path = new_record_path(record)
    files[path] = files[path].replace("title:", "titel:")


def test_unparsable_decision_in_replaces_does_not_crash() -> None:
    retire = decision(id="d-bbbbbb", decided_by="author", date=at(1), changes=RETIRE)
    bad = decision(id="d-zzzzzz", date=at(1), changes=RETIRE)
    new = decision(id="d-cccccc", date=at(2), replaces=("d-zzzzzz", "d-bbbbbb"))
    files = files_of(*her_creation(), retire, bad, new)
    unparsable(files, bad)
    found = given_files(files, new)
    assert [f.message[:30] for f in found if f.message.startswith("it replaces")] == [
        "it replaces d-bbbbbb, the last"
    ]


def test_revival_of_an_unparsable_entry_does_not_crash() -> None:
    retire = decision(id="d-bbbbbb", decided_by="author", date=at(1), changes=RETIRE)
    new = decision(id="d-cccccc", date=at(2), replaces=("d-bbbbbb",))
    files = files_of(*her_creation(), retire, new)
    unparsable(files, entry(id="s-aaaaaa"))
    assert not any(f.message.startswith("it replaces") for f in given_files(files, new))


def test_revival_of_a_dangling_entry_does_not_crash() -> None:
    ghost = decision(
        id="d-bbbbbb",
        decided_by="author",
        date=at(1),
        changes=(Change("s-zzzzzz", Action.RETIRE),),
    )
    new = decision(id="d-cccccc", date=at(2), replaces=("d-bbbbbb",))
    found = given(snapshot_of(*her_creation(), ghost, new), new)
    assert not any(f.message.startswith("it replaces") for f in found)


def test_revival_line_names_only_retirements_that_were_standing() -> None:
    first = decision(id="d-bbbbbb", decided_by="author", date=at(1), changes=RETIRE)
    second = decision(id="d-cccccc", decided_by="author", date=at(2), changes=RETIRE)
    earlier = decision(id="d-dddddd", decided_by="author", date=at(3), replaces=("d-bbbbbb",))
    new = decision(
        id="d-eeeeee", decided_by="author", date=at(4), replaces=("d-bbbbbb", "d-cccccc")
    )
    found = given(snapshot_of(*her_creation(), first, second, earlier, new), new)
    assert [f.message[:50] for f in found] == [
        "d-bbbbbb is already replaced by d-dddddd",
        "it replaces d-cccccc, the last standing retirement",
    ]


def test_replacing_a_decision_another_decision_already_replaced_says_so() -> None:
    old = decision(id="d-aaaaaa", date=at(0))
    first = decision(id="d-bbbbbb", date=at(1), replaces=("d-aaaaaa",))
    new = decision(id="d-cccccc", date=at(2), replaces=("d-aaaaaa",))
    found = given(snapshot_of(old, first, new), new)
    assert found == [Feedback("d-cccccc", "d-aaaaaa is already replaced by d-bbbbbb")]


def test_replacing_a_decision_only_this_decision_replaces_is_silent() -> None:
    old = decision(id="d-aaaaaa", date=at(0))
    new = decision(id="d-cccccc", date=at(2), replaces=("d-aaaaaa",))
    assert given(snapshot_of(old, new), new) == []
