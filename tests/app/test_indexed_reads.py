"""Indexed CLI answers and their fallback boundaries, over synthetic data."""

import random
from dataclasses import replace
from datetime import timedelta
from unittest.mock import patch

import pytest
from builders import at, decision, files_of
from fakes import FixedClock, MemoryIndex, MemoryStore
from indexed_support import app, large_store, printed, seed
from support import FIRST, project

from lodge import core
from lodge.app import Shown, read_model
from lodge.core import CoreSettings


def test_seen_state_reads_no_snapshot() -> None:
    store, index = project(), MemoryIndex()
    lodge = app(store, index)
    printed(lodge, ["show", FIRST.id])
    printed(lodge, ["show", FIRST.id])
    expected = printed(app(store), ["show", FIRST.id])
    with patch.object(core, "assemble", side_effect=AssertionError("snapshot on hit")):
        assert printed(lodge, ["show", FIRST.id]) == expected


def test_outputs_print_as_in_memory() -> None:
    store, index = large_store(), MemoryIndex()
    seed(store, index)
    rng = random.Random(1041)
    commands = [["waiting"], ["threads"], ["thread", "q-aaaaaa"], ["thread", "missing"]]
    refs = ["B.1", "B.11", "d-000001", "s-000001", "missing", "B"]
    for _ in range(200):
        args = rng.choice(
            [
                *commands,
                ["show", *rng.choices(refs, k=rng.randint(1, 4)), "--reasoning", "--provenance"],
            ]
        )
        assert printed(app(store, index), args) == printed(app(store), args), args


def test_validity_interval() -> None:
    clock = FixedClock()
    future = decision(id="d-bbbbbb", date=(clock.now() + timedelta(minutes=10)).isoformat())
    store, index = project(True), MemoryIndex()
    store.files.update(files_of(future))
    lodge = app(store, index, clock)
    for minutes in (0, 11, -1):
        clock.start = FixedClock().start + timedelta(minutes=minutes)
        expected = printed(app(store, clock=clock), ["show", future.id])
        with patch.object(core, "assemble", wraps=core.assemble) as assembled:
            assert printed(lodge, ["show", future.id]) == expected
        assert assembled.called
        for _ in range(2):
            assert printed(lodge, ["show", future.id]) == expected
        assert ("fails check" in expected[1]) == (minutes < 10)


def test_settings_change_is_another_state() -> None:
    store, index = project(), MemoryIndex()
    seed(store, index)
    settings = replace(CoreSettings(), import_sources=("synthetic",))
    with patch.object(core, "assemble", wraps=core.assemble) as assembled:
        printed(app(store, index, settings=settings), ["show", FIRST.id])
    assert assembled.called


def test_missing_bucket_falls_back_to_memory() -> None:
    store, index = project(), MemoryIndex()
    key = seed(store, index)
    index.row_values[key].pop(FIRST.id)
    with patch.object(core, "assemble", wraps=core.assemble) as assembled:
        assert printed(app(store, index), ["show", FIRST.id]) == printed(
            app(store), ["show", FIRST.id]
        )
    assert assembled.called


@pytest.mark.parametrize("part", ["citer", "parse"])
def test_missing_citer_row_or_parse_falls_back_to_memory(part: str) -> None:
    store, index = project(), MemoryIndex()
    key = seed(store, index)
    if part == "citer":
        index.citer_values[key].pop("item-1")
    else:
        index.values.pop(next(k for k in index.values if FIRST.id in k[0]))
    with patch.object(core, "assemble", wraps=core.assemble) as assembled:
        assert printed(app(store, index), ["show", FIRST.id]) == printed(
            app(store), ["show", FIRST.id]
        )
    assert assembled.called


@pytest.mark.parametrize("code", ["ITEM-1", "A"])
def test_show_code_reads_citers_without_texts(code: str) -> None:
    root = replace(FIRST, code=code)
    citers = [
        decision(id=f"d-{n + 1:06x}", date=at(n), statement=f"See {code}.") for n in range(12)
    ]
    store, index = MemoryStore(root, *citers), MemoryIndex()
    expected = printed(app(store), ["show", code])
    lodge = app(store, index)
    printed(lodge, ["show", code])
    printed(lodge, ["show", code])
    with (
        patch.object(core, "assemble", side_effect=AssertionError("assemble")),
        patch.object(core, "code_tokens", side_effect=AssertionError("texts")),
    ):
        assert printed(lodge, ["show", code]) == expected
    assert "2 more citing records" in expected[1]


def test_equal_listings_with_different_idents_take_the_shortcut(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    store, index = project(), MemoryIndex()
    original = store.identities

    def identities() -> tuple[str, str]:
        a, b = original()
        return a, b + "committed"

    monkeypatch.setattr(store, "identities", identities)
    with patch.object(core, "assemble", wraps=core.assemble) as assembled:
        printed(app(store, index), ["show", FIRST.id])
    assert assembled.call_count == 1


def test_first_read_builds_no_rows() -> None:
    store, index = project(), MemoryIndex()
    with (
        patch.object(read_model, "build_rows", side_effect=AssertionError("rows before output")),
        patch.object(
            read_model, "build_answers", side_effect=AssertionError("answers before output")
        ),
        patch.object(
            read_model, "build_citers", side_effect=AssertionError("citers before output")
        ),
    ):
        assert printed(app(store, index), ["show", FIRST.id]) == printed(
            app(store), ["show", FIRST.id]
        )
    assert not index.states


def test_keep_uses_pinned_inputs() -> None:
    store, index = project(), MemoryIndex()
    lodge = app(store, index)
    printed(lodge, ["show", FIRST.id])
    result = lodge.show_many([FIRST.id])
    before = result.items[0][1]
    old_key = next(iter(index.markers))
    path = next(p for p in store.files if FIRST.id in p)
    store.files[path] = store.files[path].replace(
        "Keep whole transcripts", "Keep edited transcripts"
    )
    lodge.after_output()
    assert old_key in index.states
    record = index.values[index.row_values[old_key][FIRST.id].key]
    assert isinstance(record, core.Decision) and isinstance(before, Shown)
    assert record.title == before.level1.title
    assert "Keep edited transcripts" in printed(lodge, ["show", FIRST.id])[1]
