from pathlib import Path

from e2e.conftest import Project
from e2e.support import area_text, decision_text, entry_text, first_decision, initialise

BRANCH = '[store]\nmode = "branch"\n'
LOG = "step one\r\nstep two: café\n"


def drafts(project: Project, *extra: str) -> tuple[list[str], str]:
    """A decision that lists `run.log`, its entry, and its area; and the entry's ID."""
    entry = project.run("id", "s").out.strip()
    changes = ["changes:", f"  - {{entry: {entry}, action: create}}", *extra]
    files = [
        project.draft("decision.md", decision_text("Keep logs", *changes)),
        project.draft("entry.md", entry_text(entry)),
        project.draft("area.md", area_text(entry)),
    ]
    return files, entry


def attachment(project: Project, name: str = "run.log", data: bytes | None = None) -> str:
    path = project.draft(name, "")
    Path(path).write_bytes(LOG.encode("utf-8") if data is None else data)
    return path


def test_attachment_lands_beside_the_decision_in_checkout_mode(project: Project) -> None:
    initialise(project)
    files, _ = drafts(project, "attachments: [run.log]")
    result = project.run("add", "--attach", attachment(project), *files)
    assert (result.code, result.err) == (0, "")
    decision = first_decision(result.out)
    stored = project.root / "lodge" / "attachments" / decision / "run.log"
    assert stored.read_bytes() == LOG.encode("utf-8")
    assert f"A  lodge/attachments/{decision}/run.log" in project.git("status", "--porcelain")
    shown = project.run("show", decision, "--provenance")
    assert "attachments: run.log" in shown.out
    assert project.run("check").out == "ok\n"


def test_attachment_lands_on_the_branch_in_branch_mode(project: Project) -> None:
    project.configure(BRANCH)
    initialise(project)
    files, _ = drafts(project, "attachments: [run.log]")
    result = project.run("add", "--attach", attachment(project), *files)
    assert (result.code, result.err) == (0, "")
    decision = first_decision(result.out)
    remote = ["--git-dir", str(project.remote)]
    raw = project.git(*remote, "cat-file", "-s", f"lodge:lodge/attachments/{decision}/run.log")
    assert int(raw) == len(LOG.encode("utf-8"))
    assert "attachments: run.log" in project.run("show", decision, "--provenance").out


def test_several_attachments_and_a_dry_run(project: Project) -> None:
    initialise(project)
    files, _ = drafts(project, "attachments: [run.log, notes.txt]")
    both = ["--attach", attachment(project), "--attach", attachment(project, "notes.txt")]
    dry = project.run("add", "--dry-run", *both, *files)
    assert dry.code == 0 and dry.out.splitlines()[-1] == "dry run: nothing published"
    assert not (project.root / "lodge" / "attachments").exists()
    done = project.run("add", *both, *files)
    assert done.code == 0, done
    decision = first_decision(done.out)
    stored = sorted(p.name for p in (project.root / "lodge" / "attachments" / decision).iterdir())
    assert stored == ["notes.txt", "run.log"]


def test_attachment_that_is_not_utf8_is_refused(project: Project) -> None:
    initialise(project)
    files, _ = drafts(project, "attachments: [run.log]")
    path = attachment(project, data=b"\xff\xfe binary")
    result = project.run("add", "--attach", path, *files)
    assert (result.code, result.out) == (2, "")
    assert result.err == f"lodge: {path}: not UTF-8 text; attachments are text in this version\n"
    assert not (project.root / "lodge" / "attachments").exists()


def test_attach_with_two_new_decisions_is_refused(project: Project) -> None:
    initialise(project)
    files, _ = drafts(project, "attachments: [run.log]")
    other = project.draft("other.md", decision_text("Another"))
    result = project.run("add", "--attach", attachment(project), *files, other)
    assert (result.code, result.out) == (2, "")
    assert result.err == "lodge: --attach needs the add to create one decision, not 2\n"


def test_attach_with_a_missing_file_is_refused(project: Project) -> None:
    initialise(project)
    files, _ = drafts(project, "attachments: [run.log]")
    missing = str(project.root / "nowhere.log")
    result = project.run("add", "--attach", missing, *files)
    assert (result.code, result.out) == (2, "")
    assert (
        result.err.startswith(f"lodge: {missing}: cannot be read") and result.err.count("\n") == 1
    )


def test_decision_that_does_not_list_the_attachment_is_refused(project: Project) -> None:
    initialise(project)
    files, _ = drafts(project)
    result = project.run("add", "--attach", attachment(project), *files)
    assert (result.code, result.out) == (2, "")
    assert result.err.startswith("lodge: the new decision lists [] in attachments")
    assert project.run("search", "logs").out == "no matches\n"
