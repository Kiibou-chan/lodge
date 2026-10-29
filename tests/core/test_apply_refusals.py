import pytest
from applying import (
    applied,
    apply,
    area_text,
    decision_text,
    problems,
    spec_text,
    state,
)
from builders import area as make_area
from builders import decision, entry

from lodge.core import (
    Decision,
    Imported,
    Scope,
    StaleBase,
    content_hash,
    new_record_path,
    parse_record,
)


def test_id_count_must_match_new_decisions() -> None:
    s, tree = state()
    with pytest.raises(ValueError, match="2 new decision drafts but 1 IDs"):
        apply(s, tree, decision_text(), decision_text(), ids=("d-aaaaaa",))


def test_stale_base_is_problem_naming_both() -> None:
    old = entry(id="s-aaaaaa")
    s, tree = state(old, make_area(order=("s-aaaaaa",)))
    actual = content_hash(tree.files[new_record_path(old)])
    found = problems(apply(s, tree, spec_text("id: s-aaaaaa", "base: 0123456789ab")))
    assert len(found) == 1 and isinstance(found[0], StaleBase)
    assert found[0].path == "draft0.md"
    assert "0123456789ab" in found[0].message and actual in found[0].message


def test_edit_without_base_is_problem() -> None:
    old = entry(id="s-aaaaaa")
    s, tree = state(old, make_area(order=("s-aaaaaa",)))
    found = problems(apply(s, tree, spec_text("id: s-aaaaaa")))
    assert found[0].path == "draft0.md" and "base" in found[0].message
    assert not isinstance(found[0], StaleBase)


def test_import_needs_flag() -> None:
    s, tree = state()
    text = decision_text("imported_from: {file: notes.md, heading: Old}", "date: 2026-01-02")
    found = problems(apply(s, tree, text, ids=("d-aaaaaa",)))
    assert [p.path for p in found] == ["draft0.md"] and "--import" in found[0].message
    result = applied(apply(s, tree, text, ids=("d-aaaaaa",), importing=True))
    d = parse_record("x", result.files["lodge/decisions/d-aaaaaa-keep-transcripts.md"])
    assert isinstance(d, Decision) and d.date == "2026-01-02T00:00:00+00:00"


def test_imported_entry_needs_flag() -> None:
    s, tree = state(make_area())
    text = spec_text("id: s-aaaaaa", "area: storage", "imported_from: {file: notes.md, heading: H}")
    assert "--import" in problems(apply(s, tree, text))[0].message


def test_date_in_new_draft_refused() -> None:
    s, tree = state()
    found = problems(
        apply(s, tree, decision_text("date: 2026-10-29T10:00:00+01:00"), ids=("d-aaaaaa",))
    )
    assert [p.path for p in found] == ["draft0.md"] and "date" in found[0].message


def test_decision_with_unknown_id_refused() -> None:
    s, tree = state()
    found = problems(apply(s, tree, decision_text("id: d-zzzzzz")))
    assert found[0].path == "draft0.md" and "d-zzzzzz" in found[0].message


def test_entry_statement_with_reasoning_heading_refused() -> None:
    s, tree = state(make_area())
    found = problems(
        apply(
            s,
            tree,
            spec_text("id: s-aaaaaa", "area: storage", body="Text.\n\n## Reasoning\n\nWhy."),
        )
    )
    assert found[0].path == "draft0.md" and "Reasoning" in found[0].message


def test_entry_without_area_refused() -> None:
    s, tree = state()
    found = problems(apply(s, tree, spec_text("id: s-aaaaaa")))
    assert found[0].path == "draft0.md" and "area" in found[0].message


def test_entry_without_id_refused() -> None:
    s, tree = state(make_area())
    found = problems(apply(s, tree, spec_text("area: storage")))
    assert found[0].path == "draft0.md" and "lodge id s" in found[0].message


def test_entry_in_unknown_area_refused() -> None:
    s, tree = state()
    found = problems(apply(s, tree, spec_text("id: s-aaaaaa", "area: storage")))
    assert found[0].path == "draft0.md" and "storage" in found[0].message


def test_area_change_refused() -> None:
    old = entry(id="s-aaaaaa")
    s, tree = state(old, make_area(order=("s-aaaaaa",)), make_area(name="other", title="O"))
    base = content_hash(tree.files[new_record_path(old)])
    found = problems(apply(s, tree, spec_text("id: s-aaaaaa", "area: other", f"base: {base}")))
    assert found[0].path == "draft0.md" and "storage" in found[0].message


def test_two_drafts_for_one_record_refused() -> None:
    s, tree = state(make_area())
    found = problems(
        apply(
            s,
            tree,
            spec_text("id: s-aaaaaa", "area: storage"),
            spec_text("id: s-aaaaaa", "area: storage"),
        )
    )
    assert [p.path for p in found] == ["draft1.md"]


def test_every_problem_names_its_draft() -> None:
    s, tree = state()
    found = problems(apply(s, tree, spec_text("id: s-aaaaaa"), decision_text("id: d-zzzzzz")))
    assert [p.path for p in found] == ["draft0.md", "draft1.md"]


def test_area_name_not_a_string_is_problem() -> None:
    s, tree = state()
    for value in ("[storage]", "{a: b}"):
        found = problems(apply(s, tree, area_text(f"name: {value}")))
        assert [p.path for p in found] == ["draft0.md"] and "name" in found[0].message


def test_entry_created_and_retired_in_one_add_not_in_order() -> None:
    s, tree = state(make_area())
    result = applied(
        apply(
            s,
            tree,
            decision_text("changes:", "  - {entry: s-aaaaaa, action: retire}"),
            spec_text("id: s-aaaaaa", "area: storage"),
            ids=("d-bbbbbb",),
        )
    )
    assert "lodge/spec/storage/_area.md" not in result.files


def test_base_on_new_decision_refused() -> None:
    s, tree = state()
    found = problems(apply(s, tree, decision_text("base: 0123456789ab"), ids=("d-aaaaaa",)))
    assert found[0].path == "draft0.md"
    assert found[0].message == (
        "base is for edits, but this draft has no id and would add a new decision; "
        "keep the id that lodge draft printed to edit one"
    )


def test_base_on_entry_that_does_not_exist_refused() -> None:
    s, tree = state(make_area())
    found = problems(
        apply(s, tree, spec_text("id: s-aaaaaa", "area: storage", "base: 0123456789ab"))
    )
    assert found[0].message == "base is for edits, but no entry s-aaaaaa exists to edit"


def test_base_on_new_area_refused() -> None:
    s, tree = state()
    found = problems(apply(s, tree, area_text("name: storage", "base: 0123456789ab")))
    assert found[0].message == "base is for edits, but no area storage exists to edit"


def test_stale_base_message_says_to_redo_the_change() -> None:
    old = entry(id="s-aaaaaa")
    s, tree = state(old, make_area(order=("s-aaaaaa",)))
    actual = content_hash(tree.files[new_record_path(old)])
    found = problems(apply(s, tree, spec_text("id: s-aaaaaa", "base: 0123456789ab")))
    assert found[0].message == (
        f"the base 0123456789ab differs from {actual}, the hash of {new_record_path(old)} now; "
        "it changed since the draft was made, so print it again with lodge draft s-aaaaaa, "
        "make the change on that print, and add it"
    )


def test_edit_changing_imported_from_has_its_own_message() -> None:
    old = entry(id="s-aaaaaa", imported_from=Imported("notes.md", "H"))
    s, tree = state(old, make_area(order=("s-aaaaaa",)))
    base = content_hash(tree.files[new_record_path(old)])
    for line in ("imported_from: {file: other.md, heading: H}", None):
        header = ["id: s-aaaaaa", f"base: {base}", *([line] if line else [])]
        found = problems(apply(s, tree, spec_text(*header)))
        assert found[0].message == (
            "this draft changes imported_from of s-aaaaaa; keep it as lodge draft printed it"
        )


def test_edit_of_decision_changing_imported_from_has_its_own_message() -> None:
    old = decision(id="d-aaaaaa", title="Keep transcripts", scope=Scope.PROCESS)
    s, tree = state(old)
    base = content_hash(tree.files[new_record_path(old)])
    text = decision_text(
        "id: d-aaaaaa",
        f"date: {old.date}",
        f"base: {base}",
        "imported_from: {file: a.md, heading: H}",
    )
    found = problems(apply(s, tree, text))
    assert found[0].message == (
        "this draft changes imported_from of d-aaaaaa; keep it as lodge draft printed it"
    )


def test_id_of_the_wrong_shape_says_so() -> None:
    s, tree = state(make_area(), entry(id="s-bbbbbb"))
    entry_ids = "a specification entry ID; "
    decision_ids = "a decision ID; "
    cases = (
        (spec_text("id: S-BBBBBB", "base: 0123456789ab"), "'S-BBBBBB'", entry_ids),
        (spec_text("id: d-aaaaaa", "area: storage"), "'d-aaaaaa'", entry_ids),
        (spec_text("id: s-bbbbbi", "area: storage"), "'s-bbbbbi'", entry_ids),
        (decision_text("id:"), "''", decision_ids),
        (decision_text("id: D-AAAAAA"), "'D-AAAAAA'", decision_ids),
        (decision_text("id: s-bbbbbb"), "'s-bbbbbb'", decision_ids),
    )
    expected = (
        "IDs are lower case, like s-4kq1zm",
        "an entry ID starts with s-, like s-4kq1zm",
        "an ID is s- and six characters from 0-9 and a-z without i, l, o, and u, like s-4kq1zm",
        "an ID is d- and six characters from 0-9 and a-z without i, l, o, and u, like d-3m8qk2",
        "IDs are lower case, like d-3m8qk2",
        "a decision ID starts with d-, like d-3m8qk2",
    )
    for (text, given, kind), rest in zip(cases, expected, strict=True):
        found = problems(apply(s, tree, text))
        assert found[0].message == f"id {given} is not {kind}{rest}"


def test_area_of_the_wrong_shape_says_so() -> None:
    s, tree = state(make_area())
    found = problems(apply(s, tree, spec_text("id: s-aaaaaa", "area: [storage]")))
    assert found[0].message == "area must be one name, not ['storage']"
