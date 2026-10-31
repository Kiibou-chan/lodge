"""Records and file sets for the snapshot tests; the project is made up."""

from itertools import count
from typing import Any

from lodge.core import (
    Area,
    Decision,
    Message,
    Problem,
    Quote,
    Raises,
    Record,
    Scope,
    Snapshot,
    SpecEntry,
    Thread,
    ThreadState,
    Tree,
    area_path,
    new_record_path,
    thread_path,
    write_area,
    write_record,
    write_thread,
)

_ALPHABET = "0123456789abcdefghjkmnpqrstvwxyz"
_NUMBERS = count(1)


def next_id(prefix: str) -> str:
    n = next(_NUMBERS)
    return (
        f"{prefix}-{_ALPHABET[(n // 1024) % 32]}{_ALPHABET[(n // 32) % 32]}{_ALPHABET[n % 32]}000"
    )


def at(minute: int) -> str:
    """A timestamp `minute` minutes into a fixed hour of a fixed day, in a fixed offset."""
    return f"2026-10-28T{10 + minute // 60:02d}:{minute % 60:02d}:00+01:00"


def decision(**kw: Any) -> Decision:
    kw.setdefault("id", next_id("d"))
    kw.setdefault("title", "A decision")
    kw.setdefault("scope", Scope.PRODUCT)
    kw.setdefault("decided_by", "coordinator")
    kw.setdefault("date", at(0))
    kw.setdefault("statement", "A statement.")
    if kw["decided_by"] == "author" and "quote" not in kw and "imported_from" not in kw:
        kw["quote"] = Quote("Do it.", "a session", "2026-10-28 10:00")
    return Decision(**kw)


def entry(**kw: Any) -> SpecEntry:
    kw.setdefault("id", next_id("s"))
    kw.setdefault("area", "storage")
    kw.setdefault("title", "An entry")
    kw.setdefault("statement", "What holds now.")
    return SpecEntry(**kw)


def area(**kw: Any) -> Area:
    kw.setdefault("name", "storage")
    kw.setdefault("title", "Storage")
    kw.setdefault("intro", "")
    kw.setdefault("order", ())
    return Area(**kw)


def files_of(*records: Record | Area | Thread) -> dict[str, str]:
    """The store files for `records`, keyed by their paths."""
    files: dict[str, str] = {}
    for item in records:
        if isinstance(item, Thread):
            files[thread_path(item.id)] = write_thread(item)
        elif isinstance(item, Area):
            files[area_path(item.name)] = write_area(item)
        else:
            files[new_record_path(item)] = write_record(item)
    return files


def snapshot_of(
    *items: Record | Area | Thread,
    attachments: tuple[str, ...] = (),
    paths: dict[str, str] | None = None,
    problems: tuple[Problem, ...] = (),
) -> Snapshot:
    """A snapshot holding `items` as given, without reading files, so that defects can be built."""
    located = {i.id: thread_path(i.id) for i in items if isinstance(i, Thread)}
    located |= {i.id: new_record_path(i) for i in items if isinstance(i, Record)} | (paths or {})
    return Snapshot(
        {i.id: i for i in items if isinstance(i, Decision)},
        {i.id: i for i in items if isinstance(i, SpecEntry)},
        {i.name: i for i in items if isinstance(i, Area)},
        located,
        problems,
        frozenset(attachments),
        {i.id: i for i in items if isinstance(i, Thread)},
    )


def tree_of(*items: Record | Area | Thread) -> Tree:
    """A tree holding the files of `items`."""
    return Tree(None, files_of(*items))


def message(**kw: Any) -> Message:
    kw.setdefault("by", "coordinator")
    kw.setdefault("when", at(0))
    kw.setdefault("text", "A message.")
    return Message(**kw)


def thread(**kw: Any) -> Thread:
    kw.setdefault("id", next_id("q"))
    kw.setdefault("about", "s-aaaaaa")
    kw.setdefault("raises", Raises.DOUBT)
    kw.setdefault("state", ThreadState.OPEN)
    kw.setdefault("opened", at(0))
    kw.setdefault("messages", (message(),))
    return Thread(**kw)
