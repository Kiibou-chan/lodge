import io
import json
from collections.abc import Callable, Sequence
from pathlib import Path

import pytest

from lodge.app import LodgeError
from lodge.hook import parse_hook_settings, respond, run

Context = tuple[Path, Path | None, Sequence[str]] | None
Finder = Callable[[Path], Context]


def payload(path: str, tool: str = "Edit") -> dict[str, object]:
    return {"tool_name": tool, "tool_input": {"file_path": path}}


def context_text(response: dict[str, object] | None) -> str:
    assert response is not None
    output = response["hookSpecificOutput"]
    assert isinstance(output, dict)
    assert output["hookEventName"] == "PostToolUse"
    text = output["additionalContext"]
    assert isinstance(text, str)
    return text


def drive(raw: str, context: Finder) -> tuple[int, str]:
    out = io.StringIO()
    return run(io.StringIO(raw), out, context), out.getvalue()


def test_record_edit_gets_feedback(tmp_path: Path) -> None:
    data = tmp_path / "lodge"
    for tool in ("Edit", "Write", "MultiEdit"):
        record = str(data / "decisions" / "d-abc123-slug.md")
        text = context_text(respond(payload(record, tool), tmp_path, data, ()))
        assert "lodge/decisions/d-abc123-slug.md" in text
        draft, dry, add = (
            text.index("lodge draft"),
            text.index("lodge add --dry-run"),
            text.rindex("`lodge add FILE`"),
        )
        assert draft < dry < add


def test_relative_record_path_is_read_from_the_repository_root(tmp_path: Path) -> None:
    data = tmp_path / "lodge"
    text = context_text(respond(payload("lodge/spec/area/_area.md"), tmp_path, data, ()))
    assert "lodge/spec/area/_area.md" in text


def test_dotted_path_still_counts_as_a_record(tmp_path: Path) -> None:
    data = tmp_path / "lodge"
    sneaky = str(tmp_path / "docs" / ".." / "lodge" / "decisions" / "d-abc123-slug.md")
    assert respond(payload(sneaky), tmp_path, data, ()) is not None


def test_attachment_edit_gets_nothing(tmp_path: Path) -> None:
    data = tmp_path / "lodge"
    attachment = str(data / "attachments" / "d-abc123" / "notes.md")
    assert respond(payload(attachment), tmp_path, data, ()) is None


def test_frozen_edit_gets_feedback(tmp_path: Path) -> None:
    frozen = ["docs/choices.md", "docs/verdicts/**/*.md"]
    for name in ("docs/choices.md", "docs/verdicts/2026/q4/one.md", "docs/verdicts/two.md"):
        text = context_text(respond(payload(str(tmp_path / name)), tmp_path, None, frozen))
        assert name in text
        assert "lodge add --dry-run" in text
        assert "lodge draft" not in text
        assert "If the author asked for this edit, tell her the file is frozen" in text


def test_frozen_globs_do_not_overreach(tmp_path: Path) -> None:
    frozen = ["docs/*.md", "notes/choices.md"]
    for name in ("docs/deep/one.md", "docs/one.txt", "other/notes/choices.md", "docs"):
        assert respond(payload(str(tmp_path / name)), tmp_path, None, frozen) is None


def test_branch_mode_protects_only_frozen_files(tmp_path: Path) -> None:
    record = str(tmp_path / "lodge" / "decisions" / "d-abc123-slug.md")
    assert respond(payload(record), tmp_path, None, ()) is None


def test_other_edit_gets_nothing(tmp_path: Path) -> None:
    data = tmp_path / "lodge"
    elsewhere = str(tmp_path / "src" / "main.py")
    outside = str(tmp_path.parent / "lodge" / "decisions" / "d-abc123-slug.md")
    assert respond(payload(elsewhere), tmp_path, data, ["docs/*.md"]) is None
    assert respond(payload(outside), tmp_path, data, ()) is None
    record = str(data / "decisions" / "d-abc123-slug.md")
    assert respond(payload(record, "Read"), tmp_path, data, ()) is None
    assert respond(payload(record, "Bash"), tmp_path, data, ()) is None


def test_symlinked_checkout_still_matches(tmp_path: Path) -> None:
    real = tmp_path / "real"
    (real / "lodge" / "decisions").mkdir(parents=True)
    link = tmp_path / "link"
    link.symlink_to(real)
    record = str(link / "lodge" / "decisions" / "d-abc123-slug.md")
    assert respond(payload(record), real, real / "lodge", ()) is not None


@pytest.mark.parametrize(
    "raw",
    [
        "",
        "not json",
        "[]",
        "null",
        '"Edit"',
        "{}",
        '{"tool_name": "Edit"}',
        '{"tool_name": "Edit", "tool_input": []}',
        '{"tool_name": "Edit", "tool_input": {"file_path": 3}}',
        '{"tool_name": "Edit", "tool_input": {"file_path": ""}}',
        '{"tool_name": 3, "tool_input": {"file_path": "x"}}',
    ],
)
def test_bad_payload_exit_0_silent(tmp_path: Path, raw: str) -> None:
    assert drive(raw, lambda _: (tmp_path, tmp_path / "lodge", ["x"])) == (0, "")


def test_unreadable_input_exit_0_silent(tmp_path: Path) -> None:
    class Broken(io.StringIO):
        def read(self, size: int | None = -1) -> str:
            raise OSError("closed")

    out = io.StringIO()
    assert run(Broken(), out, lambda _: (tmp_path, tmp_path / "lodge", ())) == 0
    assert out.getvalue() == ""


def test_context_failure_exit_0_silent(tmp_path: Path) -> None:
    raw = json.dumps(payload(str(tmp_path / "lodge" / "decisions" / "d-abc123-slug.md")))

    def fails(_: Path) -> Context:
        raise LodgeError("not a repository")

    assert drive(raw, fails) == (0, "")
    assert drive(raw, lambda _: None) == (0, "")


def test_run_writes_one_json_line_for_a_record_edit(tmp_path: Path) -> None:
    data = tmp_path / "lodge"
    raw = json.dumps(payload(str(data / "decisions" / "d-abc123-slug.md")))
    code, text = drive(raw, lambda _: (tmp_path, data, ()))
    assert code == 0
    assert text.endswith("\n") and text.count("\n") == 1
    assert "lodge draft" in context_text(json.loads(text))


def test_run_stays_silent_for_an_unwatched_file(tmp_path: Path) -> None:
    raw = json.dumps(payload(str(tmp_path / "src" / "main.py")))
    assert drive(raw, lambda _: (tmp_path, tmp_path / "lodge", ())) == (0, "")


def test_settings_default_to_no_frozen_files() -> None:
    assert parse_hook_settings({}) == ()


def test_settings_read_the_frozen_globs() -> None:
    assert parse_hook_settings({"frozen": ["a.md", "b/**"]}) == ("a.md", "b/**")


@pytest.mark.parametrize(
    ("table", "message"),
    [
        ({"frozne": []}, ".lodge.toml: unknown key hook.frozne"),
        ({"frozen": "a.md"}, ".lodge.toml: hook.frozen must be a list of strings"),
        ({"frozen": ["a.md", 3]}, ".lodge.toml: hook.frozen must be a list of strings"),
    ],
)
def test_bad_settings_are_one_sentence(table: dict[str, object], message: str) -> None:
    with pytest.raises(LodgeError) as caught:
        parse_hook_settings(table)
    assert str(caught.value) == message


def test_a_hook_section_that_is_not_a_table_is_an_error() -> None:
    with pytest.raises(LodgeError, match="hook must be a table"):
        parse_hook_settings([])


def test_record_advice_reverses_the_edit_without_git(tmp_path: Path) -> None:
    record = str(tmp_path / "lodge" / "decisions" / "d-abc123-slug.md")
    frozen = str(tmp_path / "docs" / "choices.md")
    texts = [
        context_text(respond(payload(record), tmp_path, tmp_path / "lodge", ())),
        context_text(respond(payload(frozen), tmp_path, None, ["docs/choices.md"])),
    ]
    for text in texts:
        assert "with the same tool" in text and "tell the author" in text
        assert "undo" not in text.lower()
        warning = text.index("Do not run")
        for command in ("git checkout", "git restore", "git stash", "git clean"):
            assert text.index(command) > warning


def test_frozen_advice_names_the_guide(tmp_path: Path) -> None:
    text = context_text(respond(payload("docs/choices.md"), tmp_path, None, ["docs/*.md"]))
    assert "`lodge guide`" in text


def test_context_is_asked_about_the_edited_file(tmp_path: Path) -> None:
    asked: list[Path] = []

    def context(path: Path) -> Context:
        asked.append(path)
        return None

    absolute = str(tmp_path / "lodge" / "decisions" / "d-abc123-slug.md")
    assert drive(json.dumps(payload(absolute)), context) == (0, "")
    relative = {**payload("lodge/decisions/d.md"), "cwd": str(tmp_path)}
    assert drive(json.dumps(relative), context) == (0, "")
    assert asked == [Path(absolute), tmp_path / "lodge" / "decisions" / "d.md"]


def test_relative_path_is_read_from_the_payload_working_folder(tmp_path: Path) -> None:
    sibling = tmp_path / "sibling"
    event = {**payload("lodge/decisions/d.md"), "cwd": str(sibling)}
    assert respond(event, tmp_path, sibling / "lodge", ()) is not None


def test_relative_path_without_a_payload_folder_is_read_from_the_process_folder(
    tmp_path: Path,
) -> None:
    sub = tmp_path / "sub"
    asked: list[Path] = []

    def context(path: Path) -> Context:
        asked.append(path)
        return tmp_path, sub / "lodge", ()

    out = io.StringIO()
    raw = json.dumps(payload("lodge/decisions/d.md"))
    assert run(io.StringIO(raw), out, context, sub) == 0
    assert asked == [sub / "lodge" / "decisions" / "d.md"]
    assert "sub/lodge/decisions/d.md" in out.getvalue()
