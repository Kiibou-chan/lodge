from e2e.conftest import Project
from e2e.support import area_text, decision_text, entry_text, initialise


def drafts(project: Project, with_decision: bool) -> list[str]:
    entry = project.run("id", "s").out.strip()
    files = [
        project.draft("area.md", area_text(entry)),
        project.draft("entry.md", entry_text(entry)),
    ]
    if with_decision:
        text = decision_text("Keep", "changes:", f"  - {{entry: {entry}, action: create}}")
        files.append(project.draft("decision.md", text))
    return files


def test_add_dry_run_publishes_nothing(project: Project) -> None:
    initialise(project)
    before = project.git("status", "--porcelain")
    result = project.run("add", "--dry-run", *drafts(project, True))
    assert (result.code, result.err) == (0, "")
    assert result.out.splitlines()[-1] == "dry run: nothing published"
    assert project.git("status", "--porcelain") == before
    assert project.run("search", "keep").out == "no matches\n"


def test_add_dry_run_failing_check_exits_1(project: Project) -> None:
    initialise(project)
    result = project.run("add", "--dry-run", *drafts(project, False))
    assert result.code == 1
    lines = result.out.splitlines()
    assert any(line.startswith("check 4: ") for line in lines)
    assert lines[-2:] == ["not published: the check failed", "dry run: nothing published"]


def test_dry_run_marks_new_decision_ids_provisional(project: Project) -> None:
    initialise(project)
    entry = project.run("id", "s").out.strip()
    files = [
        project.draft("area.md", area_text(entry)),
        project.draft("entry.md", entry_text(entry)),
    ]
    text = decision_text(
        "Keep",
        "changes:",
        f"  - {{entry: {entry}, action: create}}",
        body="Transcripts are kept for 40 days.",
    )
    files.append(project.draft("decision.md", text))
    dry = project.run("add", "--dry-run", *files)
    marked = [line for line in dry.out.splitlines() if line.startswith("feedback: d-")]
    assert marked and all(" (provisional): " in line for line in marked)
    real = project.run("add", *files)
    assert "(provisional)" not in real.out


def test_dry_run_marks_new_decision_ids_provisional_on_check_lines(project: Project) -> None:
    initialise(project)
    entry = project.run("id", "s").out.strip()
    files = [
        project.draft("area.md", area_text(entry)),
        project.draft("entry.md", entry_text(entry)),
    ]
    text = decision_text(
        "Keep", "changes:", f"  - {{entry: {entry}, action: create}}", decided_by="author"
    )
    files.append(project.draft("decision.md", text))
    dry = project.run("add", "--dry-run", *files)
    checks = [line for line in dry.out.splitlines() if line.startswith("check 3: ")]
    assert checks and all("(provisional)" in line for line in checks)
    assert "(provisional)" not in project.run("add", *files).out
