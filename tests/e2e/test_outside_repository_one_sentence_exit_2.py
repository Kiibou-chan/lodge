from pathlib import Path

import pytest

from e2e.conftest import Project


@pytest.mark.parametrize("argv", [["init"], ["search", "x"], ["id", "d"], ["check"], ["waiting"]])
def test_outside_repository_one_sentence_exit_2(
    project: Project, tmp_path: Path, argv: list[str]
) -> None:
    plain = tmp_path / "plain"
    plain.mkdir()
    result = project.run(*argv, cwd=plain)
    assert (result.code, result.out) == (2, "")
    assert result.err == f"lodge: {plain} is not inside a git repository\n"
