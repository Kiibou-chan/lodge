"""Running one parsed command against the operations."""

import sys
from collections.abc import Callable, Sequence
from importlib.resources import files
from pathlib import Path

from lodge.app import AddOutcome, Lodge
from lodge.cli.files import read_file
from lodge.cli.output import (
    DECISION_DRAFT_NOTE,
    NO_MATCHES,
    NOTHING_RECORDED,
    added_lines,
    check_lines,
    is_decision_file,
    listed_text,
    read_lines,
    shown_text,
)
from lodge.cli.parser import (
    HOOK_EVENT,
    Add,
    Check,
    Draft,
    Guide,
    Hook,
    Init,
    NewId,
    Search,
    Show,
    Spec,
    View,
    Waiting,
    parse,
)
from lodge.cli.thread_output import waiting_text
from lodge.cli.threads import Ask, Close, Reply, ThreadCommand, Threads, run_thread


def run(
    argv: Sequence[str],
    make_lodge: Callable[[], Lodge],
    init: Callable[[], str],
    view: Callable[[int, tuple[str, ...]], int],
    hook: Callable[[], int],
) -> int:
    """Parse `argv` and run the command; the exit status, 0, 1 for a failed check, 2 for usage.

    The callables build what a command needs only when it needs it, so `--version`, `guide`,
    and `hook` run anywhere.
    """
    command = parse(list(argv))
    if isinstance(command, int):
        return command
    match command:
        case Init():
            print(init())
            print("next: lodge guide")
        case NewId(prefix):
            print(make_lodge().mint(prefix))
        case Search(query, filters, limit):
            print(listed_text(make_lodge().search(query, filters, limit), NO_MATCHES))
        case Show(ref, reasoning, provenance):
            print(shown_text(make_lodge().show(ref, reasoning, provenance)))
        case Draft(ref):
            text = make_lodge().draft(ref)
            if is_decision_file(text):
                print(DECISION_DRAFT_NOTE, file=sys.stderr)
            print(text, end="")
        case Add(names, importing, dry_run, attach):
            drafts, attachments = _read_drafts(names), _read_attachments(attach)
            return _add(make_lodge, drafts, importing, dry_run, attachments)
        case Check(gate):
            return _check(make_lodge(), gate)
        case Spec(area):
            text, read, _ = make_lodge().spec(area)
            print("\n".join([*read_lines(read), text.rstrip("\n") or NOTHING_RECORDED]))
        case Waiting():
            lodge = make_lodge()
            print(waiting_text(lodge.waiting(), lodge.threads_waiting()))
        case Threads() | ThreadCommand() | Ask() | Reply() | Close():
            return run_thread(command, make_lodge())
        case Guide():
            print(files("lodge.cli").joinpath("guide.md").read_text(encoding="utf-8"), end="")
        case View(port, allow_hosts):
            if any(not h or "/" in h or any(c.isspace() for c in h) for h in allow_hosts):
                print("lodge: --allow-host needs a host without whitespace or /", file=sys.stderr)
                return 2
            return view(port, allow_hosts)
        case Hook(event):
            return hook() if event == HOOK_EVENT else 0
    return 0


def _add(
    make_lodge: Callable[[], Lodge],
    drafts: list[tuple[str, str]],
    importing: bool,
    dry_run: bool,
    attachments: list[tuple[str, str]],
) -> int:
    added = make_lodge().add(drafts, importing, dry_run, attachments)
    print("\n".join(added_lines(added, dry_run)))
    return 1 if added.outcome is AddOutcome.CHECK_FAILED else 0


def _check(lodge: Lodge, gate: bool) -> int:
    result, read = lodge.check(gate)
    lines = [*read_lines(read), *check_lines(result, read.unrecorded)]
    print("\n".join(lines))
    return 0 if result.ok else 1


def _read_drafts(names: Sequence[str]) -> list[tuple[str, str]]:
    return [(name, read_file(name, "not UTF-8 text", False)) for name in names]


def _read_attachments(paths: Sequence[str]) -> list[tuple[str, str]]:
    """Each file by its base name, with its text exactly as it is, line endings included."""
    problem = "not UTF-8 text; attachments are text in this version"
    return [(Path(path).name, read_file(path, problem, True)) for path in paths]
