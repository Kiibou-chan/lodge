"""Multi-ref show prints ordered records and errors through the real command line."""

import sys

import pytest

from e2e.conftest import Project
from e2e.support import decision_text, first_decision, seed


def test_show_three_refs_one_output(project: Project) -> None:
    ids = seed(project)
    draft = project.draft("schedule.md", decision_text("Schedule berths", "code: ITEM-2"))
    added = project.run("add", draft)
    assert added.code == 0
    third = first_decision(added.out)
    result = project.run("show", "ITEM-1", ids.entry, "ITEM-2")
    assert (result.code, result.err) == (0, "")
    assert result.out.startswith(f"{ids.decision} ITEM-1")
    assert result.out.count(f"----- {ids.entry}\n") == 1
    assert result.out.count("----- ITEM-2\n") == 1
    assert result.out.index(ids.decision) < result.out.index(ids.entry) < result.out.index(third)
    repeated = project.run("show", "ITEM-1", ids.decision, ids.entry)
    assert f"----- {ids.decision} is {ids.decision}, shown above\n" in repeated.out
    assert repeated.out.count("Transcripts are kept.") == 1


def test_unknown_ref_exits_2_after_the_others(project: Project) -> None:
    ids = seed(project)
    result = project.run("show", ids.decision, "unknown", ids.entry)
    assert result.code == 2
    assert result.out.index(ids.decision) < result.out.index("----- unknown\n")
    assert result.out.index("----- unknown\n") < result.out.index(f"----- {ids.entry}\n")
    assert "Held." in result.out
    assert result.err == "lodge: no record named unknown\n"
    first_bad = project.run("show", "unknown", ids.decision)
    assert first_bad.code == 2 and first_bad.out.startswith("----- unknown\n")
    assert ids.decision in first_bad.out


def test_stdout_flushed_before_each_error(
    project: Project, monkeypatch: pytest.MonkeyPatch
) -> None:
    ids = seed(project)
    events = []
    original_flush, original_write = sys.stdout.flush, sys.stderr.write

    def flush() -> None:
        events.append("flush")
        original_flush()

    def write(text: str) -> int:
        if text.startswith("lodge:"):
            events.append("error")
        return original_write(text)

    monkeypatch.setattr(sys.stdout, "flush", flush)
    monkeypatch.setattr(sys.stderr, "write", write)
    result = project.run("show", ids.decision, "unknown", ids.entry, "also-unknown")
    assert result.code == 2 and ids.entry in result.out
    assert events.count("error") == 2
    assert all(
        index > 0 and events[index - 1] == "flush"
        for index, event in enumerate(events)
        if event == "error"
    )


def test_single_ref_output_unchanged(project: Project) -> None:
    ids = seed(project)
    shown = project.run("show", "ITEM-1")
    assert shown.code == 0 and not shown.err
    assert shown.out == (
        f"{ids.decision} ITEM-1 · current · coordinator · 2026-10-29 · product\n"
        "Keep transcripts\n\nTranscripts are kept.\n"
    )
