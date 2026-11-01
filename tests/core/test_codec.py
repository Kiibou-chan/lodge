"""Plain values preserve types and reject shapes the encoder cannot write."""

import ast
from dataclasses import replace
from pathlib import Path

import pytest
from builders import area, decision, entry, message, snapshot_of, thread
from samples import EXAMPLE

from lodge.app import Read
from lodge.core import (
    CORE_CLASSES,
    Imported,
    NumberHandle,
    Problem,
    derive,
    from_plain,
    level1,
    level3,
    to_plain,
)


def test_round_trip_of_every_parse_kind() -> None:
    full = replace(
        EXAMPLE,
        narrows=("d-cccccc",),
        confirms=("d-dddddd",),
        work_item="berths",
        numbers=(NumberHandle("12", "berths.limit"),),
        attachments=("log.txt",),
        imported_from=Imported("archive.md", "Berths"),
    )
    values = (
        full,
        entry(rests_on=("s-aaaaaa",)),
        area(rank=3),
        thread(messages=(message(by="author", where="a synthetic session"),)),
        Problem("lodge/stray", 1, "broken", 4),
        None,
    )
    for value in values:
        decoded = from_plain(to_plain(value), CORE_CLASSES)
        assert decoded == value and type(decoded) is type(value)
    assert type(from_plain(to_plain(full), CORE_CLASSES).scope) is type(full.scope)  # type: ignore[attr-defined]


def test_round_trip_of_mappings_and_read() -> None:
    record = decision()
    snapshot = snapshot_of(record)
    derived = derive(snapshot)
    values = (
        Read(None, (Problem("x", 1, "bad"),), {record.id: "current"}),
        {record.id: "Berths"},
        ("berth", 2, True, None),
        frozenset({"a", "b"}),
        level1(snapshot, derived, record.id, frozenset()),
        level3(snapshot, derived, record.id),
    )
    for value in values:
        assert from_plain(to_plain(value), {**CORE_CLASSES, "Read": Read}) == value


@pytest.mark.parametrize(
    "plain",
    [
        ["Unknown", "x"],
        ["Problem", "x"],
        ["Problem", 1, "bad", "x", None],
        ["=Action", "unknown"],
        ["=Action", "edit", "extra"],
        {1: "bad"},
        {"bad": 1.2},
        b"bad",
        {"bad"},
        (1, 2),
        ["=Problem", "x"],
    ],
)
def test_refuses_unknown_class_and_bad_shapes(plain: object) -> None:
    with pytest.raises(ValueError):
        from_plain(plain, CORE_CLASSES)
    with pytest.raises(ValueError):
        to_plain(1.2)


def test_no_pickle_or_marshal_in_core() -> None:
    # Exercise the encoder too, so this guard is not green with an empty skeleton.
    assert from_plain(to_plain(Problem("x", 1, "bad")), CORE_CLASSES) == Problem("x", 1, "bad")
    for path in (Path(__file__).parents[2] / "src/lodge/core").glob("*.py"):
        for node in ast.walk(ast.parse(path.read_text())):
            if isinstance(node, ast.Import):
                assert not {a.name for a in node.names} & {"pickle", "marshal"}
            if isinstance(node, ast.ImportFrom):
                assert node.module not in {"pickle", "marshal"}


def test_compact_form_is_json_native() -> None:
    plain = to_plain(Problem("x", 1, "bad"))
    assert plain == ["Problem", "x", 1, "bad", None]
    assert from_plain(plain, CORE_CLASSES) == Problem("x", 1, "bad")


@pytest.mark.parametrize(
    "plain",
    [["Unknown", "x"], ["Problem", "x"], ["=Action", "wrong"], ["Problem", b"x", 1, "bad", None]],
)
def test_compact_form_rejects_bad_tags_and_shapes(plain: object) -> None:
    with pytest.raises(ValueError):
        from_plain(plain, CORE_CLASSES)


@pytest.mark.parametrize(
    "plain", [["Problem", 1, 1, "bad", None], ["Problem", "x", True, "bad", None]]
)
def test_compact_scalar_types_are_preserved(plain: object) -> None:
    with pytest.raises(ValueError):
        from_plain(plain, CORE_CLASSES)


@pytest.mark.parametrize(
    "position,bad", [(3, ["=Action", "edit"]), (9, None), (9, ["", 1]), (16, ["", 3])]
)
def test_compact_nested_shapes_are_checked(position: int, bad: object) -> None:
    plain = to_plain(decision())
    assert isinstance(plain, list)
    plain[position] = bad
    with pytest.raises(ValueError):
        from_plain(plain, CORE_CLASSES)
