from builders import at, decision, entry, snapshot_of
from checks import NOTES

from lodge.core import (
    Action,
    Change,
    CheckResult,
    NumberHandle,
    Problem,
    Quote,
    Scope,
    derive,
    failing_ids,
    format_level1,
    format_level3,
    level1,
    level2,
    level2_views,
    level3,
    unrecorded_problems,
)

NONE: frozenset[str] = frozenset()
CHANGE = (Change("s-aaaaaa", Action.EDIT),)


def test_level1_status_who_flags() -> None:
    author = decision(id="d-aaaaaa", decided_by="author", date=at(0), scope=Scope.PROCESS)
    agent = decision(id="d-bbbbbb", date=at(1), replaces=("d-aaaaaa",), title="T", statement="S")
    s = snapshot_of(author, agent)
    d = derive(s)
    got = level1(s, d, "d-bbbbbb", frozenset({"d-bbbbbb"}))
    assert (got.kind, got.status, got.decided_by, got.scope, got.area) == (
        "decision",
        "current",
        "coordinator",
        "product",
        None,
    )
    assert (got.title, got.statement, got.date) == ("T", "S", at(1))
    assert got.flags == ("awaiting the author", "fails check")
    old = level1(s, d, "d-aaaaaa", NONE)
    assert old.status == "replaced"
    assert old.flags == ("replaced by d-bbbbbb", "awaiting the author on d-bbbbbb")


def test_author_decision_behind_an_agent_entry_edit_awaits_the_author() -> None:
    create = (Change("s-aaaaaa", Action.CREATE),)
    hers = decision(id="d-aaaaaa", decided_by="author", date=at(0), changes=create)
    edit = decision(id="d-bbbbbb", date=at(1), changes=CHANGE)
    s = snapshot_of(entry(id="s-aaaaaa"), hers, edit)
    d = derive(s)
    assert d.awaiting_author == {"d-bbbbbb"}
    assert level1(s, d, "d-aaaaaa", NONE).flags == ("awaiting the author on d-bbbbbb",)
    assert "awaiting the author on d-bbbbbb" in level1(s, d, "s-aaaaaa", NONE).flags


def test_agent_decision_behind_an_agent_entry_edit_is_not_flagged() -> None:
    create = (Change("s-aaaaaa", Action.CREATE),)
    first = decision(id="d-aaaaaa", date=at(0), changes=create)
    edit = decision(id="d-bbbbbb", date=at(1), changes=CHANGE)
    s = snapshot_of(entry(id="s-aaaaaa"), first, edit)
    assert level1(s, derive(s), "d-aaaaaa", NONE).flags == ()


def test_narrowed_decision_flagged_at_level1() -> None:
    old = decision(id="d-aaaaaa", date=at(0))
    new = decision(id="d-bbbbbb", date=at(1), narrows=("d-aaaaaa",))
    newer = decision(id="d-cccccc", date=at(2), narrows=("d-aaaaaa",))
    s = snapshot_of(old, new, newer)
    got = level1(s, derive(s), "d-aaaaaa", NONE)
    assert got.status == "current"
    assert got.flags == ("narrowed by d-cccccc, d-bbbbbb",)


def test_replaced_decision_names_successor_at_level1() -> None:
    old = decision(id="d-aaaaaa", date=at(0))
    new = decision(id="d-bbbbbb", date=at(1), replaces=("d-aaaaaa",))
    s = snapshot_of(old, new)
    assert level1(s, derive(s), "d-aaaaaa", NONE).flags == ("replaced by d-bbbbbb",)


def test_entry_level1_takes_who_from_latest_decision() -> None:
    spec = entry(id="s-aaaaaa", area="storage", code="SPEC-1")
    first = decision(id="d-aaaaaa", date=at(0), decided_by="reviewer", changes=CHANGE)
    last = decision(id="d-bbbbbb", date=at(5), decided_by="advisor", changes=CHANGE)
    kill = decision(id="d-cccccc", date=at(9), changes=(Change("s-aaaaaa", Action.RETIRE),))
    s = snapshot_of(spec, first, last)
    got = level1(s, derive(s), "s-aaaaaa", NONE)
    assert (got.kind, got.code, got.decided_by, got.date, got.scope, got.area) == (
        "spec",
        "SPEC-1",
        "advisor",
        at(5),
        None,
        "storage",
    )
    s = snapshot_of(spec, first, last, kill)
    got = level1(s, derive(s), "s-aaaaaa", NONE)
    assert got.status == "retired"
    assert got.flags == ("retired by d-cccccc",)
    bare = snapshot_of(entry(id="s-dddddd"))
    assert level1(bare, derive(bare), "s-dddddd", NONE).decided_by is None


def test_unquoted_import_flags() -> None:
    unquoted = decision(id="d-aaaaaa", decided_by="author", imported_from=NOTES)
    quoted = decision(
        id="d-bbbbbb", decided_by="author", imported_from=NOTES, quote=Quote("Yes.", "a", "b")
    )
    agent = decision(id="d-cccccc", imported_from=NOTES)
    spec = entry(id="s-aaaaaa", imported_from=NOTES)
    s = snapshot_of(unquoted, quoted, agent, spec)
    d = derive(s)
    assert level1(s, d, "d-aaaaaa", NONE).flags == ("imported", "unquoted")
    assert level1(s, d, "d-bbbbbb", NONE).flags == ("imported",)
    assert level1(s, d, "d-cccccc", NONE).flags == ("imported",)
    assert level1(s, d, "s-aaaaaa", NONE).flags == ("imported",)


def test_awaiting_flag_on_touched_entry() -> None:
    spec = entry(id="s-aaaaaa")
    author = decision(id="d-aaaaaa", decided_by="author", date=at(0), changes=CHANGE)
    agent = decision(id="d-bbbbbb", date=at(1), changes=CHANGE)
    s = snapshot_of(spec, author, agent)
    assert level1(s, derive(s), "s-aaaaaa", NONE).flags == ("awaiting the author on d-bbbbbb",)


def test_failing_ids_maps_paths() -> None:
    a, b = decision(id="d-aaaaaa"), entry(id="s-aaaaaa")
    s = snapshot_of(a, b)
    result = CheckResult(
        (
            Problem(s.paths["d-aaaaaa"], 3, "x"),
            Problem(s.paths["d-aaaaaa"], 2, "y"),
            Problem(s.paths["s-aaaaaa"], 2, "z"),
            Problem("lodge/spec/storage/_area.md", 7, "w"),
        ),
        (),
    )
    assert failing_ids(s, result) == {"d-aaaaaa", "s-aaaaaa"}


def test_unrecorded_problem_for_unparsable_file() -> None:
    s = snapshot_of(decision(id="d-aaaaaa"))
    broken = Problem("lodge/decisions/d-zzzzzz-broken.md", 1, "no fence", 1)
    held = Problem(s.paths["d-aaaaaa"], 3, "x")
    result = CheckResult((held, broken), ())
    assert unrecorded_problems(s, result) == (broken,)
    assert failing_ids(s, result) == {"d-aaaaaa"}


def test_level2_of_entry() -> None:
    spec = entry(id="s-aaaaaa", title="Spec")
    old = decision(id="d-aaaaaa", date=at(0), title="Old", changes=CHANGE, reasoning="Because.")
    new = decision(id="d-bbbbbb", date=at(1), title="New", changes=CHANGE, decided_by="author")
    s = snapshot_of(spec, old, new)
    d = derive(s)
    assert level2(s, d, "d-aaaaaa", NONE) == "Because."
    assert level2(s, d, "s-aaaaaa", NONE) == (
        "d-bbbbbb · current · author · 2026-10-28 · product\nNew\n\n"
        "d-aaaaaa · current · coordinator · 2026-10-28 · product\nOld"
    )
    bare = snapshot_of(entry(id="s-dddddd"))
    assert level2(bare, derive(bare), "s-dddddd", NONE) == ""


def test_level2_views_of_entry_are_level1_views_newest_first() -> None:
    spec = entry(id="s-aaaaaa", title="Spec")
    old = decision(id="d-aaaaaa", date=at(0), changes=CHANGE)
    new = decision(id="d-bbbbbb", date=at(1), changes=CHANGE, decided_by="author")
    s = snapshot_of(spec, old, new)
    d = derive(s)
    assert [v.id for v in level2_views(s, d, "s-aaaaaa", NONE)] == ["d-bbbbbb", "d-aaaaaa"]
    assert level2_views(s, d, "d-aaaaaa", NONE) == ()


def test_level3_reverse_links_with_status() -> None:
    spec = entry(id="s-aaaaaa")
    base = decision(id="d-aaaaaa", date=at(0), changes=CHANGE, work_item="plan.md")
    mid = decision(id="d-bbbbbb", date=at(1), narrows=("d-aaaaaa",), attachments=("log.txt",))
    top = decision(
        id="d-cccccc", date=at(2), replaces=("d-aaaaaa",), changes=CHANGE, decided_by="author"
    )
    confirm = decision(id="d-dddddd", date=at(3), confirms=("d-bbbbbb",), decided_by="author")
    s = snapshot_of(spec, base, mid, top, confirm)
    d = derive(s)
    got = level3(s, d, "d-aaaaaa")
    assert got.work_item == "plan.md"
    assert got.links == (
        ("changes (edit)", "s-aaaaaa", "current"),
        ("replaced by", "d-cccccc", "current"),
        ("narrowed by", "d-bbbbbb", "current"),
    )
    got = level3(s, d, "d-bbbbbb")
    assert got.attachments == ("log.txt",)
    assert got.links == (
        ("narrows", "d-aaaaaa", "replaced"),
        ("confirmed by", "d-dddddd", "current"),
    )
    assert level3(s, d, "d-cccccc").links == (
        ("changes (edit)", "s-aaaaaa", "current"),
        ("replaces", "d-aaaaaa", "replaced"),
    )
    assert level3(s, d, "d-cccccc").quote == top.quote
    assert level3(s, d, "d-dddddd").links == (("confirms", "d-bbbbbb", "current"),)
    assert level3(s, d, "s-aaaaaa").links == (
        ("changed by", "d-cccccc", "current"),
        ("changed by", "d-aaaaaa", "replaced"),
    )


def test_level3_unknown_target_and_provenance() -> None:
    nums = decision(id="d-aaaaaa", replaces=("d-zzzzzz",), imported_from=NOTES)
    s = snapshot_of(nums)
    got = level3(s, derive(s), "d-aaaaaa")
    assert got.links == (("replaces", "d-zzzzzz", "unknown"),)
    assert got.imported_from == NOTES


def test_format_level1_exact_text() -> None:
    old = decision(
        id="d-3m8qk2",
        code="ITEM-1",
        scope=Scope.PROCESS,
        decided_by="author",
        date="2026-10-28T09:30:00+01:00",
        title="Keep it short",
        statement="Short and searchable.",
    )
    new = decision(id="d-bbbbbb", replaces=("d-3m8qk2",), date=at(5))
    s = snapshot_of(old, new)
    d = derive(s)
    assert format_level1(level1(s, d, "d-3m8qk2", NONE)) == (
        "d-3m8qk2 ITEM-1 · replaced · author · 2026-10-28 · process · replaced by d-bbbbbb · "
        "awaiting the author on d-bbbbbb\nKeep it short\n\nShort and searchable.\n\n"
        'quote: "Do it." (a session, 2026-10-28 10:00)'
    )
    spec = entry(id="s-aaaaaa", title="Spec", statement="Holds.", area="storage")
    s = snapshot_of(spec)
    assert format_level1(level1(s, derive(s), "s-aaaaaa", NONE)) == (
        "s-aaaaaa · current · no decision · storage\nSpec\n\nHolds."
    )


def test_format_level3_exact_text() -> None:
    d1 = decision(
        id="d-aaaaaa",
        decided_by="author",
        quote=Quote("Do it.", "a session", "2026-10-28 10:00"),
        numbers=(NumberHandle("80", "limits.words"),),
        work_item="plan.md",
        attachments=("log.txt",),
        imported_from=NOTES,
        replaces=("d-bbbbbb",),
        date=at(5),
    )
    s = snapshot_of(d1, decision(id="d-bbbbbb"))
    text = format_level3(level3(s, derive(s), "d-aaaaaa"))
    assert text == (
        'quote: "Do it." (a session, 2026-10-28 10:00)\n'
        "numbers: 80 (limits.words)\n"
        "work item: plan.md\n"
        "attachments: log.txt\n"
        "imported from: notes.md, A heading\n"
        "replaces: d-bbbbbb (replaced)"
    )
