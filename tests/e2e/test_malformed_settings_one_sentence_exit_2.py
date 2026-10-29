import pytest

from e2e.conftest import Project


@pytest.mark.parametrize(
    ("text", "start"),
    [
        ("[store\n", "lodge: .lodge.toml: "),
        ("[nonsense]\n", "lodge: .lodge.toml: unknown section [nonsense]"),
        ('[store]\nmode = "tree"\n', "lodge: .lodge.toml: store.mode must be"),
    ],
)
def test_malformed_settings_one_sentence_exit_2(project: Project, text: str, start: str) -> None:
    project.configure(text)
    for argv in (["init"], ["search", "x"]):
        result = project.run(*argv)
        assert (result.code, result.out) == (2, "")
        assert result.err.startswith(start) and result.err.count("\n") == 1


def test_settings_are_not_needed_for_the_guide(project: Project) -> None:
    project.configure("[store\n")
    assert project.run("guide").code == 0
