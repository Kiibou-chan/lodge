"""The three reading levels of a record, and which records fail the check."""

from dataclasses import dataclass

from lodge.core.check_state import CheckResult
from lodge.core.derive import Derived, is_author
from lodge.core.model import (
    Action,
    Decision,
    Imported,
    NumberHandle,
    Problem,
    Quote,
    SpecEntry,
)
from lodge.core.snapshot import Snapshot


@dataclass(frozen=True)
class Level1:
    """What every read returns: the record's statement, its status, who decided, and the flags."""

    id: str
    kind: str
    code: str | None
    title: str
    statement: str
    status: str
    decided_by: str | None
    date: str | None
    scope: str | None
    area: str | None
    flags: tuple[str, ...]
    quote: Quote | None


@dataclass(frozen=True)
class Level3:
    """Provenance; `links` are (relation, target ID, target status) in both directions."""

    quote: Quote | None
    numbers: tuple[NumberHandle, ...]
    work_item: str | None
    attachments: tuple[str, ...]
    imported_from: Imported | None
    links: tuple[tuple[str, str, str], ...]


def failing_ids(s: Snapshot, result: CheckResult) -> frozenset[str]:
    """The IDs of the records whose files have a problem."""
    by_path = {path: record_id for record_id, path in s.paths.items()}
    return frozenset(by_path[p.path] for p in result.problems if p.path in by_path)


def unrecorded_problems(s: Snapshot, result: CheckResult) -> tuple[Problem, ...]:
    """The problems whose path holds no loaded record, such as an unreadable file."""
    held = set(s.paths.values())
    return tuple(p for p in result.problems if p.path not in held)


def level1(s: Snapshot, d: Derived, record_id: str, failing: frozenset[str]) -> Level1:
    if record_id in s.decisions:
        dec = s.decisions[record_id]
        who: Decision | None = dec
        kind, area, scope = "decision", None, str(dec.scope)
        record: Decision | SpecEntry = dec
    else:
        spec = s.entries[record_id]
        newest = d.changed_by.get(record_id, ())
        who = s.decisions[newest[0]] if newest else None
        kind, area, scope = "spec", spec.area, None
        record = spec
    quote = who.quote if who and is_author(who) else None
    return Level1(
        record_id,
        kind,
        record.code,
        record.title,
        record.statement,
        d.status[record_id],
        who.decided_by if who else None,
        who.date if who else None,
        scope,
        area,
        _flags(s, d, record, who, failing),
        quote,
    )


def level2(s: Snapshot, d: Derived, record_id: str, failing: frozenset[str]) -> str:
    """A decision's reasoning; an entry's, the heads of the decisions that changed it."""
    if record_id in s.decisions:
        return s.decisions[record_id].reasoning
    return "\n\n".join(_head(v) for v in level2_views(s, d, record_id, failing))


def level2_views(
    s: Snapshot, d: Derived, record_id: str, failing: frozenset[str]
) -> tuple[Level1, ...]:
    """The level 1 views of the decisions that changed an entry, newest first."""
    if record_id in s.decisions:
        return ()
    return tuple(level1(s, d, i, failing) for i in d.changed_by.get(record_id, ()))


def level3(s: Snapshot, d: Derived, record_id: str) -> Level3:
    links: list[tuple[str, str, str]] = []

    def add(relation: str, targets: tuple[str, ...]) -> None:
        links.extend((relation, t, d.status.get(t, "unknown")) for t in targets)

    if record_id in s.decisions:
        dec = s.decisions[record_id]
        for change in dict.fromkeys(dec.changes):
            add(f"changes ({change.action})", (change.entry,))
        add("replaces", dec.replaces)
        add("narrows", dec.narrows)
        add("confirms", dec.confirms)
        add("replaced by", d.replaced_by.get(record_id, ()))
        add("narrowed by", d.narrowed_by.get(record_id, ()))
        add("confirmed by", d.confirmed_by.get(record_id, ()))
        return Level3(
            dec.quote,
            dec.numbers,
            dec.work_item,
            dec.attachments,
            dec.imported_from,
            tuple(links),
        )
    add("changed by", d.changed_by.get(record_id, ()))
    return Level3(None, (), None, (), s.entries[record_id].imported_from, tuple(links))


def format_level1(v: Level1) -> str:
    text = f"{_head(v)}\n\n{v.statement}"
    if v.quote:
        text += f'\n\nquote: "{v.quote.text}" ({v.quote.where}, {v.quote.when})'
    return text


def format_level3(v: Level3) -> str:
    lines: list[str] = []
    if v.quote:
        lines.append(f'quote: "{v.quote.text}" ({v.quote.where}, {v.quote.when})')
    if v.numbers:
        lines.append("numbers: " + "; ".join(f"{n.value} ({n.handle})" for n in v.numbers))
    if v.work_item:
        lines.append(f"work item: {v.work_item}")
    if v.attachments:
        lines.append("attachments: " + ", ".join(v.attachments))
    if v.imported_from:
        lines.append(f"imported from: {v.imported_from.file}, {v.imported_from.heading}")
    lines.extend(f"{relation}: {target} ({status})" for relation, target, status in v.links)
    return "\n".join(lines)


def head_parts(
    v: Level1,
) -> tuple[str, str | None, str, str | None, str | None, str | None]:
    """The header's parts: ID, code, status, who decided, the day, and the scope or area."""
    day = v.date.split("T")[0] if v.date else None
    who = v.decided_by or ("no decision" if v.kind == "spec" else None)
    return (v.id, v.code, v.status, who, day, v.scope or v.area)


def _head(v: Level1) -> str:
    """The header line and the title."""
    ident, code, status, who, day, place = head_parts(v)
    parts = [f"{ident} {code}" if code else ident, status, who, day, place, *v.flags]
    return " · ".join(p for p in parts if p) + "\n" + v.title


def _flags(
    s: Snapshot,
    d: Derived,
    record: Decision | SpecEntry,
    who: Decision | None,
    failing: frozenset[str],
) -> tuple[str, ...]:
    i = record.id
    flags: list[str] = []
    if replaced := d.replaced_by.get(i):
        flags.append("replaced by " + ", ".join(replaced))
    if narrowed := d.narrowed_by.get(i):
        flags.append("narrowed by " + ", ".join(narrowed))
    if d.status[i] == "retired" and (retiring := _retiring(s, d, i)):
        flags.append("retired by " + retiring)
    if isinstance(record, SpecEntry) and who:
        if replaced := d.replaced_by.get(who.id):
            flags.append("its decision replaced by " + ", ".join(replaced))
        if narrowed := d.narrowed_by.get(who.id):
            flags.append("its decision narrowed by " + ", ".join(narrowed))
    if i in d.awaiting_author:
        flags.append("awaiting the author")
    elif waiting := d.touched_by_flagged.get(i):
        flags.append("awaiting the author on " + ", ".join(waiting))
    if record.imported_from is not None:
        flags.append("imported")
        if isinstance(record, Decision) and record.decided_by == "author" and record.quote is None:
            flags.append("unquoted")
    if i in failing:
        flags.append("fails check")
    if isinstance(record, SpecEntry) and who and who.id in failing:
        flags.append("decision fails check")
    return tuple(flags)


def _retiring(s: Snapshot, d: Derived, entry_id: str) -> str | None:
    """The newest standing decision that retires the entry."""
    return next(
        (
            i
            for i in d.changed_by.get(entry_id, ())
            if i not in d.replaced_by
            and any(
                c.entry == entry_id and c.action is Action.RETIRE for c in s.decisions[i].changes
            )
        ),
        None,
    )
