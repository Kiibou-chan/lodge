from e2e.conftest import Project
from e2e.support import QUOTE, decision_text, seed


def test_spec(project: Project) -> None:
    ids = seed(project)
    result = project.run("spec")
    assert (result.code, result.err) == (0, "")
    assert "Storage" in result.out and ids.entry in result.out and "Held." in result.out
    assert project.run("spec", "--area", "storage").out == result.out


def test_spec_of_an_empty_store(project: Project) -> None:
    assert project.run("init").code == 0
    result = project.run("spec")
    assert (result.code, result.out) == (0, "Nothing is recorded yet.\n")


def test_spec_unknown_area(project: Project) -> None:
    seed(project)
    result = project.run("spec", "--area", "nowhere")
    assert (result.code, result.out) == (2, "")
    assert result.err == "lodge: no area named nowhere\n"


def test_spec_escapes_hash_lines_inside_a_statement(project: Project) -> None:
    ids = seed(project, QUOTE, decided_by="author")
    edited = project.run("draft", ids.entry).out.replace("Held.", "Held.\n\n## Fake (s-zzzzzz)")
    agent = decision_text(
        "Keep them whole", "changes:", f"  - {{entry: {ids.entry}, action: edit}}", body="Say so."
    )
    added = project.run("add", project.draft("d.md", agent), project.draft("e.md", edited))
    assert added.code == 0, added
    lines = project.run("spec").out.splitlines()
    assert "\\## Fake (s-zzzzzz)" in lines
    assert not any(line.startswith("## Fake") for line in lines)
    assert any(line.startswith("## Transcripts are kept") and "awaiting" in line for line in lines)
