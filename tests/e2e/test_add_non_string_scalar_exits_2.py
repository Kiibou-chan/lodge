from e2e.conftest import Project
from e2e.support import document, initialise


def test_add_non_string_scalar_exits_2(project: Project) -> None:
    initialise(project)
    text = document(
        ["kind: decision", "title: [a, b]", "scope: product", "decided_by: coordinator"], "Text."
    )
    path = project.draft("scalar.md", text)
    result = project.run("add", path)
    assert (result.code, result.out) == (2, "")
    assert result.err.startswith(f"lodge: {path}:3: ")
    assert "title" in result.err and result.err.count("\n") == 1


def test_yaml_words_that_look_like_values_stay_text(project: Project) -> None:
    initialise(project)
    text = document(
        ["kind: decision", "title: no", "scope: product", "decided_by: coordinator"], "Text."
    )
    result = project.run("add", project.draft("scalar.md", text))
    assert (result.code, result.err) == (0, "")
    shown = project.run("show", result.out.split()[-1])
    assert shown.out.splitlines()[1] == "no"
