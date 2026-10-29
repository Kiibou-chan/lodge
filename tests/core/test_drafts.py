import pytest
from samples import document

from lodge.core import (
    Area,
    Decision,
    Draft,
    Problem,
    Scope,
    SpecEntry,
    parse_draft,
    record_from_draft,
)

DECISION_DRAFT = document(
    ["kind: decision", 'title: "Keep transcripts"', "scope: process", "decided_by: coordinator"],
    "They are kept.\n\n## Reasoning\n\nBecause.",
)
SPEC_DRAFT = document(
    ["kind: spec", "area: storage", 'title: "Transcripts"', "base: 0123456789ab"], "They are kept."
)
AREA_DRAFT = document(
    ["kind: area", "name: storage", 'title: "Storage"', "order: [s-4kq1zm]"], "Intro."
)
DATE = "2026-10-29T09:30:00+01:00"


def drafted(text: str) -> Draft:
    result = parse_draft("draft.md", text)
    assert isinstance(result, Draft), result
    return result


def test_draft_without_id_or_date() -> None:
    draft = drafted(DECISION_DRAFT)
    assert draft.kind == "decision"
    assert draft.source == "draft.md"
    assert "id" not in draft.header
    assert "date" not in draft.header


def test_draft_keeps_header_and_body() -> None:
    draft = drafted(DECISION_DRAFT)
    assert draft.header == {
        "kind": "decision",
        "title": "Keep transcripts",
        "scope": "process",
        "decided_by": "coordinator",
    }
    assert draft.body == "They are kept.\n\n## Reasoning\n\nBecause."


def test_record_from_draft_fills_id_date_area() -> None:
    decision = record_from_draft(drafted(DECISION_DRAFT), "d-3m8qk2", DATE, None)
    assert decision == Decision(
        id="d-3m8qk2",
        title="Keep transcripts",
        scope=Scope.PROCESS,
        decided_by="coordinator",
        date=DATE,
        statement="They are kept.",
        reasoning="Because.",
    )
    entry = record_from_draft(drafted(SPEC_DRAFT), "s-4kq1zm", None, None)
    assert entry == SpecEntry("s-4kq1zm", "storage", "Transcripts", "They are kept.")


def test_existing_entry_takes_its_area_from_the_caller() -> None:
    text = document(["kind: spec", 'title: "Transcripts"', "base: 0123456789ab"], "They are kept.")
    entry = record_from_draft(drafted(text), "s-4kq1zm", None, "storage")
    assert entry == SpecEntry("s-4kq1zm", "storage", "Transcripts", "They are kept.")
    moved = record_from_draft(drafted(SPEC_DRAFT), "s-4kq1zm", None, "process")
    assert isinstance(moved, Problem)
    assert "area" in moved.message


def test_draft_carries_base_and_area() -> None:
    draft = drafted(SPEC_DRAFT)
    assert draft.header["base"] == "0123456789ab"
    assert draft.header["area"] == "storage"
    assert draft.kind == "spec"


def test_area_draft() -> None:
    draft = drafted(AREA_DRAFT)
    assert draft.kind == "area"
    assert draft.header["name"] == "storage"
    assert record_from_draft(draft, "", None, None) == Area(
        "storage", "Storage", "Intro.", ("s-4kq1zm",)
    )
    named = document(["kind: area", 'title: "Storage"'], "")
    assert record_from_draft(drafted(named), "", None, "storage") == Area(
        "storage", "Storage", "", ()
    )
    assert isinstance(record_from_draft(drafted(named), "", None, None), Problem)


def test_draft_non_utf8_is_problem() -> None:
    raw = b"---\nkind: spec\n---\n\nbad \xff byte\n"
    text = raw.decode("utf-8", errors="surrogateescape")
    result = parse_draft("draft.md", text)
    assert isinstance(result, Problem)
    assert result.path == "draft.md"
    assert result.check == 1
    assert "UTF-8" in result.message


@pytest.mark.parametrize(
    ("text", "word"),
    [
        ("no fence", "---"),
        (document(['title: "T"']), "kind"),
        (document(["kind: note"]), "kind"),
        (document(["kind: decision", "replace: [d-8rw0te]"]), "replace"),
        (document(["kind: decision", "area: storage"]), "area"),
        (document(["kind: spec", "scope: product"]), "scope"),
        (document(["kind: area", "base: 0123456789ab", "order: []", "id: s-4kq1zm"]), "id"),
        (document(["kind: decision", "title: a: b"]), "YAML"),
    ],
)
def test_draft_syntax_problems(text: str, word: str) -> None:
    result = parse_draft("draft.md", text)
    assert isinstance(result, Problem)
    assert word in result.message


def test_draft_may_not_set_a_date_unless_imported() -> None:
    header = [
        "kind: decision",
        'title: "T"',
        "scope: product",
        "decided_by: x",
        "date: 2026-10-01T00:00:00+00:00",
    ]
    refused = record_from_draft(drafted(document(header)), "d-3m8qk2", DATE, None)
    assert isinstance(refused, Problem)
    assert "date" in refused.message
    imported = [*header, 'imported_from: {file: "a.md", heading: "H"}']
    kept = record_from_draft(drafted(document(imported)), "d-3m8qk2", DATE, None)
    assert isinstance(kept, Decision)
    assert kept.date == "2026-10-01T00:00:00+00:00"
    existing = record_from_draft(drafted(document(header)), "d-3m8qk2", None, None)
    assert isinstance(existing, Decision)


def test_draft_missing_a_required_field_is_a_problem() -> None:
    text = document(["kind: decision", 'title: "T"', "scope: product"])
    result = record_from_draft(drafted(text), "d-3m8qk2", DATE, None)
    assert isinstance(result, Problem)
    assert result.path == "draft.md"
    assert "decided_by" in result.message
    no_date = record_from_draft(drafted(DECISION_DRAFT), "d-3m8qk2", None, None)
    assert isinstance(no_date, Problem)
    assert "date" in no_date.message


def test_draft_id_must_match_the_given_one() -> None:
    text = document(["kind: spec", "id: s-4kq1zm", "area: storage", 'title: "T"'])
    assert isinstance(record_from_draft(drafted(text), "s-4kq1zm", None, None), SpecEntry)
    other = record_from_draft(drafted(text), "s-0abcde", None, None)
    assert isinstance(other, Problem)
    assert "id" in other.message


def test_spec_draft_without_an_area_is_a_problem() -> None:
    text = document(["kind: spec", 'title: "T"'])
    result = record_from_draft(drafted(text), "s-4kq1zm", None, None)
    assert isinstance(result, Problem)
    assert "area" in result.message


def test_deep_nesting_in_a_draft_is_a_problem() -> None:
    nested = "[" * 1000 + "]" * 1000
    result = parse_draft("draft.md", document(["kind: decision", f"work_item: {nested}"]))
    assert isinstance(result, Problem)
    assert result.path == "draft.md"
    assert "nested" in result.message


def test_problem_from_a_draft_carries_the_key_line() -> None:
    text = document(["kind: decision", "title: [a, b]", "scope: product", "decided_by: x"])
    result = record_from_draft(drafted(text), "d-3m8qk2", DATE, None)
    assert isinstance(result, Problem)
    assert result.line == 3
    spec = document(["kind: spec", 'title: "T"', "area: Bad Area"])
    found = record_from_draft(drafted(spec), "s-4kq1zm", None, None)
    assert isinstance(found, Problem)
    assert found.line == 4


def test_draft_keeps_the_indentation_of_its_first_line() -> None:
    text = document(["kind: spec", "area: storage", 'title: "T"'], "  indented first line")
    entry = record_from_draft(drafted(text), "s-4kq1zm", None, None)
    assert isinstance(entry, SpecEntry)
    assert entry.statement == "  indented first line"
    assert drafted(text).body == "  indented first line"


def test_draft_with_a_blank_title_is_a_problem() -> None:
    text = document(["kind: decision", 'title: " "', "scope: product", "decided_by: x"])
    result = record_from_draft(drafted(text), "d-3m8qk2", DATE, None)
    assert isinstance(result, Problem)
    assert "title" in result.message
