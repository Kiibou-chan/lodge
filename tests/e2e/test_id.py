import re

from e2e.conftest import Project
from e2e.support import initialise


def test_id(project: Project) -> None:
    initialise(project)
    decision = project.run("id", "d")
    entry = project.run("id", "s")
    assert re.fullmatch(r"d-[0-9a-hjkmnp-tv-z]{6}\n", decision.out)
    assert re.fullmatch(r"s-[0-9a-hjkmnp-tv-z]{6}\n", entry.out)
    assert (decision.code, entry.code) == (0, 0)


def test_id_kind_is_d_or_s(project: Project) -> None:
    initialise(project)
    result = project.run("id", "x")
    assert result.code == 2
    assert "invalid choice" in result.err
