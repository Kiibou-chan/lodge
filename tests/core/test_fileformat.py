import hashlib

import pytest
from samples import DECISION_PATH, EXAMPLE, EXAMPLE_TEXT, SPEC_PATH, TITLE, document

from lodge.core import (
    Action,
    Area,
    Change,
    Decision,
    Imported,
    NumberHandle,
    Problem,
    Quote,
    Scope,
    SpecEntry,
    area_path,
    content_hash,
    new_record_path,
    parse_area,
    parse_record,
    slug,
    write_area,
    write_record,
)

FULL = Decision(
    id="d-3m8qk2",
    title=TITLE,
    scope=Scope.PROCESS,
    decided_by="author",
    date="2026-10-28T23:48:10+01:00",
    statement="One to three sentences.\n\nA second paragraph.",
    reasoning="Why.\n\n- a list\n- of reasons",
    code="ITEM-1",
    changes=(Change("s-4kq1zm", Action.CREATE), Change("s-0abcde", Action.RETIRE)),
    replaces=("d-8rw0te", "d-1abcde"),
    narrows=("d-2abcde",),
    confirms=("d-3abcde",),
    work_item="docs/plans/ship.md",
    quote=Quote("Record it.", "first session", "2026-10-28 23:48"),
    numbers=(NumberHandle("42", "lodge show d-1abcde"), NumberHandle("3.5 s", "d-2abcde:time")),
    attachments=("lodge/attachments/log.txt",),
    imported_from=Imported("docs/old.md", "ITEM-1"),
)
REQUIRED = Decision(
    id="d-3m8qk2",
    title="A title",
    scope=Scope.PRODUCT,
    decided_by="coordinator",
    date="2026-10-28T23:48:10+01:00",
    statement="A statement.",
)
SPEC = SpecEntry(id="s-4kq1zm", area="storage", title="Transcripts", statement="They are kept.")


def parsed(path: str, text: str) -> Decision | SpecEntry:
    result = parse_record(path, text)
    assert not isinstance(result, Problem), result
    return result


@pytest.mark.parametrize("record", [FULL, REQUIRED])
def test_decision_round_trips_both_ways(record: Decision) -> None:
    text = write_record(record)
    assert parsed(DECISION_PATH, text) == record
    assert write_record(parsed(DECISION_PATH, text)) == text


def test_written_text_matches_example() -> None:
    assert write_record(EXAMPLE) == EXAMPLE_TEXT
    assert parsed(DECISION_PATH, EXAMPLE_TEXT) == EXAMPLE


def test_written_text_of_every_field() -> None:
    lines = write_record(FULL).split("\n")
    assert "  - {entry: s-0abcde, action: retire}" in lines
    assert "replaces: [d-8rw0te, d-1abcde]" in lines
    assert "narrows: [d-2abcde]" in lines
    assert "confirms: [d-3abcde]" in lines
    assert 'work_item: "docs/plans/ship.md"' in lines
    assert '  - {value: "42", handle: "lodge show d-1abcde"}' in lines
    assert 'attachments: ["lodge/attachments/log.txt"]' in lines
    assert 'imported_from: {file: "docs/old.md", heading: "ITEM-1"}' in lines
    keys = [line.split(":")[0] for line in lines[1 : lines.index("---", 1)] if line[0] != " "]
    assert keys == [
        *("id", "kind", "code", "title", "scope", "decided_by", "date", "changes", "replaces"),
        *("narrows", "confirms", "work_item", "quote", "numbers", "attachments", "imported_from"),
    ]


HOSTILE = [
    "No",
    "null",
    "a: b",
    "# x",
    '"',
    "\\",
    "- a",
    "{a}",
    "[a]",
    "a, b",
    "'q'",
    "é😀",
    "&a *b",
]


@pytest.mark.parametrize("text", HOSTILE)
def test_round_trip_survives_hostile_strings(text: str) -> None:
    record = Decision(
        id="d-3m8qk2",
        title=text,
        scope=Scope.PRODUCT,
        decided_by=text,
        date="2026-10-28T23:48:10+01:00",
        statement="S.",
        work_item=text,
        quote=Quote(text, text, text),
        numbers=(NumberHandle(text, text),),
        attachments=(text,),
        imported_from=Imported(text, text),
    )
    written = write_record(record)
    assert parsed(DECISION_PATH, written) == record
    assert write_record(parsed(DECISION_PATH, written)) == written


def test_round_trip_survives_every_readable_character() -> None:
    every = "".join(chr(n) for n in range(0x20, 0xD800) if n not in (0x7F, 0x2028, 0x2029))
    every = "".join(c for c in every if not 0x80 <= ord(c) <= 0x9F) + "\U0001f600�"
    record = Decision(
        id="d-3m8qk2",
        title=every,
        scope=Scope.PRODUCT,
        decided_by="a",
        date="2026-10-28T23:48:10+01:00",
        statement="S.",
    )
    assert parsed(DECISION_PATH, write_record(record)) == record


@pytest.mark.parametrize("code", ["", "-a", ".a", "a b", "a:b", "a\n", "é"])
def test_bad_code_is_problem_1(code: str) -> None:
    header = ["id: d-3m8qk2", "kind: decision", f'code: "{code}"', 'title: "T"', "scope: product"]
    header += ["decided_by: coordinator", "date: 2026-10-28T23:48:10+01:00"]
    result = parse_record(DECISION_PATH, document(header))
    assert isinstance(result, Problem)
    assert result.check == 1
    assert "code" in result.message


@pytest.mark.parametrize("char", ["\x01", "\x7f", "\x85", "\u2028", "\ufffe", "\t", "\n"])
def test_control_character_is_problem_1(char: str) -> None:
    escaped = '"a' + char.encode("unicode_escape").decode() + 'b"'
    header = ["id: d-3m8qk2", "kind: decision", f"title: {escaped}", "scope: product"]
    header += ["decided_by: coordinator", "date: 2026-10-28T23:48:10+01:00"]
    result = parse_record(DECISION_PATH, document(header))
    assert isinstance(result, Problem)
    assert result.check == 1
    assert "title" in result.message


@pytest.mark.parametrize("char", ["\x01", "\x85", "\n", "\u2028"])
def test_write_refuses_control_characters(char: str) -> None:
    with pytest.raises(ValueError, match="title"):
        write_record(
            Decision("d-3m8qk2", f"a{char}b", Scope.PRODUCT, "x", "2026-10-28T23:48:10+01:00", "S.")
        )


def test_write_refuses_reasoning_heading_in_statement() -> None:
    record = Decision(
        "d-3m8qk2", "T", Scope.PRODUCT, "x", "2026-10-28T23:48:10+01:00", "A\n## Reasoning\nB"
    )
    with pytest.raises(ValueError, match="Reasoning"):
        write_record(record)
    longer = SpecEntry("s-4kq1zm", "storage", "T", "A\n## Reasoning\nB")
    with pytest.raises(ValueError, match="Reasoning"):
        write_record(longer)


def test_write_refuses_a_record_parse_would_not_read_back() -> None:
    bad = Decision("d-3m8qk2", "T", Scope.PRODUCT, "x", "yesterday", "S.")
    with pytest.raises(ValueError, match="date"):
        write_record(bad)
    with pytest.raises(ValueError, match="code"):
        write_record(
            Decision(
                "d-3m8qk2", "T", Scope.PRODUCT, "x", "2026-10-28T23:48:10+01:00", "S.", code="a b"
            )
        )


def test_statement_with_a_lookalike_heading_is_kept() -> None:
    record = Decision(
        "d-3m8qk2",
        "T",
        Scope.PRODUCT,
        "x",
        "2026-10-28T23:48:10+01:00",
        "A\n### Reasoning\n  ## Reasoning",
    )
    assert parsed(DECISION_PATH, write_record(record)) == record


def test_crlf_text_parses_and_hashes_as_lf() -> None:
    crlf = EXAMPLE_TEXT.replace("\n", "\r\n")
    assert parsed(DECISION_PATH, crlf) == EXAMPLE
    assert content_hash(crlf) == content_hash(EXAMPLE_TEXT)
    digest = hashlib.sha256(EXAMPLE_TEXT.encode()).hexdigest()
    assert content_hash(EXAMPLE_TEXT) == digest[:12]
    assert len(content_hash("")) == 12


def test_hash_covers_undecodable_bytes() -> None:
    raw = b"a\xffb"
    text = raw.decode("utf-8", errors="surrogateescape")
    assert content_hash(text) == hashlib.sha256(raw).hexdigest()[:12]


def test_spec_entry_takes_area_from_folder() -> None:
    text = write_record(SPEC)
    assert text == '---\nid: s-4kq1zm\nkind: spec\ntitle: "Transcripts"\n---\n\nThey are kept.\n'
    assert parsed(SPEC_PATH, text) == SPEC
    other = parsed("lodge/spec/other-area/s-4kq1zm-x.md", text)
    assert isinstance(other, SpecEntry)
    assert other.area == "other-area"


def test_spec_entry_with_code_and_import_round_trips() -> None:
    entry = SpecEntry(
        "s-4kq1zm", "storage", "T", "S.", code="ITEM-1", imported_from=Imported("a.md", "H")
    )
    text = write_record(entry)
    assert text.split("\n")[1:6] == [
        "id: s-4kq1zm",
        "kind: spec",
        "code: ITEM-1",
        'title: "T"',
        'imported_from: {file: "a.md", heading: "H"}',
    ]
    assert parsed(SPEC_PATH, text) == entry


def test_area_file_round_trips() -> None:
    area = Area("storage", "Storage", "How records are kept.", ("s-4kq1zm", "s-0abcde"))
    text = write_area(area)
    header = '---\nkind: area\ntitle: "Storage"\norder: [s-4kq1zm, s-0abcde]\n---\n'
    assert text == header + "\nHow records are kept.\n"
    path = area_path("storage")
    assert path == "lodge/spec/storage/_area.md"
    back = parse_area(path, text)
    assert back == area
    assert isinstance(back, Area)
    assert write_area(back) == text


def test_area_without_entries_or_intro() -> None:
    area = Area("storage", "Storage", "", ())
    text = write_area(area)
    assert text == '---\nkind: area\ntitle: "Storage"\n---\n'
    assert parse_area(area_path("storage"), text) == area


def test_paths_and_slugs() -> None:
    assert (
        new_record_path(EXAMPLE)
        == "lodge/decisions/d-3m8qk2-whole-transcripts-are-kept-before-a.md"
    )
    assert new_record_path(SPEC) == "lodge/spec/storage/s-4kq1zm-transcripts.md"
    assert (
        slug("Whole transcripts, kept: before a session is archived!")
        == "whole-transcripts-kept-before-a-session"
    )
    assert slug("  Ünï--code & 42 ") == "n-code-42"
    assert slug("***") == ""
    bare = Decision("d-3m8qk2", "***", Scope.PRODUCT, "x", "2026-10-28T23:48:10+01:00", "S.")
    assert new_record_path(bare) == "lodge/decisions/d-3m8qk2.md"
