from e2e.conftest import Project
from e2e.support import seed

BRANCH = '[store]\nmode = "branch"\n'


def test_init_branch_mode(project: Project) -> None:
    project.configure(BRANCH)
    result = project.run("init")
    assert (result.code, result.err) == (0, "")
    assert result.out == "created the branch lodge on origin\nnext: lodge guide\n"
    tree = project.git("--git-dir", str(project.remote), "ls-tree", "-r", "--name-only", "lodge")
    assert tree.splitlines() == ["lodge/decisions/.gitkeep", "lodge/spec/.gitkeep"]
    assert project.git("status", "--porcelain") == "?? .lodge.toml"


def test_reads_in_branch_mode_start_with_the_freshness_line(project: Project) -> None:
    project.configure(BRANCH)
    seed(project)
    result = project.run("search", "transcripts")
    assert result.code == 0
    first = result.out.splitlines()[0]
    assert first.startswith("lodge@") and "fetched" in first
