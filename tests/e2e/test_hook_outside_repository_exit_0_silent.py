from pathlib import Path

from e2e.conftest import Project


def test_hook_outside_repository_exit_0_silent(project: Project, tmp_path: Path) -> None:
    plain = tmp_path / "plain"
    plain.mkdir()
    result = project.run("hook", "post-tool-use", cwd=plain)
    assert (result.code, result.out, result.err) == (0, "", "")


def test_hook_with_a_malformed_settings_file_stays_silent(project: Project) -> None:
    project.configure("[store\n")
    result = project.run("hook", "post-tool-use")
    assert (result.code, result.out, result.err) == (0, "", "")


def test_hook_with_an_unknown_event_stays_silent(project: Project) -> None:
    result = project.run("hook", "whenever")
    assert (result.code, result.out, result.err) == (0, "", "")
