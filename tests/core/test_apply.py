from datetime import datetime

from applying import (
    NOW,
    applied,
    apply,
    area_text,
    decision_text,
    problems,
    spec_text,
    state,
)
from builders import area as make_area
from builders import at, decision, entry
from samples import document

from lodge.core import (
    Action,
    Area,
    Change,
    CoreSettings,
    Decision,
    Imported,
    Scope,
    SpecEntry,
    StaleBase,
    Tree,
    area_path,
    check_change,
    content_hash,
    load,
    new_record_path,
    parse_area,
    parse_record,
)


def test_new_decision_and_entry_and_area() -> None:
    s, tree = state()
    result = applied(
        apply(
            s,
            tree,
            decision_text("changes:", "  - {entry: s-aaaaaa, action: create}"),
            spec_text("id: s-aaaaaa", "area: storage"),
            area_text("name: storage"),
            ids=("d-bbbbbb",),
        )
    )
    assert result.ids == ("d-bbbbbb", "s-aaaaaa")
    assert sorted(result.files) == [
        "lodge/decisions/d-bbbbbb-keep-transcripts.md",
        "lodge/spec/storage/_area.md",
        "lodge/spec/storage/s-aaaaaa-transcripts.md",
    ]
    d = parse_record("x", result.files["lodge/decisions/d-bbbbbb-keep-transcripts.md"])
    assert isinstance(d, Decision)
    assert (d.id, d.date) == ("d-bbbbbb", NOW)
    area = parse_area("lodge/spec/storage/_area.md", result.files["lodge/spec/storage/_area.md"])
    assert area == Area("storage", "Storage", "Intro.", ("s-aaaaaa",))
    after = load(Tree(None, {**tree.files, **result.files}))
    assert check_change(s, after, CoreSettings(), datetime.fromisoformat(NOW)).ok


def test_new_entry_appended_to_existing_area_order() -> None:
    old = entry(id="s-aaaaaa", title="Old")
    s, tree = state(old, make_area(order=("s-aaaaaa",)))
    result = applied(
        apply(
            s,
            tree,
            decision_text("changes:", "  - {entry: s-cccccc, action: create}"),
            spec_text("id: s-cccccc", "area: storage"),
            ids=("d-bbbbbb",),
        )
    )
    area = parse_area("lodge/spec/storage/_area.md", result.files["lodge/spec/storage/_area.md"])
    assert isinstance(area, Area)
    assert area.order == ("s-aaaaaa", "s-cccccc")
    assert area.title == "Storage"


def test_area_draft_already_listing_entry_not_doubled() -> None:
    s, tree = state()
    result = applied(
        apply(
            s,
            tree,
            spec_text("id: s-aaaaaa", "area: storage"),
            area_text("name: storage", "order: [s-aaaaaa]"),
        )
    )
    area = parse_area("lodge/spec/storage/_area.md", result.files["lodge/spec/storage/_area.md"])
    assert isinstance(area, Area) and area.order == ("s-aaaaaa",)


def test_new_ids_ascend_in_draft_order() -> None:
    s, tree = state()
    result = applied(
        apply(
            s,
            tree,
            decision_text(),
            decision_text(body="Second."),
            decision_text(body="Third."),
            ids=("d-cccccc", "d-aaaaaa", "d-bbbbbb"),
        )
    )
    assert result.ids == ("d-aaaaaa", "d-bbbbbb", "d-cccccc")


def test_edit_keeps_path_even_if_title_changes() -> None:
    old = entry(id="s-aaaaaa", title="Old title", statement="Old.")
    s, tree = state(old, make_area(order=("s-aaaaaa",)))
    base = content_hash(tree.files[new_record_path(old)])
    result = applied(
        apply(
            s,
            tree,
            spec_text("id: s-aaaaaa", f"base: {base}", body="New."),
        )
    )
    assert list(result.files) == [new_record_path(old)]
    new = parse_record(new_record_path(old), result.files[new_record_path(old)])
    assert isinstance(new, SpecEntry) and new.statement == "New." and new.title == "Transcripts"
    assert new.area == "storage"
    assert result.ids == ("s-aaaaaa",)


def test_retire_removes_from_order() -> None:
    a, b = entry(id="s-aaaaaa", title="A"), entry(id="s-bbbbbb", title="B")
    s, tree = state(a, b, make_area(order=("s-aaaaaa", "s-bbbbbb")))
    result = applied(
        apply(
            s,
            tree,
            decision_text("changes:", "  - {entry: s-aaaaaa, action: retire}"),
            ids=("d-cccccc",),
        )
    )
    area = parse_area("lodge/spec/storage/_area.md", result.files["lodge/spec/storage/_area.md"])
    assert isinstance(area, Area) and area.order == ("s-bbbbbb",)
    assert new_record_path(a) not in result.files
    after = load(Tree(None, {**tree.files, **result.files}))
    assert check_change(s, after, CoreSettings(), datetime.fromisoformat(NOW)).ok


def test_replacing_retirement_restores_order() -> None:
    a, b = entry(id="s-aaaaaa", title="A"), entry(id="s-bbbbbb", title="B")
    retire = decision(id="d-cccccc", date=at(2), changes=(Change("s-aaaaaa", Action.RETIRE),))
    s, tree = state(a, b, retire, make_area(order=("s-bbbbbb",)))
    result = applied(
        apply(s, tree, decision_text("replaces: [d-cccccc]"), ids=("d-dddddd",)),
    )
    area = parse_area("lodge/spec/storage/_area.md", result.files["lodge/spec/storage/_area.md"])
    assert isinstance(area, Area) and area.order == ("s-bbbbbb", "s-aaaaaa")
    after = load(Tree(None, {**tree.files, **result.files}))
    assert check_change(s, after, CoreSettings(), datetime.fromisoformat(NOW)).ok


def test_replacing_one_of_two_retirements_leaves_the_order() -> None:
    a = entry(id="s-aaaaaa", title="A")
    changes = (Change("s-aaaaaa", Action.RETIRE),)
    first = decision(id="d-cccccc", date=at(2), changes=changes)
    second = decision(id="d-dddddd", date=at(3), changes=changes)
    s, tree = state(a, first, second, make_area(order=()))
    result = applied(apply(s, tree, decision_text("replaces: [d-cccccc]"), ids=("d-eeeeee",)))
    assert list(result.files) == ["lodge/decisions/d-eeeeee-keep-transcripts.md"]


def test_untouched_area_not_written() -> None:
    s, tree = state(make_area(), make_area(name="other", title="Other"))
    result = applied(apply(s, tree, decision_text(), ids=("d-aaaaaa",)))
    assert list(result.files) == ["lodge/decisions/d-aaaaaa-keep-transcripts.md"]


def test_import_without_date_gets_the_add_date() -> None:
    s, tree = state()
    text = decision_text("imported_from: {file: notes.md, heading: Old}")
    result = applied(apply(s, tree, text, ids=("d-aaaaaa",), importing=True))
    d = parse_record("x", result.files["lodge/decisions/d-aaaaaa-keep-transcripts.md"])
    assert isinstance(d, Decision) and d.date == NOW


def test_edit_of_imported_entry_keeping_its_origin_needs_no_flag() -> None:
    old = entry(id="s-aaaaaa", imported_from=Imported("notes.md", "H"))
    s, tree = state(old, make_area(order=("s-aaaaaa",)))
    base = content_hash(tree.files[new_record_path(old)])
    text = spec_text("id: s-aaaaaa", f"base: {base}", "imported_from: {file: notes.md, heading: H}")
    assert applied(apply(s, tree, text)).ids == ("s-aaaaaa",)
    moved = spec_text(
        "id: s-aaaaaa", f"base: {base}", "imported_from: {file: other.md, heading: H}"
    )
    assert "changes imported_from of s-aaaaaa" in problems(apply(s, tree, moved))[0].message


def test_decision_reasoning_edit_keeps_date_and_passes() -> None:
    old = decision(
        id="d-aaaaaa",
        title="Keep transcripts",
        date=at(3),
        scope=Scope.PROCESS,
        statement="It is kept.",
        reasoning="one two three four five six",
    )
    s, tree = state(old)
    base = content_hash(tree.files[new_record_path(old)])
    text = document(
        [
            "id: d-aaaaaa",
            "kind: decision",
            'title: "Keep transcripts"',
            "scope: process",
            "decided_by: coordinator",
            f"date: {at(3)}",
            f"base: {base}",
        ],
        "It is kept.\n\n## Reasoning\n\none two three",
    )
    result = applied(apply(s, tree, text))
    assert list(result.files) == [new_record_path(old)] and result.ids == ("d-aaaaaa",)
    written = parse_record("x", result.files[new_record_path(old)])
    assert isinstance(written, Decision) and written.date == at(3)
    after = load(Tree(None, {**tree.files, **result.files}))
    checked = check_change(s, after, CoreSettings(), datetime.fromisoformat(NOW))
    assert checked.ok and any("shortened from 6 to 3" in n for n in checked.notes)


def test_decision_edit_changing_statement_is_judged_by_the_check() -> None:
    old = decision(id="d-aaaaaa", title="Keep transcripts", date=at(3), scope=Scope.PROCESS)
    s, tree = state(old)
    base = content_hash(tree.files[new_record_path(old)])
    text = document(
        [
            "id: d-aaaaaa",
            "kind: decision",
            'title: "Keep transcripts"',
            "scope: process",
            "decided_by: coordinator",
            f"date: {at(3)}",
            f"base: {base}",
        ],
        "Changed.",
    )
    result = applied(apply(s, tree, text))
    after = load(Tree(None, {**tree.files, **result.files}))
    assert not check_change(s, after, CoreSettings(), datetime.fromisoformat(NOW)).ok


def test_area_edit_needs_current_base_and_keeps_new_entries() -> None:
    old = entry(id="s-aaaaaa")
    area = make_area(order=("s-aaaaaa",), intro="Old intro.")
    s, tree = state(old, area)
    base = content_hash(tree.files[area_path("storage")])
    stale = problems(apply(s, tree, area_text("name: storage", "base: 0123456789ab")))
    assert isinstance(stale[0], StaleBase)
    result = applied(
        apply(
            s,
            tree,
            area_text("name: storage", f"base: {base}", "order: [s-aaaaaa]", body="New intro."),
            spec_text("id: s-cccccc", "area: storage"),
        )
    )
    written = parse_area("lodge/spec/storage/_area.md", result.files[area_path("storage")])
    assert isinstance(written, Area)
    assert (written.intro, written.order) == ("New intro.", ("s-aaaaaa", "s-cccccc"))
