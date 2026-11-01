"""The checks between the published state and the state about to be published."""

from collections.abc import Iterator, Mapping
from dataclasses import dataclass
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
from lodge.core.derive import Derived, Status, derive
from lodge.core.model import Action, Problem
from lodge.core.settings import CoreSettings
from lodge.core.snapshot import Snapshot


@dataclass(frozen=True)
class ChangeFacts:
    """What check_change would otherwise compute from the two snapshots."""

    published_status: Mapping[str, Status]
    published_problems: frozenset[tuple[str, int, str]]
    after_derived: Derived
    after_problems: tuple[Problem, ...]


def change_facts(
    published: Snapshot,
    after: Snapshot,
    *,
    before: Derived | None = None,
    before_problems: tuple[Problem, ...] | None = None,
    after_derived: Derived | None = None,
    after_problems: tuple[Problem, ...] | None = None,
) -> ChangeFacts:
    before = derive(published) if before is None else before
    standing = derive(after) if after_derived is None else after_derived
    if before_problems is None:
        before_problems = check_state(published, derived=before).problems
    if after_problems is None:
        after_problems = check_state(after, derived=standing).problems
    return ChangeFacts(
        before.status, frozenset(sort_key(p) for p in before_problems), standing, after_problems
    )


def check_change(
    published: Snapshot,
    after: Snapshot,
    settings: CoreSettings,
    now: datetime,
    current: Snapshot | None = None,
    *,
    facts: ChangeFacts | None = None,
) -> CheckResult:
    """Every problem of 4, 5, and 6, and those of 1, 2, 3, 7, and 8 that `after` alone has.

    A state compared with itself finds nothing: with `published` equal to `after`,
    no check adds a problem; reads rely on this rule (d-zyqzkg).
    A problem of `after` that `published` has too, by path, check, and message, is a note.
    `current` is the state this change starts from when it is not the published one: a decision
    it adds is dated after the decisions of `current` as well, and one that `current` holds is
    not checked again.
    """
    facts = change_facts(published, after) if facts is None else facts
    known = facts.published_problems
    problems: list[Problem] = []
    notes: list[str] = []
    for found in facts.after_problems:
        if sort_key(found) in known:
            notes.append(f"already published, check {found.check}: {found.path}: {found.message}")
        else:
            problems.append(found)
    problems += [
        *_missing(published, after),
        *_dates(published, after, now, current),
        *_imports_over_live(published, after),
        *check_entries(
            published, after, settings, facts.published_status, facts.after_derived.status
        ),
        *check_immutable(published, after),
        *_links_to_dead(published, after, facts.published_status, facts.after_derived.status),
    ]
    notes += _area_notes(published, after)
    return CheckResult(tuple(sorted(problems, key=sort_key)), tuple(notes))


def _missing(published: Snapshot, after: Snapshot) -> Iterator[Problem]:
    present = after.decisions.keys() | after.entries.keys() | after.threads.keys()
    for record_id in sorted({*published.decisions, *published.entries, *published.threads}):
        if record_id not in present:
            message = "was published and is missing from this state"
            yield problem_at(published, record_id, 2, message)


def _dates(
    published: Snapshot, after: Snapshot, now: datetime, current: Snapshot | None
) -> Iterator[Problem]:
    """A new decision is dated no later than `now`; a non-imported one after each decision of
    `published` and `current` it links to or shares an entry with."""
    earlier = {**published.decisions, **(current.decisions if current else {})}
    by_entry: dict[str, set[str]] = {}
    for target, decision in earlier.items():
        for change in decision.changes:
            by_entry.setdefault(change.entry, set()).add(target)
    for d in new_decisions(published, after):
        if current is not None and d.id in current.decisions:
            continue
        if datetime.fromisoformat(d.date) > now:
            message = f"dated {d.date}, which is after the time of this change"
            yield problem_at(after, d.id, 1, message)
        if d.imported_from is not None:
            continue
        shared: dict[str, str] = {}
        for entry in sorted({c.entry for c in d.changes}):
            for target in by_entry.get(entry, ()):
                shared.setdefault(target, entry)
        replaces, narrows, confirms = set(d.replaces), set(d.narrows), set(d.confirms)
        targets = (replaces | narrows | confirms) & earlier.keys() | shared.keys()
        for target in sorted(targets):
            if target in replaces:
                reason = "which it replaces"
            elif target in narrows:
                reason = "which it narrows"
            elif target in confirms:
                reason = "which it confirms"
            else:
                reason = f"which shares {shared[target]} with it"
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


def _links_to_dead(
    published: Snapshot,
    after: Snapshot,
    status: Mapping[str, Status],
    standing: Mapping[str, Status],
) -> Iterator[Problem]:
    """Check 6: a new decision narrows or confirms a replaced decision, or edits a retired entry,
    or an entry newly rests on a retired entry.

    An entry counts as retired when it is retired both before and after the change, so a decision
    that replaces the last standing retirement may edit the entry.
    """
    for e in sorted(after.entries.values(), key=lambda e: e.id):
        before = published.entries.get(e.id)
        previous = before.rests_on if before else ()
        for target in dict.fromkeys(e.rests_on):
            if target not in previous and standing.get(target) == "retired":
                yield problem_at(after, e.id, 6, f"rests on {target}, which is retired")
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
        for field in ("title", "intro", "order", "rank"):
            if getattr(before, field) != getattr(now, field):
                yield f"area {name}: {field} changed"
