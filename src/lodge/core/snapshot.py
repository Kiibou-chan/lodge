"""A set of store files loaded into records, areas, and the problems found on the way."""

import re
from collections.abc import Mapping
from dataclasses import dataclass, field

from lodge.core.fileformat import parse_area, parse_record
from lodge.core.model import Area, Decision, Problem, SpecEntry, Thread
from lodge.core.threads import THREADS, parse_thread

Files = Mapping[str, str]

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
    """The files of one state of the store, and the revision they were read at."""

    rev: str | None
    files: Files
    attachments: frozenset[str] = frozenset()


@dataclass(frozen=True)
class Snapshot:
    decisions: Mapping[str, Decision]
    entries: Mapping[str, SpecEntry]
    areas: Mapping[str, Area]
    paths: Mapping[str, str]
    problems: tuple[Problem, ...]
    attachments: frozenset[str]
    threads: Mapping[str, Thread] = field(default_factory=dict)


def load(tree: Tree) -> Snapshot:
    """Every file of `tree` read; a file that does not read, or repeats an ID, is a problem."""
    threads: dict[str, Thread] = {}
    decisions: dict[str, Decision] = {}
    entries: dict[str, SpecEntry] = {}
    areas: dict[str, Area] = {}
    paths: dict[str, str] = {}
    problems: list[Problem] = []
    attachments = set(tree.attachments)
    for path in sorted(tree.files):
        if path.startswith(ATTACHMENTS):
            attachments.add(path)
        elif re.fullmatch(rf"{THREADS}[^/]+\.md", path):
            _keep_thread(path, parse_thread(path, tree.files[path]), threads, paths, problems)
        elif _AREA_FILE.fullmatch(path):
            _keep_area(parse_area(path, tree.files[path]), areas, problems)
        elif _DECISION_FILE.fullmatch(path) or _SPEC_FILE.fullmatch(path):
            parsed = parse_record(path, tree.files[path])
            _keep_record(path, parsed, decisions, entries, paths, problems)
        elif path.startswith("lodge/") and not path.endswith("/.gitkeep"):
            problems.append(Problem(path, 1, _STRAY))
    return Snapshot(
        decisions, entries, areas, paths, tuple(problems), frozenset(attachments), threads
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
        kept = paths[parsed.id]
        message = f"the ID {parsed.id} is in both {kept} and {path}; the first is kept"
        problems.extend([Problem(kept, 2, message), Problem(path, 2, message)])
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
        kept = paths[parsed.id]
        message = f"the ID {parsed.id} is in both {kept} and {path}; the first is kept"
        problems.extend([Problem(kept, 2, message), Problem(path, 2, message)])
    else:
        paths[parsed.id] = path
        threads[parsed.id] = parsed
