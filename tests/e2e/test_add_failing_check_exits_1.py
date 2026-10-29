from e2e.conftest import Project
from e2e.support import area_text, entry_text, initialise


def test_add_failing_check_exits_1(project: Project) -> None:
    initialise(project)
    entry = project.run("id", "s").out.strip()
    files = [
        project.draft("area.md", area_text(entry)),
        project.draft("entry.md", entry_text(entry)),
    ]
    result = project.run("add", *files)
    assert (result.code, result.err) == (1, "")
    lines = result.out.splitlines()
    assert lines[-1] == "not published: the check failed"
    assert any(line.startswith("check 4: ") and entry in line for line in lines)
    assert project.git("status", "--porcelain", "lodge").count("lodge/spec/storage") == 0
