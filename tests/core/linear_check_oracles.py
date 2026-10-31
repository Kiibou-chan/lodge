"""Pre-Task-2 checks and doubts, retained only as differential oracles."""

from collections.abc import Iterator, Mapping
from datetime import datetime

from lodge.core.check_state import new_decisions, problem_at
from lodge.core.derive import derive
from lodge.core.fileformat import area_path
from lodge.core.model import Action, Problem, Raises, ThreadState
from lodge.core.snapshot import Snapshot


def old_check_areas(s: Snapshot) -> Iterator[Problem]:
    status = derive(s).status
    folders = sorted({e.area for e in s.entries.values()} | s.areas.keys())
    for name in folders:
        entries = sorted(e.id for e in s.entries.values() if e.area == name)
        if name not in s.areas:
            message = f"area {name}: has entries but no _area.md"
            yield Problem(area_path(name), 7, message)
            continue
        current = {i for i in entries if status[i] == "current"}
        order = s.areas[name].order
        for entry_id in entries:
            if entry_id in current and entry_id not in order:
                message = f"{entry_id}: is not listed in the order of area {name}"
                yield Problem(s.paths[entry_id], 7, message)
        for entry_id in dict.fromkeys(order):
            if entry_id not in current:
                message = (
                    f"area {name}: order lists {entry_id}, which is not a current entry of the area"
                )
                yield Problem(area_path(name), 7, message)
            elif order.count(entry_id) > 1:
                message = f"area {name}: order lists {entry_id} more than once"
                yield Problem(area_path(name), 7, message)


def old_check_cycles(s: Snapshot) -> Iterator[Problem]:
    def reachable(start: str) -> set[str]:
        found: set[str] = set()
        pending = list(s.entries[start].rests_on)
        while pending:
            target = pending.pop()
            if target in found or target not in s.entries:
                continue
            found.add(target)
            pending.extend(s.entries[target].rests_on)
        return found

    reach = {i: reachable(i) for i in s.entries}
    for i in sorted(reach):
        if i in reach[i] and (others := sorted(t for t in reach[i] if t != i and i in reach[t])):
            yield Problem(
                s.paths.get(i, ""),
                8,
                f"{i}: is in a cycle of rests_on links with {', '.join(others)}",
            )


def old_dates(
    published: Snapshot, after: Snapshot, now: datetime, current: Snapshot | None
) -> Iterator[Problem]:
    """A new decision is dated no later than `now`; a non-imported one after each decision of
    `published` and `current` it links to or shares an entry with."""
    earlier = {**published.decisions, **(current.decisions if current else {})}
    for d in new_decisions(published, after):
        if current is not None and d.id in current.decisions:
            continue
        if datetime.fromisoformat(d.date) > now:
            message = f"dated {d.date}, which is after the time of this change"
            yield problem_at(after, d.id, 1, message)
        if d.imported_from is not None:
            continue
        reasons: dict[str, str] = {}
        entries = {c.entry for c in d.changes}
        for target in sorted(earlier):
            if target in d.replaces:
                reasons[target] = "which it replaces"
            elif target in d.narrows:
                reasons[target] = "which it narrows"
            elif target in d.confirms:
                reasons[target] = "which it confirms"
            elif shared := sorted(entries & {c.entry for c in earlier[target].changes}):
                reasons[target] = f"which shares {shared[0]} with it"
        for target, reason in reasons.items():
            if datetime.fromisoformat(d.date) <= datetime.fromisoformat(earlier[target].date):
                message = f"dated {d.date}, no later than {target}, {reason}"
                yield problem_at(after, d.id, 1, message)


def old_doubt_marks(
    s: Snapshot, changed_by: Mapping[str, tuple[str, ...]]
) -> dict[str, tuple[str, ...]]:
    doubts = _open(s, Raises.DOUBT)
    questions = _open(s, Raises.QUESTION)
    marks: dict[str, list[str]] = {}
    affected: set[str] = set()
    for ident in sorted(s.decisions.keys() | s.entries.keys()):
        local: list[str] = []
        if ident in doubts:
            local.append("in doubt")
        if ident in questions:
            local.append("question open")
        changed = False
        if ident in s.entries:
            for decision in sorted(doubts & s.decisions.keys()):
                created = any(
                    c.entry == ident and c.action is Action.CREATE
                    for c in s.decisions[decision].changes
                )
                if created or changed_by.get(ident, ())[:1] == (decision,):
                    changed = True
                    local.append(f"changed by {decision}, in doubt")
            if ident in doubts or changed:
                affected.add(ident)
        if local:
            marks[ident] = local
    _propagate(s, affected, marks)
    return {ident: tuple(values) for ident, values in marks.items()}


def _open(s: Snapshot, kind: Raises) -> set[str]:
    return {t.about for t in s.threads.values() if t.state is ThreadState.OPEN and t.raises is kind}


def _propagate(s: Snapshot, affected: set[str], marks: dict[str, list[str]]) -> None:
    for ident, entry in sorted(s.entries.items()):
        seen = {ident}
        pending = list(entry.rests_on)
        reached: set[str] = set()
        while pending:
            target = pending.pop()
            if target in seen:
                continue
            seen.add(target)
            if target in affected:
                reached.add(target)
            if target in s.entries:
                pending.extend(s.entries[target].rests_on)
        if reached:
            marks.setdefault(ident, []).extend(f"rests on {t}, in doubt" for t in sorted(reached))
