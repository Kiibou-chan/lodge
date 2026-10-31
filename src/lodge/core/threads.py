"""Thread files and append-only message operations."""

import re
from collections.abc import Iterable
from dataclasses import replace
from datetime import datetime

from lodge.core.document import assemble, key_line, load_header, read_with, trim_block
from lodge.core.fields import (
    FormatError,
    check_keys,
    read_enum,
    read_id,
    read_optional_str,
    read_stamp,
    read_str,
    require,
)
from lodge.core.ids import is_id
from lodge.core.model import Message, Problem, Raises, Thread, ThreadState
from lodge.core.yamlio import quoted

THREADS = "lodge/threads/"
_HEADING = re.compile(r"## Message ([0-9]+)")
_ESCAPE = re.compile(r"^\\*## Message [0-9]+$", re.MULTILINE)
_UNESCAPE = re.compile(r"^\\+## Message [0-9]+$", re.MULTILINE)
_PLAIN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")


def thread_path(thread_id: str) -> str:
    return f"{THREADS}{thread_id}.md"


def parse_thread(path: str, text: str) -> Thread | Problem:
    def build(header: dict[str, object], body: str) -> Thread:
        check_keys(header, ("id", "kind", "about", "raises", "state", "opened"))
        ident = read_id(require(header, "id"), "id", "q")
        if require(header, "kind") != "thread":
            raise FormatError("kind must be 'thread'", "kind")
        about = read_str(require(header, "about"), "about")
        if not is_id(about) or about[:2] not in ("d-", "s-"):
            raise FormatError("about must name a decision or a specification entry", "about")
        raises = read_enum(Raises, require(header, "raises"), "raises")
        state = read_enum(ThreadState, require(header, "state"), "state")
        opened = read_stamp(require(header, "opened"), "opened")
        messages = _messages(body, state, text.count("\n") - body.count("\n"))
        return Thread(ident, about, raises, state, opened, messages)

    return read_with(path, text, build)


def _messages(body: str, state: ThreadState, offset: int) -> tuple[Message, ...]:
    lines = body.split("\n")
    starts = [i for i, line in enumerate(lines) if _HEADING.fullmatch(line)]
    if not starts:
        raise FormatError("a thread needs at least one message")
    if any(line.strip() for line in lines[: starts[0]]):
        raise FormatError("text before ## Message 1")
    result: list[Message] = []
    for n, start in enumerate(starts, 1):
        if lines[start] != f"## Message {n}":
            raise FormatError("messages are numbered 1, 2, 3, in order", line=offset + start + 1)
        end = starts[n] if n < len(starts) else len(lines)
        closing = state is ThreadState.CLOSED and n == len(starts)
        result.append(_message(lines, start + 1, end, offset, closing))
    return tuple(result)


def _message(lines: list[str], first: int, end: int, offset: int, closing: bool) -> Message:
    heading = first
    while first < end and not lines[first].strip():
        first += 1
    split = first
    while split < end and lines[split].strip():
        split += 1
    if first == split:
        raise FormatError("a message needs by and when", line=offset + heading)
    header_text = "\n".join(lines[first:split])
    try:
        header = load_header(header_text)
        check_keys(header, ("by", "when", "where"))
        by = read_str(require(header, "by"), "by")
        when = read_str(require(header, "when"), "when")
        where = read_optional_str(header, "where")
        if by == "author" and where is None:
            raise FormatError("an author message needs where", "where")
        if by != "author":
            when = read_stamp(when, "when")
    except FormatError as error:
        relative = key_line(header_text, error.key) if error.key is not None else error.line
        error.line = offset + first + (relative or 2) - 1
        raise
    text = trim_block("\n".join(lines[split:end]))
    if not text and not closing:
        raise FormatError("message text must not be empty", line=offset + split + 1)
    return Message(by, when, _UNESCAPE.sub(lambda m: m.group()[1:], text), where)


def _quote(key: str, value: str) -> str:
    try:
        return quoted(value)
    except ValueError as error:
        raise ValueError(f"{key}: {error}") from None


def write_thread(thread: Thread) -> str:
    header = [
        f"id: {thread.id}",
        "kind: thread",
        f"about: {thread.about}",
        f"raises: {thread.raises}",
        f"state: {thread.state}",
        f"opened: {thread.opened}",
    ]
    blocks: list[str] = []
    for n, message in enumerate(thread.messages, 1):
        by = message.by if _PLAIN.fullmatch(message.by) else _quote("by", message.by)
        when = _quote("when", message.when) if message.by == "author" else message.when
        meta = [f"by: {by}", f"when: {when}"]
        if message.where is not None:
            meta.append(f"where: {_quote('where', message.where)}")
        text = _ESCAPE.sub(lambda m: "\\" + m.group(), trim_block(message.text))
        blocks.append(f"## Message {n}\n\n" + "\n".join(meta) + (f"\n\n{text}" if text else ""))
    text = assemble(header, "\n\n".join(blocks))
    back = parse_thread(thread_path(thread.id), text)
    if isinstance(back, Problem):
        raise ValueError(f"the thread would not read back: {back.message}")
    if back != thread:
        for n, (original, parsed) in enumerate(
            zip(thread.messages, back.messages, strict=False), 1
        ):
            for field in ("by", "when", "where", "text"):
                if getattr(original, field) != getattr(parsed, field):
                    raise ValueError(
                        f"the thread would not read back unchanged: message {n} {field}"
                    )
        raise ValueError("the thread would not read back unchanged: header or messages")
    return text


def clean_text(text: str) -> str:
    """Remove CR before LF and surrounding whitespace from message text."""
    return text.replace("\r\n", "\n").strip()


def appended(thread: Thread, message: Message, close: bool = False) -> Thread:
    if thread.state is ThreadState.CLOSED:
        raise ValueError("the thread is closed")
    message = replace(message, text=clean_text(message.text))
    if not message.text and not close:
        raise ValueError("message text must not be empty")
    return replace(
        thread,
        messages=(*thread.messages, message),
        state=ThreadState.CLOSED if close else ThreadState.OPEN,
    )


def newest_last(threads: Iterable[Thread]) -> tuple[Thread, ...]:
    return tuple(sorted(threads, key=lambda t: (datetime.fromisoformat(t.opened), t.id)))
