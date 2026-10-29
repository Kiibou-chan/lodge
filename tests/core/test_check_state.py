from dataclasses import replace

import pytest
from builders import area, at, decision, entry, files_of, snapshot_of
from checks import REMEDY_ATTACH, REMEDY_CHECK_3

from lodge.core import (
    Action,
    Change,
    Imported,
    Problem,
    Quote,
    Snapshot,
    Tree,
    check_state,
    load,
    new_record_path,
)

SPEC = "s-aaaaaa"
OLD = decision(id="d-aaaaaa", date=at(0), changes=(Change(SPEC, Action.CREATE),))


def world(*extra: object) -> Snapshot:
    base = (area(order=(SPEC,)), entry(id=SPEC), OLD)
    return snapshot_of(*base, *extra)  # type: ignore[arg-type]


def lines(snap: Snapshot) -> list[tuple[int, str]]:
    return [(p.check, p.message) for p in check_state(snap).problems]


def test_clean_state_passes() -> None:
    result = check_state(world())
    assert result.ok
    assert result.problems == ()
    assert result.notes == ()


def test_check_1_parse_problem_is_reported() -> None:
    bad = Problem("lodge/decisions/d-bbbbbb-x.md", 1, "the header is not closed", 3)
    assert check_state(world()).ok
    assert check_state(snapshot_of(problems=(bad,))).problems == (bad,)


def test_check_1_file_name_without_the_id() -> None:
    other = decision(id="d-bbbbbb")
    paths = {"d-bbbbbb": "lodge/decisions/d-cccccc-misnamed.md"}
    snap = snapshot_of(area(), other, paths=paths)
    assert lines(snap) == [
        (1, "d-bbbbbb: the file name d-cccccc-misnamed.md does not start with the ID")
    ]
    assert check_state(snap).problems[0].path == paths["d-bbbbbb"]


def test_check_1_file_name_of_the_bare_id_passes() -> None:
    paths = {"d-bbbbbb": "lodge/decisions/d-bbbbbb.md"}
    assert check_state(snapshot_of(decision(id="d-bbbbbb"), paths=paths)).ok


def test_check_1_file_name_that_only_begins_like_the_id() -> None:
    paths = {"d-bbbbbb": "lodge/decisions/d-bbbbbbx-title.md"}
    assert not check_state(snapshot_of(decision(id="d-bbbbbb"), paths=paths)).ok


@pytest.mark.parametrize(
    ("field", "kwargs"),
    [
        ("changes", {"changes": (Change("s-zzzzzz", Action.EDIT),)}),
        ("replaces", {"replaces": ("d-zzzzzz",)}),
        ("narrows", {"narrows": ("d-zzzzzz",)}),
        ("confirms", {"confirms": ("d-zzzzzz",)}),
    ],
)
def test_check_2_unresolved_link(field: str, kwargs: dict[str, object]) -> None:
    target = "s-zzzzzz" if field == "changes" else "d-zzzzzz"
    snap = world(decision(id="d-bbbbbb", decided_by="author", **kwargs))
    assert lines(snap) == [(2, f"d-bbbbbb: {field} {target}, which does not exist")]


def test_check_2_links_that_resolve_pass() -> None:
    new = decision(
        id="d-bbbbbb",
        decided_by="author",
        changes=(Change(SPEC, Action.EDIT),),
        replaces=("d-aaaaaa",),
        narrows=("d-aaaaaa",),
        confirms=("d-aaaaaa",),
    )
    assert check_state(world(new)).ok


def test_check_2_one_problem_per_unresolved_link() -> None:
    snap = world(decision(id="d-bbbbbb", replaces=("d-yyyyyy", "d-zzzzzz", "d-zzzzzz")))
    assert [m for _, m in lines(snap)] == [
        "d-bbbbbb: replaces d-yyyyyy, which does not exist",
        "d-bbbbbb: replaces d-zzzzzz, which does not exist",
    ]


def test_check_2_duplicate_id_from_load_is_reported() -> None:
    first, second = decision(id="d-aaaaaa", title="First"), decision(id="d-aaaaaa", title="Second")
    snap = load(Tree(None, files_of(first) | files_of(second), frozenset()))
    assert [p.check for p in check_state(snap).problems] == [2, 2]


def test_check_2_codes_compared_without_case() -> None:
    snap = world(decision(id="d-bbbbbb", code="ITEM-1"), entry(id="s-bbbbbb", code="item-1"))
    snap = replace(snap, areas={"storage": area(order=(SPEC, "s-bbbbbb"))})
    assert [m for _, m in lines(snap)] == [
        "d-bbbbbb: code ITEM-1 is shared with another record, compared without regard to case",
        "s-bbbbbb: code item-1 is shared with another record, compared without regard to case",
    ]


def test_check_2_distinct_codes_pass() -> None:
    snap = world(decision(id="d-bbbbbb", code="ITEM-1"), decision(id="d-cccccc", code="ITEM-2"))
    assert check_state(snap).ok


def test_check_2_listed_attachment_missing() -> None:
    snap = world(decision(id="d-bbbbbb", attachments=("run.log",)))
    assert lines(snap) == [
        (2, "d-bbbbbb: lists attachment run.log, which does not exist" + REMEDY_ATTACH)
    ]


def test_check_2_listed_attachment_resolves_below_the_decision_folder() -> None:
    snap = world(decision(id="d-bbbbbb", attachments=("run.log",)))
    held = frozenset({"lodge/attachments/d-bbbbbb/run.log"})
    assert check_state(replace(snap, attachments=held)).ok


@pytest.mark.parametrize(
    "held", ["lodge/attachments/run.log", "lodge/attachments/d-cccccc/run.log", "d-bbbbbb/run.log"]
)
def test_check_2_listed_attachment_elsewhere_does_not_count(held: str) -> None:
    snap = world(decision(id="d-bbbbbb", attachments=("run.log",)))
    assert not check_state(replace(snap, attachments=frozenset({held}))).ok


@pytest.mark.parametrize("field", ["replaces", "narrows", "confirms"])
def test_check_2_decision_linking_to_itself(field: str) -> None:
    snap = world(decision(id="d-bbbbbb", decided_by="author", **{field: ("d-bbbbbb",)}))
    assert lines(snap) == [(2, f"d-bbbbbb: {field} itself")]


def test_check_3_author_decision_without_quote() -> None:
    snap = world(decision(id="d-bbbbbb", decided_by="author", quote=None))
    assert lines(snap) == [
        (
            3,
            "d-bbbbbb: decided_by is author, but there is no quote" + REMEDY_CHECK_3,
        )
    ]


@pytest.mark.parametrize("key", ["where", "when"])
def test_check_3_empty_where_or_when(key: str) -> None:
    quote = replace(Quote("Do it.", "a session", "2026-10-28 10:00"), **{key: " "})
    snap = world(decision(id="d-bbbbbb", decided_by="author", quote=quote))
    assert lines(snap) == [(3, f"d-bbbbbb: quote.{key} is empty")]


def test_check_3_imported_author_decision_needs_no_quote() -> None:
    imported = decision(id="d-bbbbbb", decided_by="author", imported_from=Imported("n.md", "H"))
    assert imported.quote is None
    assert check_state(world(imported)).ok


@pytest.mark.parametrize("value", ["Author", "the author", " author", "author (relayed)", "AUTHOR"])
def test_check_3_author_lookalike(value: str) -> None:
    snap = world(decision(id="d-bbbbbb", decided_by=value, quote=None))
    message = f"d-bbbbbb: decided_by is {value}; "
    message += "write author exactly, with a quote, or use your own role"
    assert lines(snap) == [(3, message)]


def test_check_3_confirms_on_a_non_author_decision() -> None:
    snap = world(decision(id="d-bbbbbb", decided_by="coordinator", confirms=("d-aaaaaa",)))
    assert lines(snap) == [
        (3, "d-bbbbbb: confirms is for author decisions, but decided_by is coordinator")
    ]


def test_check_7_entry_missing_from_the_order() -> None:
    extra = entry(id="s-bbbbbb")
    assert lines(world(extra)) == [(7, "s-bbbbbb: is not listed in the order of area storage")]
    assert check_state(world(extra)).problems[0].path == new_record_path(extra)


def test_check_7_order_lists_an_entry_that_is_not_there() -> None:
    snap = world(area(order=(SPEC, "s-zzzzzz")))
    assert lines(snap) == [
        (7, "area storage: order lists s-zzzzzz, which is not a current entry of the area")
    ]


def test_check_7_order_lists_an_entry_of_another_area() -> None:
    snap = world(entry(id="s-bbbbbb", area="other"), area(name="other", order=("s-bbbbbb",)))
    snap = replace(snap, areas=dict(snap.areas) | {"storage": area(order=(SPEC, "s-bbbbbb"))})
    assert lines(snap) == [
        (7, "area storage: order lists s-bbbbbb, which is not a current entry of the area")
    ]


def test_check_7_order_lists_a_retired_entry() -> None:
    retire = decision(id="d-bbbbbb", date=at(1), changes=(Change(SPEC, Action.RETIRE),))
    assert lines(world(retire)) == [
        (7, "area storage: order lists s-aaaaaa, which is not a current entry of the area")
    ]
    assert check_state(world(retire, area(order=()))).ok


def test_check_7_order_lists_an_entry_twice() -> None:
    snap = world(area(order=(SPEC, SPEC)))
    assert lines(snap) == [(7, "area storage: order lists s-aaaaaa more than once")]


def test_check_7_folder_with_entries_has_no_area_file() -> None:
    snap = snapshot_of(entry(id=SPEC))
    assert lines(snap) == [(7, "area storage: has entries but no _area.md")]
    assert check_state(snap).problems[0].path == "lodge/spec/storage/_area.md"


def test_check_7_empty_area_needs_no_entries() -> None:
    assert check_state(snapshot_of(area())).ok
