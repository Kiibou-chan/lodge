import pytest

from e2e.conftest import Project


@pytest.mark.parametrize("argv", [["search", "x"], ["show", "d-aaaaaa"], ["id", "s"], ["check"]])
def test_before_init_one_sentence_exit_2(project: Project, argv: list[str]) -> None:
    result = project.run(*argv)
    assert (result.code, result.out) == (2, "")
    assert result.err == "lodge: lodge has no data in this repository yet; run `lodge init`\n"
