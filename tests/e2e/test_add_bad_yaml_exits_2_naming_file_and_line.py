from e2e.conftest import Project
from e2e.support import initialise


def test_add_bad_yaml_exits_2_naming_file_and_line(project: Project) -> None:
    initialise(project)
    path = project.draft("broken.md", "---\nkind: decision\ntitle: [unclosed\n---\n\nText.\n")
    result = project.run("add", path)
    assert (result.code, result.out) == (2, "")
    assert result.err.startswith(f"lodge: {path}:")
    assert result.err.count("\n") == 1
    assert path + ":3" in result.err or path + ":4" in result.err


def test_add_missing_fence_exits_2(project: Project) -> None:
    initialise(project)
    path = project.draft("nofence.md", "kind: decision\n")
    result = project.run("add", path)
    assert result.code == 2 and result.err.startswith(f"lodge: {path}")
