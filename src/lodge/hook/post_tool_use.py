"""The `PostToolUse` hook: after a hand edit of a record file or a frozen file, name what to use."""

import json
import re
from collections.abc import Callable, Mapping, Sequence
from pathlib import Path
from typing import TextIO

from lodge.app import LodgeError

EDIT_TOOLS = frozenset({"Edit", "Write", "MultiEdit"})
ATTACHMENTS = "attachments"

RESTORE = (
    "put back exactly the text you replaced, with the same tool. "
    "Do not run `git checkout`, `git restore`, `git stash`, or `git clean` on this file, "
    "since they also discard changes that are not yours. "
    "If you cannot restore it exactly, tell the author."
)
REVERSE = "Reverse your own edit now: " + RESTORE
ASKED = (
    "If the author asked for this edit, tell her the file is frozen and ask before reversing it."
)
RECORD_TEXT = (
    "{path} is a lodge record file, and lodge owns it: do not edit it by hand. "
    "Run `lodge draft REF` (or `lodge draft area:NAME`) to get it as a draft outside `lodge/`, "
    "edit the draft, check it with `lodge add --dry-run FILE`, then publish it with "
    "`lodge add FILE`. " + REVERSE
)
FROZEN_TEXT = (
    "{path} is frozen: lodge holds its content now, so do not edit it. "
    "Record the change as a new decision instead: write a draft (`lodge guide` shows the "
    "draft format), check it with `lodge add --dry-run FILE`, then publish it with "
    "`lodge add FILE`. " + ASKED + " Otherwise reverse your own edit now: " + RESTORE
)


def parse_hook_settings(table: object) -> tuple[str, ...]:
    """The `frozen` globs of `[hook]`; any other key is an error naming it."""
    if not isinstance(table, Mapping):
        raise LodgeError(".lodge.toml: hook must be a table")
    for key in table:
        if key != "frozen":
            raise LodgeError(f".lodge.toml: unknown key hook.{key}")
    frozen = table.get("frozen", [])
    if not isinstance(frozen, list) or not all(isinstance(glob, str) for glob in frozen):
        raise LodgeError(".lodge.toml: hook.frozen must be a list of strings")
    return tuple(frozen)


def respond(
    payload: Mapping[str, object],
    repo_root: Path,
    data_root: Path | None,
    frozen: Sequence[str],
    cwd: Path | None = None,
) -> dict[str, object] | None:
    """The hook output for one tool call, or None when the edit is not lodge's business.

    A relative path without a payload folder starts from `cwd`, else from the repository root.
    """
    root = repo_root.resolve()
    edited = _edited_path(payload, cwd or root)
    if edited is None:
        return None
    path = edited.resolve()
    if data_root is not None and _is_record(path, data_root.resolve()):
        return _output(RECORD_TEXT, path, root)
    if path.is_relative_to(root) and _is_frozen(path.relative_to(root).as_posix(), frozen):
        return _output(FROZEN_TEXT, path, root)
    return None


def run(
    stdin: TextIO,
    stdout: TextIO,
    context: Callable[[Path], tuple[Path, Path | None, Sequence[str]] | None],
    cwd: Path | None = None,
) -> int:
    """Answer one hook event on `stdout`; always 0, since a hook never fails the tool call.

    `context` takes the edited file and gives the repository root, the folder of the record
    files, and the frozen globs of the repository that file is in, or None where lodge has
    nothing to protect.
    A relative path without a payload folder starts from `cwd`, the process's folder, for both.
    """
    try:
        payload = json.loads(stdin.read())
        edited = _edited_path(payload, cwd) if isinstance(payload, Mapping) else None
        if edited is None:
            return 0
        found = context(edited)
        if found is None:
            return 0
        response = respond(payload, *found, cwd=cwd)
        if response is not None:
            stdout.write(json.dumps(response) + "\n")
    except Exception:
        return 0
    return 0


def _edited_path(payload: Mapping[str, object], fallback: Path | None) -> Path | None:
    """The file an edit tool call names; a relative one starts from the call's own folder."""
    if payload.get("tool_name") not in EDIT_TOOLS:
        return None
    tool_input = payload.get("tool_input")
    if not isinstance(tool_input, Mapping):
        return None
    path = tool_input.get("file_path")
    if not isinstance(path, str) or not path:
        return None
    cwd = payload.get("cwd")
    base = Path(cwd) if isinstance(cwd, str) and cwd else fallback
    return Path(path) if base is None else base / path


def _is_record(path: Path, data_root: Path) -> bool:
    return path.is_relative_to(data_root) and not path.is_relative_to(data_root / ATTACHMENTS)


def _is_frozen(relative: str, frozen: Sequence[str]) -> bool:
    return any(_glob(pattern).fullmatch(relative) for pattern in frozen)


def _glob(pattern: str) -> re.Pattern[str]:
    """A glob over `/`-separated paths: `*` and `?` stay in one segment, `**` crosses them."""
    out: list[str] = []
    i = 0
    while i < len(pattern):
        if pattern.startswith("**/", i):
            out.append("(?:.*/)?")
            i += 3
        elif pattern.startswith("**", i):
            out.append(".*")
            i += 2
        elif pattern[i] == "*":
            out.append("[^/]*")
            i += 1
        elif pattern[i] == "?":
            out.append("[^/]")
            i += 1
        else:
            out.append(re.escape(pattern[i]))
            i += 1
    return re.compile("".join(out))


def _output(template: str, path: Path, root: Path) -> dict[str, object]:
    shown = path.relative_to(root).as_posix() if path.is_relative_to(root) else str(path)
    return {
        "hookSpecificOutput": {
            "hookEventName": "PostToolUse",
            "additionalContext": template.format(path=shown),
        }
    }
