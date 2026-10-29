import io
import json
import sys
from pathlib import Path

import pytest

from e2e.conftest import Project

BRANCH = '[store]\nmode = "branch"\n'


def fire(project: Project, monkeypatch: pytest.MonkeyPatch, path: str) -> tuple[int, str, str]:
    event = {"tool_name": "Write", "tool_input": {"file_path": path}}
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(event)))
    result = project.run("hook", "post-tool-use")
    return result.code, result.out, result.err


def test_hook_names_the_write_path_after_a_hand_edit_of_a_record(
    project: Project, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert project.run("init").code == 0
    path = str(project.root / "lodge" / "decisions" / "d-abc123-slug.md")
    code, out, err = fire(project, monkeypatch, path)
    assert (code, err) == (0, "")
    text = json.loads(out)["hookSpecificOutput"]["additionalContext"]
    assert "lodge/decisions/d-abc123-slug.md" in text and "lodge draft" in text


def test_hook_finds_the_repository_of_the_edited_file_not_of_the_session(
    project: Project, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    assert project.run("init").code == 0
    project.git("commit", "-m", "Store")
    sibling = tmp_path / "sibling"
    project.git("worktree", "add", "-q", "-b", "sibling", str(sibling))
    path = str(sibling / "lodge" / "decisions" / "d-abc123-slug.md")
    code, out, err = fire(project, monkeypatch, path)
    assert (code, err) == (0, "")
    text = json.loads(out)["hookSpecificOutput"]["additionalContext"]
    assert "lodge/decisions/d-abc123-slug.md" in text


def test_hook_finds_the_repository_for_a_file_that_does_not_exist_yet(
    project: Project, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert project.run("init").code == 0
    path = str(project.root / "lodge" / "decisions" / "new" / "deeper" / "d-abc123-slug.md")
    assert "lodge draft" in fire(project, monkeypatch, path)[1]


def test_hook_stays_silent_where_lodge_is_not_initialised(
    project: Project, monkeypatch: pytest.MonkeyPatch
) -> None:
    (project.root / "lodge").mkdir()
    (project.root / "lodge" / "__init__.py").write_text("", encoding="utf-8")
    path = str(project.root / "lodge" / "__init__.py")
    assert fire(project, monkeypatch, path) == (0, "", "")


def test_hook_stays_silent_for_a_file_that_is_not_lodges(
    project: Project, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert fire(project, monkeypatch, str(project.root / "README.md")) == (0, "", "")


def test_hook_reads_the_frozen_globs_from_the_settings(
    project: Project, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert project.run("init").code == 0
    project.configure('[hook]\nfrozen = ["docs/choices.md"]\n')
    code, out, _ = fire(project, monkeypatch, str(project.root / "docs" / "choices.md"))
    assert code == 0
    assert "docs/choices.md is frozen" in json.loads(out)["hookSpecificOutput"]["additionalContext"]


def test_hook_in_branch_mode_protects_frozen_files_only(
    project: Project, monkeypatch: pytest.MonkeyPatch
) -> None:
    project.configure(BRANCH + '[hook]\nfrozen = ["docs/choices.md"]\n')
    record = str(project.root / "lodge" / "decisions" / "d-abc123-slug.md")
    assert fire(project, monkeypatch, record) == (0, "", "")
    _, out, _ = fire(project, monkeypatch, str(project.root / "docs" / "choices.md"))
    assert "is frozen" in out


@pytest.mark.parametrize("text", ["[hook]\nfrozne = []\n", "[hook]\nfrozen = 3\n", "hook = 3\n"])
def test_unknown_hook_setting_is_one_sentence_for_commands_and_silent_for_the_hook(
    project: Project, monkeypatch: pytest.MonkeyPatch, text: str
) -> None:
    project.configure(text)
    for argv in (["init"], ["search", "x"]):
        result = project.run(*argv)
        assert (result.code, result.out) == (2, "")
        assert result.err.startswith("lodge: .lodge.toml: ")
        assert result.err.count("\n") == 1
    path = str(project.root / "docs" / "choices.md")
    assert fire(project, monkeypatch, path) == (0, "", "")


def test_unknown_hook_key_is_named(project: Project) -> None:
    project.configure("[hook]\nfrozne = []\n")
    assert project.run("search", "x").err == "lodge: .lodge.toml: unknown key hook.frozne\n"
