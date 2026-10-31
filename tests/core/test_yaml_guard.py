"""The fast path admits only writer shapes and preserves the Python diagnostics."""

from dataclasses import replace

import pytest
import yaml
from builders import area, decision, entry, message, thread
from samples import DECISION_PATH, EXAMPLE, document, replaced

from lodge.core import (
    Action,
    Change,
    Imported,
    NumberHandle,
    Problem,
    Quote,
    Record,
    parse_record,
    write_area,
    write_record,
    write_thread,
    yamlfast,
    yamlio,
)
from lodge.core.document import split_document


def test_every_written_header_is_admitted() -> None:
    rich = decision(
        decided_by="author",
        code="PORT-1.why",
        changes=(Change("s-aaaaaa", Action.CREATE), Change("s-bbbbbb", Action.EDIT)),
        replaces=("d-aaaaaa",),
        narrows=("d-bbbbbb",),
        confirms=("d-cccccc",),
        work_item="harbour/read-speed",
        quote=Quote('Sail\n\t"now"\\later\rsoon', "a session", "yesterday"),
        numbers=(NumberHandle("42", "berths"), NumberHandle("2", "cranes")),
        attachments=("diagram.txt", "notes with spaces.txt"),
    )
    imported = Imported("archive.md", "Old harbour notes")
    records: list[Record] = [
        EXAMPLE,
        decision(),
        rich,
        replace(rich, decided_by="harbour planner", imported_from=imported),
        entry(),
        entry(code="PORT-2", rests_on=("s-aaaaaa",), imported_from=imported),
    ]
    texts = [write_record(record) for record in records]
    texts += [write_area(area()), write_area(area(rank=12, order=("s-aaaaaa", "s-bbbbbb")))]
    texts.append(
        write_thread(
            thread(
                messages=(
                    message(by="author", when="yesterday", where="a session"),
                    message(),
                    message(by="harbour planner", where="the review"),
                )
            )
        )
    )
    headers = [split_document(text)[0] for text in texts]
    body = split_document(texts[-1])[1]
    headers += [block.split("\n\n")[1] for block in body.split("## Message ")[1:]]
    for header in headers:
        assert yamlfast.admitted(header), header
        assert yamlfast.load_yaml(header) == yaml.load(header, Loader=yamlio._TextLoader)
    for title in ("Café 船 😀", 'quotes " \\ / # | > & * ! % ?'):
        header = split_document(write_record(decision(title=title)))[0]
        assert yamlfast.admitted(header), header
        assert yamlfast.load_yaml(header) == yaml.load(header, Loader=yamlio._TextLoader)


@pytest.mark.parametrize("line", ["title: x\t", "title:\tx", "- a\t", "title: x\t# c"])
def test_trailing_tab_is_not_admitted_and_fails_as_today(
    line: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    header = "\n".join(replaced("title", line))
    assert not yamlfast.admitted(header)
    actual = parse_record(DECISION_PATH, document(header.split("\n")))
    # With libyaml unavailable, the unchanged Python loader supplies the reference problem.
    monkeypatch.setattr(yaml, "__with_libyaml__", False)
    expected = parse_record(DECISION_PATH, document(header.split("\n")))
    assert isinstance(actual, Problem)
    assert actual == expected
    assert actual.line is not None
    assert "not valid YAML" in actual.message


@pytest.mark.parametrize(
    "header", ["key: |#", "a: b\n\ufeffkey: c", "key: " + "[" * 600 + "]" * 600]
)
def test_block_scalar_bom_and_nesting_not_admitted(header: str) -> None:
    assert not yamlfast.admitted(header)


def test_c_loader_used_for_admitted_headers(monkeypatch: pytest.MonkeyPatch) -> None:
    original = yamlfast.load_yaml
    calls: list[str] = []

    def counted(text: str) -> object:
        calls.append(text)
        return original(text)

    monkeypatch.setattr(yamlfast, "load_yaml", counted)
    assert yamlio.load_yaml("key: yes") == {"key": "yes"}
    assert calls == ["key: yes"]


def test_falls_back_without_libyaml(monkeypatch: pytest.MonkeyPatch) -> None:
    assert yamlfast.admitted('key: "berth"')
    monkeypatch.setattr(yaml, "__with_libyaml__", False)

    def forbidden(text: str) -> object:
        pytest.fail(f"libyaml called while unavailable: {text!r}")

    monkeypatch.setattr(yamlfast, "load_yaml", forbidden)
    assert yamlio.load_yaml('key: "berth"') == {"key": "berth"}


@pytest.mark.parametrize("failure", [ValueError("synthetic C failure"), RuntimeError("C failed")])
def test_c_failures_fall_back_with_python_diagnostics(
    failure: Exception, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert yamlfast.admitted("title: a\ntitle: b")

    def broken(text: str) -> object:
        raise failure

    monkeypatch.setattr(yamlfast, "load_yaml", broken)
    assert yamlio.load_yaml("title: a") == {"title": "a"}
    with pytest.raises(yamlio.YamlError, match="duplicate key 'title'") as error:
        yamlio.load_yaml("title: a\ntitle: b")
    assert error.value.line == 2


@pytest.mark.parametrize(
    "header",
    [
        "a: b",
        'a: ""',
        "a: 14:14",
        "a: [a, b]",
        "a: []",
        "a: {b: c, d: e}",
        'a:\n  - {b: "c"}\n  - {d: 3}',
        'a: "# | > & * ! % ?"',
        'a: "\\u0000\\u0041\\uD7FF\\ue000"',
        'a: "\\b\\f\\n\\r\\t\\/\\\\\\""',
    ],
)
def test_writer_shapes_are_admitted(header: str) -> None:
    assert yamlfast.admitted(header)


@pytest.mark.parametrize(
    "header",
    [
        "",
        "a:",
        "a:\nb: c",
        "  - {a: b}",
        "a:\n  - b",
        "a: {}",
        "a: b ",
        "a: b\n\n",
        "a: b # c",
        "a: a:",
        "a: ~",
        "A: b",
        "a1: b",
        "a-b: c",
        "a: {b: {c: d}}",
        "a: [a, [b]]",
        "a: [a,b]",
        "a: {b: c,d: e}",
        "a: |",
        "a: >",
        "a: &b c",
        "a: *b",
        "a: !str b",
        "%YAML 1.1",
        "? a",
        'a: "\\uD800"',
        'a: "\\udfff"',
        'a: "\\ud83d\\ude00"',
        'a: "\\x41"',
        'a: "\x7f"',
        'a: "\x85"',
        'a: "\u2028"',
        'a: "\u2029"',
        'a: "\ufeff"',
        'a: "\ud800"',
        "a: b\r\n",
        'a: "\t"',
    ],
)
def test_other_shapes_are_not_admitted(header: str) -> None:
    assert not yamlfast.admitted(header)
