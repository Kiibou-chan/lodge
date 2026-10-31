"""The command line's grammar: argv to one typed command, or an exit status."""

import argparse
from dataclasses import dataclass
from importlib.metadata import version
from typing import Literal

from lodge.core import Filters, Scope

DEFAULT_PORT = 8787
HOOK_EVENT = "post-tool-use"


@dataclass(frozen=True)
class Init:
    pass


@dataclass(frozen=True)
class NewId:
    prefix: Literal["d", "s"]


@dataclass(frozen=True)
class Search:
    query: str
    filters: Filters
    limit: int = 20


@dataclass(frozen=True)
class Show:
    ref: str
    reasoning: bool
    provenance: bool


@dataclass(frozen=True)
class Draft:
    ref: str


@dataclass(frozen=True)
class Add:
    files: tuple[str, ...]
    importing: bool
    dry_run: bool
    attachments: tuple[str, ...]


@dataclass(frozen=True)
class Check:
    gate: bool


@dataclass(frozen=True)
class Spec:
    area: str | None


@dataclass(frozen=True)
class Waiting:
    pass


@dataclass(frozen=True)
class Guide:
    pass


@dataclass(frozen=True)
class View:
    port: int


@dataclass(frozen=True)
class Hook:
    event: str


Command = Init | NewId | Search | Show | Draft | Add | Check | Spec | Waiting | Guide | View | Hook


def parse(argv: list[str]) -> Command | int:
    """The command `argv` names; the exit status instead when argparse has already answered."""
    if argv[:1] == ["hook"] and not {"-h", "--help"} & set(argv):
        return Hook(argv[1] if len(argv) > 1 else "")
    parser = _parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as stop:
        return stop.code if isinstance(stop.code, int) else 2
    command: Command = args.build(args)
    return command


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="lodge",
        description="Decisions and specification entries for agent-built software.",
        epilog="Agents: start with `lodge guide`.",
    )
    parser.add_argument("--version", action="version", version=f"lodge {version('lodge')}")
    commands = parser.add_subparsers(
        dest="command", title="commands", metavar="COMMAND", required=True
    )

    def add(name: str, summary: str, build: object) -> argparse.ArgumentParser:
        sub = commands.add_parser(name, help=summary, description=summary)
        sub.set_defaults(build=build)
        return sub

    add("init", "create the empty store in this repository", lambda _: Init())
    ids = add("id", "print a new ID for a decision (d) or a specification entry (s)", _new_id)
    ids.add_argument("prefix", choices=("d", "s"))
    _search(add("search", "find records by words, ID, or code; one level-1 block each", _search_of))
    _show(add("show", "show one record; reasoning and provenance only when asked for", _show_of))
    draft = add(
        "draft",
        "print the file of an entry to edit and add; area:<name> for an area; "
        "a decision is immutable, so change it with a new decision that replaces or narrows it",
        _draft_of,
    )
    draft.add_argument("ref", help="an ID, a code, or area:<name>")
    _add(add("add", "add draft files: new records, edits, areas", _add_of))
    check = add("check", "run the checks; --gate compares with the published state", _check_of)
    check.add_argument("--gate", action="store_true", help="the check that gates publication")
    spec = add(
        "spec",
        "print the readable specification: areas by rank, entries after what they rest on",
        _spec_of,
    )
    spec.add_argument("--area", help="only this area")
    add("waiting", "list the agent decisions that wait for the author", lambda _: Waiting())
    add("guide", "print the guide for agents", lambda _: Guide())
    view = add("view", "serve the read-only viewer on this machine", _view_of)
    view.add_argument("--port", type=int, default=DEFAULT_PORT, help=f"default {DEFAULT_PORT}")
    hook = add("hook", "answer a Claude Code hook event: post-tool-use", lambda a: Hook(a.event))
    hook.add_argument("event", choices=(HOOK_EVENT,))
    return parser


def _positive(text: str) -> int:
    if not text.isdecimal() or int(text) < 1:
        raise argparse.ArgumentTypeError(f"{text!r} is not a positive whole number")
    return int(text)


def _search(sub: argparse.ArgumentParser) -> None:
    sub.add_argument(
        "query",
        nargs="?",
        default="",
        help="words, an ID, or a code; empty lists records newest first, up to --limit",
    )
    sub.add_argument("--kind", choices=("decision", "spec"))
    sub.add_argument("--scope", choices=[s.value for s in Scope])
    sub.add_argument(
        "--status", choices=("current", "replaced", "retired", "any"), default="current"
    )
    sub.add_argument("--area", help="an area; a decision's areas are those of its entries")
    sub.add_argument("--by", help="who decided, such as author or an agent role")
    sub.add_argument("--limit", type=_positive, default=20, help="records to list; default 20")


def _show(sub: argparse.ArgumentParser) -> None:
    sub.add_argument("ref", help="an ID or a code")
    sub.add_argument("--reasoning", action="store_true", help="add level 2")
    sub.add_argument("--provenance", action="store_true", help="add level 3")


def _add(sub: argparse.ArgumentParser) -> None:
    sub.add_argument("files", nargs="+", metavar="FILE")
    sub.add_argument(
        "--import", dest="importing", action="store_true", help="records with imported_from"
    )
    sub.add_argument("--dry-run", action="store_true", help="apply and check, publish nothing")
    sub.add_argument(
        "--attach",
        action="append",
        default=[],
        metavar="PATH",
        help="a text file kept beside the one new decision; repeat for more",
    )


def _new_id(args: argparse.Namespace) -> Command:
    return NewId("d" if args.prefix == "d" else "s")


def _search_of(args: argparse.Namespace) -> Command:
    filters = Filters(
        kind=None if args.kind is None else ("decision" if args.kind == "decision" else "spec"),
        scope=None if args.scope is None else Scope(args.scope),
        status=args.status,
        area=args.area,
        decided_by=args.by,
    )
    return Search(args.query, filters, args.limit)


def _show_of(args: argparse.Namespace) -> Command:
    return Show(args.ref, args.reasoning, args.provenance)


def _draft_of(args: argparse.Namespace) -> Command:
    return Draft(args.ref)


def _add_of(args: argparse.Namespace) -> Command:
    return Add(tuple(args.files), args.importing, args.dry_run, tuple(args.attach))


def _check_of(args: argparse.Namespace) -> Command:
    return Check(args.gate)


def _spec_of(args: argparse.Namespace) -> Command:
    return Spec(args.area)


def _view_of(args: argparse.Namespace) -> Command:
    return View(args.port)
