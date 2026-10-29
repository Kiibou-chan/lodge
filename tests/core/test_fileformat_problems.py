import pytest
from samples import BASE_HEADER, DECISION_PATH, SPEC_PATH, document, replaced

from lodge.core import Decision, Problem, SpecEntry, parse_area, parse_record


def problem(text: str, path: str = DECISION_PATH) -> Problem:
    result = parse_record(path, text)
    assert isinstance(result, Problem), result
    assert result.check == 1
    assert result.path == path
    return result


def test_missing_fence() -> None:
    assert "---" in problem("title: x\n\nBody.\n").message
    assert "closed" in problem("---\ntitle: x\n\nBody.\n").message
    assert "---" in problem("").message


def test_bad_yaml_with_line() -> None:
    found = problem(document(replaced("title", "title: a: b")))
    assert found.line == 7
    assert "YAML" in found.message


def test_header_that_is_not_a_mapping() -> None:
    assert "mapping" in problem(document(["- a", "- b"])).message
    assert "mapping" in problem(document([])).message


def test_unknown_key_named() -> None:
    found = problem(document([*BASE_HEADER, "replace: [d-8rw0te]"]))
    assert "replace" in found.message
    assert found.line == 8


def test_unknown_kind() -> None:
    assert "kind" in problem(document(replaced("kind", "kind: note"))).message
    assert "kind" in problem(document(replaced("kind", None))).message


@pytest.mark.parametrize("key", ["id", "title", "scope", "decided_by", "date"])
def test_missing_required_field(key: str) -> None:
    found = problem(document(replaced(key, None)))
    assert key in found.message
    assert "missing" in found.message


def test_empty_statement_is_missing() -> None:
    assert "statement" in problem(document(BASE_HEADER, body="")).message
    assert "statement" in problem(document(BASE_HEADER, body="## Reasoning\n\nWhy.")).message


def test_empty_title_is_missing() -> None:
    assert "title" in problem(document(replaced("title", 'title: ""'))).message


@pytest.mark.parametrize(
    ("extra", "word"),
    [
        (["scope: private"], "scope"),
        (["changes:", "  - {entry: s-4kq1zm, action: rewrite}"], "action"),
        (["changes:", "  - {entry: s-4kq1zm}"], "action"),
        (["changes:", "  - {entry: s-4kq1zm, action: edit, why: x}"], "why"),
        (["changes: s-4kq1zm"], "changes"),
        (["changes:", "  - s-4kq1zm"], "changes"),
    ],
)
def test_bad_scope_or_action(extra: list[str], word: str) -> None:
    header = replaced("scope", None) if extra[0].startswith("scope") else BASE_HEADER
    assert word in problem(document([*header, *extra])).message


@pytest.mark.parametrize(
    "line",
    [
        "title: [a, b]",
        "title: {a: b}",
        "decided_by: [a]",
        "date: [2026-10-28T23:48:10+01:00]",
    ],
)
def test_non_string_where_string_expected(line: str) -> None:
    key = line.split(":")[0]
    found = problem(document(replaced(key, line)))
    assert key in found.message


@pytest.mark.parametrize(
    "line",
    [
        "replaces: d-8rw0te",
        "replaces: [{a: b}]",
        "replaces: [s-4kq1zm]",
        "narrows: [d-8rw0tI]",
        "confirms: [x]",
        "attachments: log.txt",
        "quote: Record it.",
        'quote: {text: "x", where: "y"}',
        'quote: {text: "x", where: "y", when: "z", by: "w"}',
        "numbers: [1]",
        'numbers: [{value: "1"}]',
        "imported_from: a.md",
        'imported_from: {file: "a.md"}',
        "work_item: [a]",
        "code: [a]",
    ],
)
def test_wrong_shapes_name_their_key(line: str) -> None:
    found = problem(document([*BASE_HEADER, line]))
    assert line.split(":")[0] in found.message


def test_bad_id_shapes() -> None:
    assert "id" in problem(document(replaced("id", "id: d-3m8qkI"))).message
    assert "id" in problem(document(replaced("id", "id: s-3m8qk2"))).message


def test_change_entry_must_be_a_specification_id() -> None:
    found = problem(document([*BASE_HEADER, "changes:", "  - {entry: d-8rw0te, action: edit}"]))
    assert "changes" in found.message


@pytest.mark.parametrize(
    "date",
    [
        "2026-10-28T23:48:10",
        "2026-10-28 23:48:10+01:00",
        "2026-10-28T23:48+01:00",
        "2026-10-28T23:48:10Z",
    ],
)
def test_date_without_offset(date: str) -> None:
    found = problem(document(replaced("date", f"date: {date}")))
    assert "date" in found.message
    assert "offset" in found.message


def test_date_that_is_not_a_date() -> None:
    assert "date" in problem(document(replaced("date", "date: 2026-13-28T23:48:10+01:00"))).message


def test_date_only_without_import() -> None:
    found = problem(document(replaced("date", "date: 2026-10-28")))
    assert "imported_from" in found.message


def test_imported_date_only_normalised() -> None:
    header = [*replaced("date", "date: 2026-10-28"), 'imported_from: {file: "a.md", heading: "H"}']
    result = parse_record(DECISION_PATH, document(header))
    assert isinstance(result, Decision)
    assert result.date == "2026-10-28T00:00:00+00:00"
    assert (
        "2026-13-45"
        in problem(document([*replaced("date", "date: 2026-13-45"), header[-1]])).message
    )


def test_duplicate_key() -> None:
    found = problem(document([*BASE_HEADER, 'title: "Again"']))
    assert "title" in found.message
    assert found.line == 8


def test_spec_entry_outside_an_area_folder() -> None:
    text = '---\nid: s-4kq1zm\nkind: spec\ntitle: "T"\n---\n\nS.\n'
    assert "area" in problem(text, "s-4kq1zm-t.md").message
    assert "area" in problem(text, "lodge/spec/Bad Name/s-4kq1zm-t.md").message


def test_spec_entry_rejects_decision_keys_and_reasoning() -> None:
    header = ["id: s-4kq1zm", "kind: spec", 'title: "T"', "scope: product"]
    assert "scope" in problem(document(header), SPEC_PATH).message
    header = ["id: s-4kq1zm", "kind: spec", 'title: "T"']
    assert "Reasoning" in problem(document(header, "S.\n\n## Reasoning\n\nWhy."), SPEC_PATH).message
    result = parse_record(SPEC_PATH, document(header))
    assert isinstance(result, SpecEntry)


def test_bad_utf8_is_problem_1() -> None:
    raw = document(BASE_HEADER, "A \udcff statement.")
    assert "UTF-8" in problem(raw).message


def test_area_problems() -> None:
    path = "lodge/spec/storage/_area.md"
    for text in [
        "no fence",
        document(["kind: area"]),
        document(["kind: spec", 'title: "T"']),
        document(["kind: area", 'title: "T"', "order: s-4kq1zm"]),
        document(["kind: area", 'title: "T"', "order: [d-8rw0te]"]),
        document(["kind: area", 'title: "T"', "name: x"]),
    ]:
        result = parse_area(path, text)
        assert isinstance(result, Problem)
        assert result.check == 1
    assert isinstance(parse_area("_area.md", document(["kind: area", 'title: "T"'])), Problem)
