"""Batched show reads once, preserves ref order, and caps contextual records."""

from unittest.mock import patch

import pytest
from builders import area, at, decision
from fakes import MemoryStore
from support import ENTRY, FIRST, project, wired

from lodge.app import Conflict, LodgeError, Shown, reads
from lodge.app.state import State, resolve_ref
from lodge.cli import run


def test_each_record_once_in_ref_order() -> None:
    result = wired(project()).show_many([FIRST.id, "ITEM-1", ENTRY.id, FIRST.id], True, True)
    assert [ref for ref, _ in result.items] == [FIRST.id, "ITEM-1", ENTRY.id, FIRST.id]
    shown = [item for _, item in result.items if isinstance(item, Shown)]
    assert [s.level1.id for s in shown] == [FIRST.id, FIRST.id, ENTRY.id, FIRST.id]
    assert [s.repeat for s in shown] == [False, True, False, True]
    assert shown[0].level2 == "Because they are evidence."
    assert shown[0].level3 is not None
    assert all(s.read is result.read for s in shown)


def test_failing_ref_in_place_and_others_shown() -> None:
    result = wired(project()).show_many([FIRST.id, "unknown", ENTRY.id])
    assert len(result.items) == 3
    assert isinstance(result.items[0][1], Shown)
    error = result.items[1][1]
    assert isinstance(error, LodgeError)
    assert str(error) == "no record named unknown" and error.exit_code == 2
    last = result.items[2][1]
    assert isinstance(last, Shown) and last.level1.id == ENTRY.id


def test_one_read_for_many_refs() -> None:
    store = project()
    with patch.object(store, "trees", wraps=store.trees) as calls:
        result = wired(store).show_many([FIRST.id, ENTRY.id, "ITEM-1", "bad"])
    assert len(result.items) == 4
    assert calls.call_count == 1


def test_siblings_and_citers_capped_at_ten(capsys: pytest.CaptureFixture[str]) -> None:
    root = decision(id="d-000000", code="X-1")
    siblings = [decision(id=f"d-{n:06x}", code=f"X-1.{n:02d}") for n in range(1, 13)]
    citers = [decision(id=f"d-{n + 20:06x}", date=at(n), statement="See X-1.") for n in range(11)]
    lodge = wired(MemoryStore(area(), root, *siblings, *citers))
    result = lodge.show_many(["x-1"])
    shown = result.items[0][1]
    assert isinstance(shown, Shown)
    assert [v.id for v in shown.siblings] == [s.id for s in siblings[:10]]
    assert [v.id for v in shown.citers] == [c.id for c in reversed(citers[1:])]
    assert shown.left_out == (2, 1)
    assert lodge.show("X-1") == shown
    assert (
        run(
            ["show", "X-1", "--reasoning", "--provenance"],
            lambda: lodge,
            lambda: "",
            lambda *_: 0,
            lambda: 0,
        )
        == 0
    )
    output = capsys.readouterr().out
    assert output.index("## Provenance") < output.index("siblings:") < output.index("cited by:")
    assert output.endswith("and 2 more siblings and 1 more citing records; lodge search X-1\n")
    assert output.count(" · A decision") == 20
    assert "A statement." not in output[output.index("siblings:") :]


def test_broken_files_reported_once_for_the_batch(capsys: pytest.CaptureFixture[str]) -> None:
    store = project()
    store.files["lodge/decisions/d-bbbbbb-broken.md"] = "no header\n"
    shown = wired(store).show_many([FIRST.id, ENTRY.id])
    assert len(shown.read.unrecorded) == 1
    assert shown.read.unrecorded[0].check == 1
    assert all(isinstance(item, Shown) for _, item in shown.items)
    assert (
        run(["show", FIRST.id, ENTRY.id], lambda: wired(store), lambda: "", lambda *_: 0, lambda: 0)
        == 0
    )
    output = capsys.readouterr().out
    assert output.count("fetched ") == 1
    assert output.count("problem: lodge/decisions/d-bbbbbb-broken.md") == 1


def test_batch_exit_uses_highest_failure(capsys: pytest.CaptureFixture[str]) -> None:
    lodge = wired(project())
    original = resolve_ref

    def resolve(state: State, ref: str) -> str:
        if ref == "conflict":
            raise Conflict("the store moved")
        return original(state, ref)

    with patch.object(reads, "resolve_ref", resolve):
        status = run(
            ["show", "unknown", "conflict", FIRST.id],
            lambda: lodge,
            lambda: "",
            lambda *_: 0,
            lambda: 0,
        )
    assert status == 2
    captured = capsys.readouterr()
    assert captured.out.startswith("fetched 2026-10-29T08:00:00+00:00\n----- unknown\n")
    assert FIRST.id in captured.out
    assert captured.err == "lodge: no record named unknown\nlodge: the store moved\n"
