"""The command flushes before building or keeping a second-sighting state."""

import io
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

import pytest
from fakes import MemoryIndex
from indexed_support import app, printed
from support import FIRST, project

from lodge.app import Row, read_model
from lodge.app.state import State
from lodge.cli import run


def test_first_read_keeps_only_a_marker() -> None:
    store, index = project(), MemoryIndex()
    printed(app(store, index), ["show", FIRST.id])
    assert len(index.markers) == 1 and index.values and not index.states
    assert not index.row_values and not index.citer_values and not index.answer_values


def test_second_read_keeps_after_its_output() -> None:
    store, index = project(), MemoryIndex()
    lodge = app(store, index)
    printed(lodge, ["show", FIRST.id])
    events: list[str] = []

    class Stream(io.StringIO):
        def flush(self) -> None:
            events.append("flush")

    stream = Stream()
    build = read_model.build_rows

    def rows(state: State) -> dict[str, Row]:
        assert FIRST.id in stream.getvalue()
        assert events == ["flush"]
        events.append("rows")
        return build(state)

    with redirect_stdout(stream), patch.object(read_model, "build_rows", rows):
        assert run(["show", FIRST.id], lambda: lodge, lambda: "", lambda *_: 0, lambda: 0) == 0
    assert events == ["flush", "rows"] and len(index.states) == 1
    before = dict(index.states)
    printed(lodge, ["show", FIRST.id])
    assert index.states == before


@pytest.mark.parametrize(
    "builder", ["build_rows", "build_answers", "build_citers", "build_facts", "build_state"]
)
@pytest.mark.parametrize("unknown", [False, True])
def test_failed_keep_keeps_output_and_status(builder: str, unknown: bool) -> None:
    store, index = project(), MemoryIndex()
    lodge = app(store, index)
    printed(lodge, ["show", FIRST.id])
    args = ["show", FIRST.id, "unknown"] if unknown else ["show", FIRST.id]
    expected = printed(app(store), args)
    with patch.object(read_model, builder, side_effect=ValueError("injected builder failure")):
        assert printed(lodge, args) == expected
    assert not index.states


@pytest.mark.parametrize("failure", ["flush", "closed", "pipe"])
def test_output_failure_keeps_nothing(failure: str) -> None:
    store, index = project(), MemoryIndex()
    lodge = app(store, index)
    printed(lodge, ["show", FIRST.id])

    class Stream(io.StringIO):
        def flush(self) -> None:
            if failure == "flush":
                raise OSError("injected flush failure")

        def write(self, text: str) -> int:
            if failure == "pipe":
                raise BrokenPipeError("injected broken pipe")
            return super().write(text)

    stream = Stream()
    if failure == "closed":
        stream.close()

    with (
        redirect_stdout(stream),
        patch.object(
            read_model, "build_rows", side_effect=AssertionError("keep after failed output")
        ),
        pytest.raises((OSError, ValueError)),
    ):
        run(["show", FIRST.id], lambda: lodge, lambda: "", lambda *_: 0, lambda: 0)
    assert not index.states


def test_failed_error_stream_flush_keeps_nothing() -> None:
    store, index = project(), MemoryIndex()
    lodge = app(store, index)
    printed(lodge, ["show", FIRST.id])

    class ErrorStream(io.StringIO):
        def flush(self) -> None:
            raise OSError("injected error-stream flush failure")

    with redirect_stdout(io.StringIO()), redirect_stderr(ErrorStream()), pytest.raises(OSError):
        run(["show", FIRST.id, "missing"], lambda: lodge, lambda: "", lambda *_: 0, lambda: 0)
    assert not index.states
