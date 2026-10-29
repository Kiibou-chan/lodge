"""Turning parsed drafts into the files an add writes."""

from collections.abc import Sequence
from dataclasses import dataclass, field, replace

from lodge.core.derive import derive
from lodge.core.drafts import Draft, record_from_draft
from lodge.core.fileformat import area_path, content_hash, new_record_path, write_area, write_record
from lodge.core.ids import is_id
from lodge.core.model import Action, Area, Decision, Problem, Record, SpecEntry
from lodge.core.snapshot import Snapshot, Tree, load


class StaleBase(Problem):
    """An edit draft made from a file that has changed since."""


@dataclass(frozen=True)
class Applied:
    """The files to write, and the IDs of the decisions and entries they hold, in draft order."""

    files: dict[str, str]
    ids: tuple[str, ...]


@dataclass
class _Add:
    current: Snapshot
    tree: Tree
    date: str
    importing: bool
    new_ids: list[str]
    drafted_areas: set[str]
    files: dict[str, str] = field(default_factory=dict)
    ids: list[str] = field(default_factory=list)
    areas: dict[str, Area] = field(default_factory=dict)
    new_entries: list[SpecEntry] = field(default_factory=list)
    retired: set[str] = field(default_factory=set)


def apply_drafts(
    current: Snapshot,
    tree: Tree,
    drafts: Sequence[Draft],
    new_decision_ids: Sequence[str],
    date: str,
    importing: bool,
) -> Applied | list[Problem]:
    """The files that `drafts` change, or the problems that stop them.

    A decision draft without an ID is new and takes the next of `new_decision_ids`, lowest
    first, so decisions of one add keep their draft order.
    A draft with an ID that exists is an edit and needs the `base` of the file in `tree`.
    """
    new_drafts = [d for d in drafts if d.kind == "decision" and "id" not in d.header]
    if len(new_drafts) != len(new_decision_ids):
        raise ValueError(
            f"{len(new_drafts)} new decision drafts but {len(new_decision_ids)} IDs were given"
        )
    names = {
        name for d in drafts if d.kind == "area" and isinstance(name := d.header.get("name"), str)
    }
    add = _Add(current, tree, date, importing, sorted(new_decision_ids), names)
    problems: list[Problem] = []
    for draft in drafts:
        found = _apply_one(add, draft)
        if found is not None:
            problems.append(found)
    problems += _area_files(add)
    if problems:
        return problems
    return Applied(add.files, tuple(add.ids))


def _apply_one(add: _Add, draft: Draft) -> Problem | None:
    if draft.kind == "decision":
        return _decision(add, draft)
    if draft.kind == "spec":
        return _entry(add, draft)
    return _area(add, draft)


def _decision(add: _Add, draft: Draft) -> Problem | None:
    given = draft.header.get("id")
    if given is None:
        if "base" in draft.header:
            return _refuse(
                draft,
                "base is for edits, but this draft has no id and would add a new decision; "
                "keep the id that lodge draft printed to edit one",
            )
        if "imported_from" in draft.header and not add.importing:
            return _refuse(draft, _NEEDS_FLAG)
        path, record_id, date = None, add.new_ids.pop(0), add.date
    else:
        if not isinstance(given, str) or not _is_id(given, "d"):
            return _refuse(draft, _not_an_id(given, "d"))
        if given not in add.current.decisions:
            return _refuse(
                draft, f"the decision {given} does not exist; a new decision draft carries no id"
            )
        path, record_id, date = add.current.paths[given], given, None
        stale = _stale(add, draft, path, given)
        if stale is not None:
            return stale
    record = record_from_draft(draft, record_id, date, None)
    if not isinstance(record, Decision):
        return record if isinstance(record, Problem) else _refuse(draft, "this is not a decision")
    if path is not None:
        existing = add.current.decisions[record.id]
        if record.imported_from != existing.imported_from and not add.importing:
            return _refuse(draft, _origin_changed(record.id))
    else:
        for change in record.changes:
            if change.action is Action.RETIRE:
                add.retired.add(change.entry)
    return _keep(add, draft, record, path or new_record_path(record))


def _entry(add: _Add, draft: Draft) -> Problem | None:
    given = draft.header.get("id")
    if given is None:
        return _refuse(draft, "a specification draft needs an id; lodge id s gives one")
    if not isinstance(given, str) or not _is_id(given, "s"):
        return _refuse(draft, _not_an_id(given, "s"))
    existing = add.current.entries.get(given)
    area = draft.header.get("area")
    if existing is not None:
        if area is not None and area != existing.area:
            return _refuse(
                draft, f"area {area} differs from {existing.area}; entries do not move areas"
            )
        path = add.current.paths[given]
        stale = _stale(add, draft, path, given)
        if stale is not None:
            return stale
        area = existing.area
    else:
        path = None
        if "base" in draft.header:
            return _refuse(draft, f"base is for edits, but no entry {given} exists to edit")
        if "imported_from" in draft.header and not add.importing:
            return _refuse(draft, _NEEDS_FLAG)
        if area is None:
            return _refuse(draft, "a new specification draft needs an area key")
        if not isinstance(area, str):
            return _refuse(draft, f"area must be one name, not {area!r}")
        if area not in add.current.areas and area not in add.drafted_areas:
            return _refuse(
                draft, f"area {area} does not exist; add an area draft for it in the same add"
            )
    record = record_from_draft(draft, given, None, str(area))
    if not isinstance(record, SpecEntry):
        return record if isinstance(record, Problem) else _refuse(draft, "this is not an entry")
    if (
        existing is not None
        and record.imported_from != existing.imported_from
        and not add.importing
    ):
        return _refuse(draft, _origin_changed(record.id))
    if existing is None:
        add.new_entries.append(record)
    return _keep(add, draft, record, path or new_record_path(record))


def _area(add: _Add, draft: Draft) -> Problem | None:
    record = record_from_draft(draft, "", None, None)
    if not isinstance(record, Area):
        return record if isinstance(record, Problem) else _refuse(draft, "this is not an area")
    path = area_path(record.name)
    if record.name not in add.current.areas:
        if "base" in draft.header:
            return _refuse(draft, f"base is for edits, but no area {record.name} exists to edit")
    else:
        stale = _stale(add, draft, path, f"area:{record.name}")
        if stale is not None:
            return stale
    if record.name in add.areas:
        return _refuse(draft, f"another draft of this add is for the area {record.name}")
    add.areas[record.name] = record
    return None


def _keep(add: _Add, draft: Draft, record: Record, path: str) -> Problem | None:
    if record.id in add.ids:
        return _refuse(draft, f"another draft of this add is for {record.id}")
    try:
        add.files[path] = write_record(record)
    except ValueError as error:
        return _refuse(draft, str(error))
    add.ids.append(record.id)
    return None


def _stale(add: _Add, draft: Draft, path: str, ref: str) -> Problem | None:
    base = draft.header.get("base")
    if base is None:
        return _refuse(
            draft, f"an edit draft needs a base key; print the draft with lodge draft {ref}"
        )
    text = add.tree.files.get(path)
    actual = "(the file is missing)" if text is None else content_hash(text)
    if base == actual:
        return None
    message = (
        f"the base {base} differs from {actual}, the hash of {path} now; "
        f"it changed since the draft was made, so print it again with lodge draft {ref}, "
        "make the change on that print, and add it"
    )
    return StaleBase(draft.source, 1, message)


def _area_files(add: _Add) -> list[Problem]:
    """Area files: those drafted, and those whose order gains new or restored entries or loses
    retired ones."""
    gained: dict[str, list[str]] = {}
    for entry in add.new_entries:
        gained.setdefault(entry.area, []).append(entry.id)
    for entry_id in _restored(add):
        gained.setdefault(add.current.entries[entry_id].area, []).append(entry_id)
    lost = {add.current.entries[i].area for i in add.retired if i in add.current.entries}
    problems: list[Problem] = []
    for name in sorted(add.areas.keys() | gained.keys() | lost):
        start = add.areas.get(name) or add.current.areas.get(name)
        if start is None:
            continue
        order = [i for i in start.order if i not in add.retired]
        order += [i for i in gained.get(name, []) if i not in order and i not in add.retired]
        area = replace(start, order=tuple(order))
        if name in add.areas or area != start:
            try:
                add.files[area_path(name)] = write_area(area)
            except ValueError as error:
                problems.append(Problem(area_path(name), 1, str(error)))
    return problems


def _restored(add: _Add) -> list[str]:
    """The entries that were retired before this add and are current once it is written."""
    was = derive(add.current).status
    if "retired" not in was.values():
        return []
    now = derive(load(Tree(add.tree.rev, {**add.tree.files, **add.files}))).status
    return sorted(i for i in add.current.entries if was[i] == "retired" and now.get(i) == "current")


def _refuse(draft: Draft, message: str) -> Problem:
    return Problem(draft.source, 1, message)


_NEEDS_FLAG = "imported_from is for imports; add with --import to bring in imported records"


def _is_id(text: str, prefix: str) -> bool:
    return is_id(text) and text.startswith(f"{prefix}-")


def _not_an_id(given: object, prefix: str) -> str:
    """Why `given` is not an ID of the kind `prefix` names, saying what would be."""
    kind, noun, example = (
        ("a decision", "a decision", "d-3m8qk2")
        if prefix == "d"
        else ("a specification entry", "an entry", "s-4kq1zm")
    )
    head = f"id {given!r} is not {kind} ID; "
    if isinstance(given, str) and given != given.lower() and _is_id(given.lower(), prefix):
        return head + f"IDs are lower case, like {example}"
    if isinstance(given, str) and is_id(given):
        return head + f"{noun} ID starts with {prefix}-, like {example}"
    return head + (
        f"an ID is {prefix}- and six characters from 0-9 and a-z without i, l, o, and u, "
        f"like {example}"
    )


def _origin_changed(record_id: str) -> str:
    return f"this draft changes imported_from of {record_id}; keep it as lodge draft printed it"
