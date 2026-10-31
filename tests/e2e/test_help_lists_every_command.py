from pathlib import Path

import pytest

from e2e.conftest import Project

COMMANDS = ["init", "id", "search", "show", "draft", "add", "check", "spec", "waiting"]
COMMANDS += ["guide", "view", "hook", "threads", "thread", "ask", "reply", "close"]


def test_help_lists_every_command(project: Project) -> None:
    result = project.run("--help")
    assert (result.code, result.err) == (0, "")
    for name in COMMANDS:
        assert any(line.split()[:1] == [name] for line in result.out.splitlines()), name


@pytest.mark.parametrize("name", COMMANDS)
def test_every_command_has_help(project: Project, name: str) -> None:
    result = project.run(name, "--help")
    assert result.code == 0 and result.out.startswith(f"usage: lodge {name}")


def test_no_command_is_a_usage_error(project: Project) -> None:
    result = project.run()
    assert result.code == 2 and "usage:" in result.err


def test_version_works_anywhere(project: Project, tmp_path: Path) -> None:
    assert project.run("--version", cwd=tmp_path).out == "lodge 0.2.0\n"
