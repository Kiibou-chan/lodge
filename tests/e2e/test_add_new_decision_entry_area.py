from e2e.conftest import Project
from e2e.support import area_text, decision_text, entry_text, first_decision, initialise, seed


def test_add_new_decision_entry_area(project: Project) -> None:
    initialise(project)
    entry = project.run("id", "s").out.strip()
    files = [
        project.draft("area.md", area_text(entry)),
        project.draft("entry.md", entry_text(entry)),
        project.draft(
            "decision.md",
            decision_text(
                "Keep transcripts", "changes:", f"  - {{entry: {entry}, action: create}}"
            ),
        ),
    ]
    result = project.run("add", *files)
    assert (result.code, result.err) == (0, "")
    lines = result.out.splitlines()
    assert lines[-1].startswith("staged ") and entry in lines[-1].split()
    assert any(line.startswith("note: area storage") for line in lines)
    decision = first_decision(result.out)
    assert project.git("status", "--porcelain", "lodge").count("A  lodge/") == 5
    assert project.run("show", decision).code == 0
    assert project.run("check").out == "ok\n"


def test_add_prints_feedback_before_the_outcome(project: Project) -> None:
    initialise(project)
    long_title = "Keep " + "very " * 30 + "long titles"
    entry = project.run("id", "s").out.strip()
    files = [
        project.draft("area.md", area_text(entry)),
        project.draft("entry.md", entry_text(entry, long_title)),
        project.draft(
            "decision.md",
            decision_text("Keep", "changes:", f"  - {{entry: {entry}, action: create}}"),
        ),
    ]
    lines = project.run("add", *files).out.splitlines()
    feedback = [line for line in lines if line.startswith("feedback: ")]
    assert feedback and feedback[0].startswith(f"feedback: {entry}: the title is ")
    assert lines.index(feedback[0]) < len(lines) - 1


def test_add_without_a_file_is_a_usage_error(project: Project) -> None:
    initialise(project)
    result = project.run("add")
    assert result.code == 2 and "usage:" in result.err


def test_add_missing_file(project: Project) -> None:
    initialise(project)
    result = project.run("add", str(project.root / "nowhere.md"))
    assert result.code == 2 and result.out == ""
    assert result.err.startswith("lodge: ") and "nowhere.md" in result.err
    assert result.err.count("\n") == 1


def test_add_file_that_is_not_utf8(project: Project) -> None:
    initialise(project)
    path = project.draft("bad.md", "")
    (project.root.parent / "drafts" / "bad.md").write_bytes(b"---\ntitle: \xff\n---\n")
    result = project.run("add", path)
    assert result.code == 2
    assert result.err == f"lodge: {path}: not UTF-8 text\n"


def test_add_nothing_changed(project: Project) -> None:
    seed(project)
    unchanged = project.run("draft", "area:storage").out
    again = project.run("add", project.draft("area.md", unchanged))
    assert again.code == 0
    assert again.out.splitlines()[-1] == "nothing changed"
    assert "note: nothing changed" not in again.out
