"""A set of store files loaded into records, areas, and the problems found on the way."""

import re
from collections.abc import Mapping
from dataclasses import dataclass, field

from lodge.core.fileformat import parse_area, parse_record
from lodge.core.model import Area, Decision, Problem, SpecEntry, Thread
from lodge.core.threads import parse_thread

Files = Mapping[str, str]
Parsed = Decision | SpecEntry | Area | Thread | Problem

_THREAD_FILE = re.compile(r"lodge/threads/[^/]+\.md")
_DECISION_FILE = re.compile(r"lodge/decisions/[^/]+\.md")
_AREA_FILE = re.compile(r"lodge/spec/[^/]+/_area\.md")
_SPEC_FILE = re.compile(r"lodge/spec/[^/]+/[^/]+\.md")
ATTACHMENTS = "lodge/attachments/"
_STRAY = (
    "this file is not a record; lodge holds decisions in lodge/decisions/, specification "
    "entries in lodge/spec/<area>/, and attachments in lodge/attachments/"
)


def attachment_path(decision_id: str, name: str) -> str:
    """Where the attachment `name` of decision `decision_id` lives in the store."""
    return f"{ATTACHMENTS}{decision_id}/{name}"


@dataclass(frozen=True)
class Tree:
    """The files of one state of the store, and the revision they were read at.

    `blobs` keys every non-attachment file by the blob ID of its bytes read.
    An empty mapping means the tree was built without keys.
    Derived trees in writes, threads, and apply omit keys because they change files;
    cache consumers must parse unkeyed files directly rather than trust stale keys.
    """

    rev: str | None
    files: Files
    attachments: frozenset[str] = frozenset()
    blobs: Mapping[str, str] = field(default_factory=dict)


def same_listing(a: Tree, b: Tree) -> bool:
    """Whether two exact trees hold equal file mappings and attachment sets."""
    return (a.files, a.attachments) == (b.files, b.attachments)


@dataclass(frozen=True)
class Snapshot:
    decisions: Mapping[str, Decision]
    entries: Mapping[str, SpecEntry]
    areas: Mapping[str, Area]
    paths: Mapping[str, str]
    problems: tuple[Problem, ...]
    attachments: frozenset[str]
    threads: Mapping[str, Thread] = field(default_factory=dict)


def parse_file(path: str, text: str) -> Parsed | None:
    """Parse one store file independently of every other file."""
    if path.startswith(ATTACHMENTS):
        return None
    if _THREAD_FILE.fullmatch(path):
        return parse_thread(path, text)
    if _AREA_FILE.fullmatch(path):
        return parse_area(path, text)
    if _DECISION_FILE.fullmatch(path) or _SPEC_FILE.fullmatch(path):
        return parse_record(path, text)
    if path.startswith("lodge/") and not path.endswith("/.gitkeep"):
        return Problem(path, 1, _STRAY)
    return None


def assemble(parsed: Mapping[str, Parsed | None], attachments: frozenset[str]) -> Snapshot:
    """Assemble records, preserving sorted-path duplicate handling and problems."""
    threads: dict[str, Thread] = {}
    decisions: dict[str, Decision] = {}
    entries: dict[str, SpecEntry] = {}
    areas: dict[str, Area] = {}
    paths: dict[str, str] = {}
    problems: list[Problem] = []
    listed = set(attachments)
    for path in sorted(parsed):
        item = parsed[path]
        if path.startswith(ATTACHMENTS):
            listed.add(path)
        elif isinstance(item, Problem):
            problems.append(item)
        elif isinstance(item, Thread):
            _keep_thread(path, item, threads, paths, problems)
        elif isinstance(item, Area):
            _keep_area(item, areas, problems)
        elif isinstance(item, (Decision, SpecEntry)):
            _keep_record(path, item, decisions, entries, paths, problems)
    return Snapshot(decisions, entries, areas, paths, tuple(problems), frozenset(listed), threads)


def load(tree: Tree) -> Snapshot:
    """Every file of `tree` read; a file that does not read, or repeats an ID, is a problem."""
    return assemble(
        {path: parse_file(path, text) for path, text in tree.files.items()}, tree.attachments
    )


def _keep_area(parsed: Area | Problem, areas: dict[str, Area], problems: list[Problem]) -> None:
    if isinstance(parsed, Problem):
        problems.append(parsed)
    else:
        areas[parsed.name] = parsed


def _keep_record(
    path: str,
    parsed: Decision | SpecEntry | Problem,
    decisions: dict[str, Decision],
    entries: dict[str, SpecEntry],
    paths: dict[str, str],
    problems: list[Problem],
) -> None:
    if isinstance(parsed, Problem):
        problems.append(parsed)
        return
    in_decisions = path.startswith("lodge/decisions/")
    if in_decisions != isinstance(parsed, Decision):
        home = "lodge/decisions/" if isinstance(parsed, Decision) else "lodge/spec/<area>/"
        problems.append(Problem(path, 1, f"this record belongs in {home}"))
    elif parsed.id in paths:
        problems.extend(_duplicate(paths[parsed.id], path, parsed.id))
    else:
        paths[parsed.id] = path
        if isinstance(parsed, Decision):
            decisions[parsed.id] = parsed
        else:
            entries[parsed.id] = parsed


def _keep_thread(
    path: str,
    parsed: Thread | Problem,
    threads: dict[str, Thread],
    paths: dict[str, str],
    problems: list[Problem],
) -> None:
    if isinstance(parsed, Problem):
        problems.append(parsed)
    elif parsed.id in paths:
        problems.extend(_duplicate(paths[parsed.id], path, parsed.id))
    else:
        paths[parsed.id] = path
        threads[parsed.id] = parsed


def _duplicate(kept: str, path: str, ident: str) -> tuple[Problem, Problem]:
    message = f"the ID {ident} is in both {kept} and {path}; the first is kept"
    return Problem(kept, 2, message), Problem(path, 2, message)
