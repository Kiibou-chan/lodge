import re

import pytest

from e2e.conftest import Project
from e2e.support import seed
from lodge.core import Tree, load


def test_ask_reply_close_round_trip(project: Project) -> None:
    entry = seed(project).entry
    opened = project.run(
        "ask",
        entry,
        "--kind",
        "doubt",
        "--by",
        "coordinator",
        project.draft("ask.txt", "First question"),
    )
    assert opened.code == 0, opened
    assert opened.out.startswith("staged q-")
    q = opened.out.split()[-1]
    assert q in project.run("threads").out
    assert "1 message ·" in project.run("threads").out
    assert (
        project.run(
            "reply", q, "--by", "reviewer", project.draft("reply.txt", "Second answer")
        ).code
        == 0
    )
    shown = project.run("thread", q).out
    assert shown.index("First question") < shown.index("Second answer")
    assert "2 messages · last by reviewer" in shown
    assert project.run("close", q, "--by", "coordinator").code == 0
    assert project.run("threads").out == "no open threads\n"
    shown = project.run("thread", q).out
    assert re.match(r"closed by coordinator · .+", shown.splitlines()[-1])
    assert "Closed." not in shown


def test_author_message_needs_where_and_when_exit_2(project: Project) -> None:
    entry = seed(project).entry
    for extra in ((), ("--where", "chat"), ("--when", "2026-10-31 12:00")):
        result = project.run(
            "ask",
            entry,
            "--kind",
            "question",
            "--by",
            "author",
            *extra,
            project.draft("message.txt", "Why?"),
        )
        assert result.code == 2
        assert (
            "a message by author needs --where and --when, the place and time of the author's words"
            in result.err
        )


def test_where_with_an_agent_role_exit_2(project: Project) -> None:
    entry = seed(project).entry
    result = project.run(
        "ask",
        entry,
        "--kind",
        "question",
        "--by",
        "reviewer",
        "--where",
        "chat",
        project.draft("message.txt", "Why?"),
    )
    assert result.code == 2
    assert "--where and --when are for messages by author" in result.err


def test_ask_on_unknown_ref_exit_2(project: Project) -> None:
    seed(project)
    result = project.run(
        "ask",
        "s-aaaaaa",
        "--kind",
        "doubt",
        "--by",
        "reviewer",
        project.draft("message.txt", "Why?"),
    )
    assert result.code == 2
    assert "s-aaaaaa" in result.err and "usage:" not in result.err


def test_thread_files_are_staged_not_committed(project: Project) -> None:
    entry = seed(project).entry
    before = project.git("rev-parse", "HEAD")
    result = project.run(
        "ask", entry, "--kind", "question", "--by", "reviewer", project.draft("message.txt", "Why?")
    )
    assert result.code == 0, result
    q = result.out.split()[-1]
    assert f"lodge/threads/{q}.md" in project.git("diff", "--cached", "--name-only")
    assert project.git("rev-parse", "HEAD") == before


def test_author_words_are_recorded_exactly(project: Project) -> None:
    entry = seed(project).entry
    result = project.run(
        "ask",
        entry,
        "--kind",
        "question",
        "--by",
        "author",
        "--where",
        "chat",
        "--when",
        "2026-10-31 12:00",
        project.draft("words.txt", "  a\rb\r\nc\r\nd  "),
    )
    assert result.code == 0, result
    q = result.out.split()[-1]
    shown = project.run("thread", q)
    assert shown.code == 0 and shown.err == ""
    assert "author · 2026-10-31 12:00 · chat\na\rb\nc\nd" in shown.out
    raw = (project.root / f"lodge/threads/{q}.md").read_bytes().decode("utf-8")
    assert (
        load(Tree(None, {f"lodge/threads/{q}.md": raw})).threads[q].messages[0].text == "a\rb\nc\nd"
    )


@pytest.mark.parametrize("action", ["reply", "close"])
def test_reply_to_unknown_or_closed_thread_exit_2(project: Project, action: str) -> None:
    entry = seed(project).entry
    message = project.draft("message.txt", "Again")
    unknown = project.run(action, "q-000000", "--by", "reviewer", message)
    assert unknown.code == 2 and "no thread named q-000000" in unknown.err
    opened = project.run("ask", entry, "--kind", "doubt", "--by", "reviewer", message)
    q = opened.out.split()[-1]
    assert project.run("close", q, "--by", "reviewer").code == 0
    closed = project.run(action, q, "--by", "reviewer", message)
    assert closed.code == 2 and f"{q} is closed" in closed.err


@pytest.mark.parametrize("bad", ["missing", "non-utf8"])
def test_missing_message_file_exit_2(project: Project, bad: str) -> None:
    entry = seed(project).entry
    path = project.root.parent / "bad.txt"
    if bad == "non-utf8":
        path.write_bytes(b"\xff")
    result = project.run("ask", entry, "--kind", "question", "--by", "reviewer", str(path))
    assert result.code == 2 and result.err.startswith("lodge:")
    assert ("not UTF-8 text" if bad == "non-utf8" else "bad.txt") in result.err
