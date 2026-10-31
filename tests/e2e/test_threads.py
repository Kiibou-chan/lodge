import re

from e2e.conftest import Project
from e2e.support import seed


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
