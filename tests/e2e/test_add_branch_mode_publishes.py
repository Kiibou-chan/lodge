from e2e.conftest import Project
from e2e.support import area_text, decision_text, entry_text, seed

BRANCH = '[store]\nmode = "branch"\n'


def test_add_branch_mode_publishes(project: Project) -> None:
    project.configure(BRANCH)
    ids = seed(project)
    tree = project.git("--git-dir", str(project.remote), "ls-tree", "-r", "--name-only", "lodge")
    assert f"lodge/spec/storage/{ids.entry}-transcripts-are-kept.md" in tree.splitlines()
    assert any(line.startswith(f"lodge/decisions/{ids.decision}-") for line in tree.splitlines())
    assert project.git("status", "--porcelain") == "?? .lodge.toml"


def test_add_branch_mode_says_published(project: Project) -> None:
    project.configure(BRANCH)
    project.run("init")
    entry = project.run("id", "s").out.strip()
    files = [
        project.draft("area.md", area_text(entry)),
        project.draft("entry.md", entry_text(entry)),
        project.draft(
            "decision.md",
            decision_text("Keep", "changes:", f"  - {{entry: {entry}, action: create}}"),
        ),
    ]
    last = project.run("add", *files).out.splitlines()[-1]
    assert last.startswith("published ") and entry in last.split()
