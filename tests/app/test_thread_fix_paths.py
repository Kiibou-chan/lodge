"""Command outcomes and orphaned-thread consumers over synthetic ports."""

from pathlib import Path

import pytest
from support import project, wired

from lodge.app import AddOutcome, Lodge, Written
from lodge.cli.thread_output import thread_head, thread_text, waiting_text
from lodge.cli.threads import Ask, ThreadCommand, Threads, run_thread
from lodge.core import CheckResult, Problem, Raises


def orphan() -> Lodge:
    store = project()
    lodge = wired(store)
    lodge.ask("s-aaaaaa", Raises.DOUBT, "agent", "Why?")
    path = "lodge/threads/q-111111.md"
    store.files[path] = store.files[path].replace("s-aaaaaa", "s-zzzzzz")
    return lodge


def test_orphaned_thread_outputs(capsys: pytest.CaptureFixture[str]) -> None:
    lodge = orphan()
    shown = lodge.thread("q-111111")
    assert "about s-zzzzzz, not found" in thread_head(shown.thread, None).splitlines()
    assert "about s-zzzzzz, not found" in thread_text(shown).splitlines()
    for command in (Threads(), ThreadCommand("q-111111")):
        assert run_thread(command, lodge) == 0
        out = capsys.readouterr().out
        assert "about s-zzzzzz, not found" in out.splitlines()
    assert "about s-zzzzzz, not found" in waiting_text(
        lodge.waiting_all()[0], lodge.threads_waiting()
    )


@pytest.mark.parametrize("outcome,code", [(AddOutcome.PUBLISHED, 0), (AddOutcome.CHECK_FAILED, 1)])
def test_run_thread_outcomes(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
    outcome: AddOutcome,
    code: int,
) -> None:
    lodge = wired(project())
    check = CheckResult((Problem("lodge/threads/q-111111.md", 2, "missing subject"),), ())
    monkeypatch.setattr(Lodge, "ask", lambda *a, **kw: Written(("q-111111",), outcome, check))
    path = tmp_path / "message.txt"
    path.write_text("Why?")
    assert run_thread(Ask("s-aaaaaa", "agent", None, None, Raises.DOUBT, str(path)), lodge) == code
    out = capsys.readouterr().out
    if code:
        assert "missing subject" in out and out.endswith("not published: the check failed\n")
    else:
        assert out == "published q-111111\n"


def test_waiting_reads_one_snapshot() -> None:
    store = project()
    lodge = wired(store)
    lodge.ask("s-aaaaaa", Raises.DOUBT, "agent", "Why?")
    path = "lodge/threads/q-111111.md"
    store.moves_after_read({path: store.files[path].replace("agent", "author")})
    listed, waiting = lodge.waiting_all()
    assert listed.read is waiting.read
    assert [t.id for t in waiting.for_author] == ["q-111111"]
    assert waiting.for_agent == ()
