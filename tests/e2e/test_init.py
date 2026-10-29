import os

import pytest

from e2e.conftest import Project


def test_init(project: Project) -> None:
    result = project.run("init")
    assert (result.code, result.err) == (0, "")
    assert result.out == "created lodge/decisions and lodge/spec, staged\nnext: lodge guide\n"
    staged = project.git("diff", "--cached", "--name-only").splitlines()
    assert staged == ["lodge/decisions/.gitkeep", "lodge/spec/.gitkeep"]


def test_init_twice_is_refused(project: Project) -> None:
    project.run("init")
    result = project.run("init")
    assert result.code == 2
    assert result.out == ""
    assert result.err == "lodge: lodge is already initialised: lodge/ exists\n"


@pytest.mark.skipif(os.geteuid() == 0, reason="root can write to a folder with no write mode")
def test_init_in_an_unwritable_checkout(project: Project) -> None:
    project.root.chmod(0o555)
    try:
        result = project.run("init")
    finally:
        project.root.chmod(0o755)
    assert (result.code, result.out) == (2, "")
    assert result.err == "lodge: cannot create lodge/decisions/.gitkeep: Permission denied\n"
