from e2e.conftest import Project
from e2e.support import QUOTE, decision_text, entry_text, seed
from gitstore.repos import clone, git

BRANCH = '[store]\nmode = "branch"\n'
SAID = "the lodge branch was rewritten since lodge last accepted it"
TELL = "tell the author; only the author accepts a rewrite"


def rewritten(project: Project) -> str:
    """A branch-mode project whose author decision was reworded by an amended force push."""
    project.configure(BRANCH)
    ids = seed(project, QUOTE, decided_by="author")
    other = clone(project.remote, "rewriter")
    git(other, "fetch", "origin", "lodge")
    git(other, "checkout", "-q", "-b", "lodge", "FETCH_HEAD")
    path = next((other / "lodge" / "decisions").glob(f"{ids.decision}-*.md"))
    path.write_text(path.read_text(encoding="utf-8").replace("are kept", "are dropped"))
    git(other, "commit", "-q", "--amend", "-a", "-m", "tidied")
    git(other, "push", "--force", "origin", "lodge")
    return ids.decision


def another_add(project: Project) -> tuple[int, str]:
    entry = project.run("id", "s").out.strip()
    files = [
        project.draft(
            "decision2.md",
            decision_text("Keep logs", "changes:", f"  - {{entry: {entry}, action: create}}"),
        ),
        project.draft("entry2.md", entry_text(entry, "Logs are kept")),
    ]
    added = project.run("add", *files)
    return added.code, added.out


def test_rewritten_branch_is_said_and_the_gate_fails(project: Project) -> None:
    decision = rewritten(project)
    shown = project.run("show", decision)
    assert shown.code == 0
    assert SAID in shown.out and TELL in shown.out
    assert "git update-ref -d refs/lodge/accepted" in shown.out
    gate = project.run("check", "--gate")
    assert gate.code == 1
    assert any(line.startswith("check 5: ") and decision in line for line in gate.out.splitlines())


def test_a_git_fetch_first_does_not_hide_it(project: Project) -> None:
    decision = rewritten(project)
    project.git("fetch", "origin")
    assert SAID in project.run("show", decision).out
    assert project.run("check", "--gate").code == 1


def test_add_refuses_after_a_rewrite_and_the_gate_still_fails(project: Project) -> None:
    decision = rewritten(project)
    code, out = another_add(project)
    assert code == 1
    assert any(line.startswith("check 5: ") and decision in line for line in out.splitlines())
    assert "not published" in out
    assert SAID in out and TELL in out
    assert SAID in project.run("show", decision).out
    assert project.run("check", "--gate").code == 1


def test_acknowledging_the_rewrite_clears_it(project: Project) -> None:
    decision = rewritten(project)
    project.git("update-ref", "-d", "refs/lodge/accepted")
    shown = project.run("show", decision)
    assert SAID not in shown.out
    assert project.run("check", "--gate").code == 0
    assert another_add(project)[0] == 0
