import re
from importlib.resources import files
from pathlib import Path

from e2e.conftest import Project


def test_guide(project: Project, tmp_path: Path) -> None:
    outside = tmp_path / "plain"
    outside.mkdir()
    result = project.run("guide", cwd=outside)
    assert (result.code, result.err) == (0, "")
    assert result.out == files("lodge.cli").joinpath("guide.md").read_text(encoding="utf-8")


def test_guide_is_short_and_covers_the_write_path(project: Project) -> None:
    text = project.run("guide").out
    assert len(text.splitlines()) <= 60
    assert "—" not in text
    for phrase in (
        "lodge id s",
        "lodge draft",
        "lodge add --dry-run",
        "lodge/attachments/<decision id>/<name>",
        "lodge add --attach PATH FILE...",
        "In checkout mode `add` stages the files",
        "replaces: [d-xxxxxx]",
        "quote: {text, where, when}",
        "never edit",
    ):
        assert phrase in text.replace("Never edit", "never edit")


def test_guide_names_the_author_not_a_person(project: Project) -> None:
    text = project.run("guide").out
    assert not re.search(r"\b(her|hers|she)\b", text, re.IGNORECASE)


def test_guide_names_rests_on_and_link(project: Project) -> None:
    out = project.run("guide").out
    assert "rests_on" in out and "action `link`" in out
    assert "\n\n```\n---" in out
    assert "Transcripts are kept whole.\n```\n\n" in out


def test_guide_says_waiting_first(project: Project) -> None:
    text = project.run("guide").out
    assert (
        "Run `lodge waiting` at the start of a session, and answer what waits for an agent first."
        in text
    )
    assert (
        "`lodge threads` lists the open doubts and questions, and `lodge thread Q` shows one."
        in text
    )
    assert "close a thread only when the author asked for it." in text
    assert (
        "Write `--by author` only with the author's words verbatim, with `--where` and `--when`."
        in text
    )


def test_guide_restores_introduction_and_heading_spacing(project: Project) -> None:
    text = project.run("guide").out
    assert "lodge holds a project's decisions and specification entries." in text
    assert "An area is a named group with a title, an intro, and the order of its entries." in text
    assert all(
        not lines[i + 1]
        for lines in [text.splitlines()]
        for i, line in enumerate(lines)
        if line.startswith("#")
    )
    assert len(text.splitlines()) <= 60
