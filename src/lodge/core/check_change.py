"""The checks between the published state and the state about to be published."""

from collections.abc import Iterator
from datetime import datetime

from lodge.core.check_entries import check_entries
from lodge.core.check_immutable import check_immutable
from lodge.core.check_state import (
    CheckResult,
    check_state,
    new_decisions,
    problem_at,
    sort_key,
)
from lodge.core.derive import derive
from lodge.core.model import Action, Problem
from lodge.core.settings import CoreSettings
from lodge.core.snapshot import Snapshot


def check_change(
    published: Snapshot,
    after: Snapshot,
    settings: CoreSettings,
    now: datetime,
    current: Snapshot | None = None,
) -> CheckResult:
    """Every problem of 4, 5, and 6, and those of 1, 2, 3, and 7 that `after` alone has.

    A problem of `after` that `published` has too, by path, check, and message, is a note.
    `current` is the state this change starts from when it is not the published one: a decision
    it adds is dated after the decisions of `current` as well, and one that `current` holds is
    not checked again.
    """
    known = {sort_key(p) for p in check_state(published).problems}
    problems: list[Problem] = []
    notes: list[str] = []
    for found in check_state(after).problems:
        if sort_key(found) in known:
            notes.append(f"already published, check {found.check}: {found.path}: {found.message}")
        else:
            problems.append(found)
    immutable, shrunk = check_immutable(published, after)
    problems += [
        *_missing(published, after),
        *_dates(published, after, now, current),
        *_imports_over_live(published, after),
        *check_entries(published, after, settings),
        *immutable,
        *_links_to_dead(published, after),
    ]
    notes += [*shrunk, *_area_notes(published, after)]
    return CheckResult(tuple(sorted(problems, key=sort_key)), tuple(notes))


def _missing(published: Snapshot, after: Snapshot) -> Iterator[Problem]:
    for record_id in sorted({*published.decisions, *published.entries}):
        if record_id not in after.decisions and record_id not in after.entries:
            message = "was published and is missing from this state"
            yield problem_at(published, record_id, 2, message)


def _dates(
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


def _imports_over_live(published: Snapshot, after: Snapshot) -> Iterator[Problem]:
    live = {
        c.entry for d in published.decisions.values() if d.imported_from is None for c in d.changes
    }
    for d in new_decisions(published, after):
        if d.imported_from is not None:
            for entry in dict.fromkeys(c.entry for c in d.changes if c.entry in live):
                message = f"imported, changes {entry}, which a live decision already changed"
                yield problem_at(after, d.id, 1, message)


def _links_to_dead(published: Snapshot, after: Snapshot) -> Iterator[Problem]:
    """Check 6: a new decision narrows or confirms a replaced decision, or edits a retired entry.

    An entry counts as retired when it is retired both before and after the change, so a decision
    that replaces the last standing retirement may edit the entry.
    """
    status = derive(published).status
    standing = derive(after).status
    for d in new_decisions(published, after):
        for verb, targets in (("narrows", d.narrows), ("confirms", d.confirms)):
            for target in dict.fromkeys(targets):
                if status.get(target) == "replaced":
                    yield problem_at(after, d.id, 6, f"{verb} {target}, which is replaced")
        for change in dict.fromkeys(d.changes):
            retired = status.get(change.entry) == "retired" == standing.get(change.entry)
            if change.action is not Action.RETIRE and retired:
                message = (
                    f"changes {change.entry} with action {change.action}, but the entry is retired"
                )
                yield problem_at(after, d.id, 6, message)


def _area_notes(published: Snapshot, after: Snapshot) -> Iterator[str]:
    for name in sorted(after.areas.keys() - published.areas.keys()):
        yield f"area {name}: added"
    for name in sorted(published.areas.keys() - after.areas.keys()):
        yield f"area {name}: removed"
    for name in sorted(published.areas.keys() & after.areas.keys()):
        before, now = published.areas[name], after.areas[name]
        for field in ("title", "intro", "order"):
            if getattr(before, field) != getattr(now, field):
                yield f"area {name}: {field} changed"
