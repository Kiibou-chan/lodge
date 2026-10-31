"""Thread files preserve messages and reject malformed records."""

import pytest
from builders import at, decision, files_of, message, snapshot_of, thread

from lodge.core import (
    LengthGuidance,
    Problem,
    Thread,
    ThreadState,
    Tree,
    appended,
    derive,
    feedback,
    load,
    newest_last,
    parse_thread,
    thread_path,
    write_thread,
)


def parsed(t: Thread) -> Thread:
    result = parse_thread(thread_path(t.id), write_thread(t))
    assert isinstance(result, Thread)
    return result


def test_thread_round_trips() -> None:
    t = thread(
        state=ThreadState.CLOSED,
        messages=(
            message(text="One.\nTwo."),
            message(by="author", when="yesterday", where="lodge viewer"),
            message(text=""),
        ),
    )
    assert parsed(t) == t


@pytest.mark.parametrize("closed,first", [(False, False), (True, True)])
def test_empty_text_only_on_the_closing_message(closed: bool, first: bool) -> None:
    t = thread(state=ThreadState.CLOSED if closed else ThreadState.OPEN)
    text = write_thread(t).replace("A message.", "")
    if first:
        text += "\n## Message 2\n\nby: coordinator\nwhen: " + at(1) + "\n\nEnd.\n"
    assert isinstance(parse_thread(thread_path(t.id), text), Problem)


def test_written_shape_matches_the_example() -> None:
    t = thread(
        id="q-4kq1zm",
        about="s-0abcde",
        opened="2026-10-29T09:30:00+01:00",
        messages=(
            message(
                by="author",
                when="2026-10-29 09:30",
                where="lodge viewer",
                text="Is this still true?",
            ),
            message(when="2026-10-29T10:00:00+01:00", text="It is; see d-3m8qk2."),
        ),
    )
    assert write_thread(t) == EXAMPLE


EXAMPLE = """---
id: q-4kq1zm
kind: thread
about: s-0abcde
raises: doubt
state: open
opened: 2026-10-29T09:30:00+01:00
---

## Message 1

by: author
when: "2026-10-29 09:30"
where: "lodge viewer"

Is this still true?

## Message 2

by: coordinator
when: 2026-10-29T10:00:00+01:00

It is; see d-3m8qk2.
"""


@pytest.mark.parametrize("text", ["## Message 2", r"\## Message 2"])
def test_text_line_like_a_heading_round_trips(text: str) -> None:
    assert parsed(thread(messages=(message(text=text),))).messages[0].text == text


@pytest.mark.parametrize("text", ['a: "b" # c', "<script>", "## Reasoning"])
def test_yaml_and_markdown_specials_round_trip(text: str) -> None:
    assert parsed(thread(messages=(message(text=text),))).messages[0].text == text


def invalid(old: str, new: str) -> Problem:
    t = thread()
    result = parse_thread(thread_path(t.id), write_thread(t).replace(old, new))
    assert isinstance(result, Problem) and result.check == 1
    return result


def test_author_message_needs_where() -> None:
    assert "an author message needs where" in invalid("by: coordinator", "by: author").message


def test_malformed_id_is_problem_1() -> None:
    assert isinstance(
        parse_thread("lodge/threads/q-BAD.md", EXAMPLE.replace("q-4kq1zm", "q-BAD")), Problem
    )


def test_about_must_name_a_decision_or_entry() -> None:
    assert "about must name" in invalid("about: s-aaaaaa", "about: q-aaaaaa").message


def test_thread_needs_a_message() -> None:
    assert "at least one message" in invalid("## Message 1", "").message


def test_messages_numbered_in_order() -> None:
    assert "numbered" in invalid("## Message 1", "## Message 2").message


def test_body_text_before_first_message_refused() -> None:
    invalid("## Message 1", "Stray text.\n\n## Message 1")


def test_appended_refuses_a_closed_thread() -> None:
    with pytest.raises(ValueError):
        appended(thread(state=ThreadState.CLOSED), message())
    with pytest.raises(ValueError):
        appended(thread(), message(text=""))


def test_newest_last_by_opened_then_id() -> None:
    a = thread(id="q-aaaaaa", opened=at(1))
    b = thread(id="q-bbbbbb", opened=at(1))
    c = thread(opened=at(0))
    assert newest_last((b, a, c)) == (c, a, b)


def test_load_reads_threads_and_their_paths() -> None:
    t = thread()
    s = load(Tree(None, files_of(t)))
    assert s.threads[t.id] == t and s.paths[t.id] == thread_path(t.id)


def test_nested_file_under_threads_is_stray() -> None:
    s = load(Tree(None, {"lodge/threads/nested/q-aaaaaa.md": EXAMPLE}))
    assert s.problems[0].check == 1
    assert s.problems[0].path == "lodge/threads/nested/q-aaaaaa.md"
    assert "this file is not a record" in s.problems[0].message


@pytest.mark.parametrize("close", [False, True])
def test_appended_cleans_the_text_and_closes(close: bool) -> None:
    result = appended(thread(), message(text=" " if close else "a\r\nb \r\n  "), close=close)
    assert result.messages[-1].text == ("" if close else "a\nb")
    assert result.state is (ThreadState.CLOSED if close else ThreadState.OPEN)


@pytest.mark.parametrize(
    "old,new,key",
    [
        ("opened: " + at(0), "opened: yesterday", "opened"),
        ("raises: doubt", "raises: worry", "raises"),
        ("state: open", "state: ajar", "state"),
        ("when: " + at(0), "when: yesterday", "when"),
        ("by: coordinator", "by: coordinator\nextra: value", "extra"),
        ("by: coordinator\n", "", "by"),
    ],
)
def test_unreadable_header_values_are_problem_1(old: str, new: str, key: str) -> None:
    assert key in invalid(old, new).message


@pytest.mark.parametrize("text", ["A message. ", "A\r\nmessage."])
def test_write_text_error_names_the_field(text: str) -> None:
    with pytest.raises(ValueError, match="message 1 text"):
        write_thread(thread(messages=(message(text=text),)))


def test_message_without_metadata_names_the_message() -> None:
    problem = invalid("by: coordinator\nwhen: " + at(0) + "\n\nA message.", "")
    assert problem.message == "a message needs by and when"
    assert problem.line == 10


def test_thread_id_is_not_number_feedback() -> None:
    d = decision(statement="See q-123456.")
    s = snapshot_of(d)
    assert not any("number" in f.message for f in feedback([d], s, derive(s), LengthGuidance()))
