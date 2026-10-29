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
