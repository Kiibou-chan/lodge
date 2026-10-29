"""What the format keeps of free text: indentation, line breaks, emoji, and the slug cap."""

import json

import pytest
from samples import BASE_HEADER, DECISION_PATH, SPEC_PATH, document, replaced

from lodge.core import (
    Decision,
    Imported,
    Problem,
    Quote,
    Scope,
    SpecEntry,
    new_record_path,
    parse_record,
    slug,
    write_record,
)

STAMP = "2026-10-28T23:48:10+01:00"


def decision(**fields: object) -> Decision:
    base: dict[str, object] = {
        "id": "d-3m8qk2",
        "title": "T",
        "scope": Scope.PRODUCT,
        "decided_by": "x",
        "date": STAMP,
        "statement": "S.",
    }
    return Decision(**{**base, **fields})  # type: ignore[arg-type]


def test_deep_nesting_is_problem_1() -> None:
    nested = "[" * 1000 + "]" * 1000
    result = parse_record(DECISION_PATH, document([*BASE_HEADER, f"work_item: {nested}"]))
    assert isinstance(result, Problem)
    assert result.check == 1
    assert "nested" in result.message


def test_indentation_of_the_first_line_is_kept() -> None:
    header = [*BASE_HEADER]
    body = "    code first\n    more\n\n## Reasoning\n\n  - a\n  - b"
    result = parse_record(DECISION_PATH, document(header, body))
    assert isinstance(result, Decision)
    assert result.statement == "    code first\n    more"
    assert result.reasoning == "  - a\n  - b"
    assert write_record(result) == document(header, body)
    spec = parse_record(SPEC_PATH, document(["id: s-4kq1zm", "kind: spec", 'title: "T"'], "  x"))
    assert isinstance(spec, SpecEntry)
    assert spec.statement == "  x"


def test_blank_lines_around_a_block_are_dropped() -> None:
    result = parse_record(DECISION_PATH, document(BASE_HEADER, "\n \n  S.  \n\n"))
    assert isinstance(result, Decision)
    assert result.statement == "  S."


@pytest.mark.parametrize("key", ["title", "decided_by"])
def test_blank_required_string_is_problem_1(key: str) -> None:
    result = parse_record(DECISION_PATH, document(replaced(key, f'{key}: "   "')))
    assert isinstance(result, Problem)
    assert key in result.message


def test_quote_text_keeps_line_breaks_and_tabs() -> None:
    record = decision(quote=Quote("one\ntwo\r\n\tthree", "a session", "then"))
    text = write_record(record)
    assert '"one\\ntwo\\r\\n\\tthree"' in text
    assert parse_record(DECISION_PATH, text) == record
    assert write_record(record) == text


@pytest.mark.parametrize("field", ["where", "when"])
def test_other_quote_parts_keep_the_control_character_ban(field: str) -> None:
    parts = {"text": "t", "where": "w", "when": "n"} | {field: "a\nb"}
    with pytest.raises(ValueError, match=f"quote.{field}"):
        write_record(decision(quote=Quote(**parts)))


def test_quote_text_still_refuses_other_control_characters() -> None:
    with pytest.raises(ValueError, match=r"quote\.text"):
        write_record(decision(quote=Quote("a\x01b", "w", "n")))
    with pytest.raises(ValueError, match=r"quote\.text"):
        write_record(decision(quote=Quote("a\u2028b", "w", "n")))


def test_json_dumps_default_escapes_read_back_as_emoji() -> None:
    quote = "Ship it \U0001f600"
    assert "\\ud83d" in json.dumps(quote)
    line = f'quote: {{text: {json.dumps(quote)}, where: "w", when: "n"}}'
    result = parse_record(DECISION_PATH, document([*BASE_HEADER, line]))
    assert isinstance(result, Decision)
    assert result.quote == Quote(quote, "w", "n")


def test_lone_surrogate_escape_is_problem_1() -> None:
    result = parse_record(DECISION_PATH, document(replaced("title", 'title: "a\\ud83d"')))
    assert isinstance(result, Problem)
    assert "title" in result.message


def test_write_names_the_field_that_would_read_back_differently() -> None:
    imported = decision(date="2026-10-28", imported_from=Imported("a.md", "H"))
    with pytest.raises(ValueError, match="date"):
        write_record(imported)
    with pytest.raises(ValueError, match="statement"):
        write_record(decision(statement="a\r\nb"))
    with pytest.raises(ValueError, match="statement"):
        write_record(decision(statement="a\n \n"))


def test_slug_is_capped_at_a_word_boundary() -> None:
    assert slug("a" * 300) == "a" * 60
    six = " ".join(["abcdefghijklmno"] * 6)
    assert slug(six) == "-".join(["abcdefghijklmno"] * 3)
    short = "one two three four five six seven"
    assert slug(short) == "one-two-three-four-five-six"


def test_slug_cut_never_splits_a_word_unless_one_word_is_too_long() -> None:
    assert slug("x" * 59 + " yz") == "x" * 59
    assert slug("x" * 57 + " yz") == "x" * 57 + "-yz"
    assert slug("x" * 58 + " yz") == "x" * 58
    assert slug("x" * 60 + " yz") == "x" * 60
    assert slug("x" * 61 + " yz") == "x" * 60


def test_new_record_path_stays_short_for_long_titles() -> None:
    path = new_record_path(decision(title="a" * 300))
    assert path == "lodge/decisions/d-3m8qk2-" + "a" * 60 + ".md"
