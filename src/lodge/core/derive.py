"""Facts derived from a snapshot: statuses, reverse links, and the review flag."""

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from lodge.core.model import Action, Decision
from lodge.core.snapshot import Snapshot

Status = Literal["current", "replaced", "retired"]
Links = Mapping[str, tuple[str, ...]]


@dataclass(frozen=True)
class Derived:
    """Each list of decisions is newest first, ties by ID.

    The maps hold known records only: a decision or entry that no loaded file defines is neither
    a key nor a listed target, so a dangling `replaces` or `changes` entry leaves no trace.
    `revived` maps a decision to the entries it brings back by replacing their last standing
    retirement; such a decision counts as changing the entry.
    """

    status: Mapping[str, Status]
    replaced_by: Links
    narrowed_by: Links
    changed_by: Links
    confirmed_by: Links
    awaiting_author: frozenset[str]
    touched_by_flagged: Links
    revived: Links
    linked_by: Links
    supports: Links


def is_author(d: Decision) -> bool:
    return d.decided_by == "author"


def derive(s: Snapshot) -> Derived:
    oldest_first = sorted(s.decisions.values(), key=_order)
    newest_first = oldest_first[::-1]
    replaced_by = _reverse(newest_first, lambda d: d.replaces, s.decisions)
    narrowed_by = _reverse(newest_first, lambda d: d.narrows, s.decisions)
    revived = _revived(oldest_first, replaced_by)
    touches = {d.id: _entries_changed(d, revived) for d in oldest_first}
    changed_by = _reverse(newest_first, lambda d: touches[d.id], s.entries)
    confirmed_by = _reverse(newest_first, lambda d: d.confirms if is_author(d) else (), s.decisions)
    retired = {
        c.entry
        for d in oldest_first
        if d.id not in replaced_by
        for c in d.changes
        if c.action is Action.RETIRE
    }
    status: dict[str, Status] = {
        i: "replaced" if i in replaced_by else "current" for i in s.decisions
    }
    status |= {i: "retired" if i in retired else "current" for i in s.entries}
    changes: dict[str, list[Decision]] = {}
    for d in oldest_first:
        for entry in touches[d.id]:
            changes.setdefault(entry, []).append(d)
    hers = _confirmed_by_her(oldest_first)
    flagged = _flagged(s, oldest_first, touches, changes, hers)
    touched: dict[str, list[str]] = {}
    for d in newest_first:
        if d.id in flagged:
            behind = _behind_entry_edits(
                d, touches[d.id], changes, _counts_for(d, hers), replaced_by
            )
            targets = {*d.replaces, *d.narrows, *touches[d.id], *behind}
            for target in sorted(targets & (s.decisions.keys() | s.entries.keys())):
                touched.setdefault(target, []).append(d.id)
    linked = _reverse(
        newest_first, lambda d: (c.entry for c in d.changes if c.action is Action.LINK), s.entries
    )
    supports: dict[str, list[str]] = {}
    for i, e in sorted(s.entries.items()):
        for target in dict.fromkeys(e.rests_on):
            if target in s.entries:
                supports.setdefault(target, []).append(i)
    return Derived(
        status,
        replaced_by,
        narrowed_by,
        changed_by,
        confirmed_by,
        frozenset(flagged),
        {target: tuple(ids) for target, ids in touched.items()},
        {i: known for i, entries in revived.items() if (known := _known(entries, s.entries))},
        linked,
        {t: tuple(ids) for t, ids in supports.items()},
    )


def _order(d: Decision) -> tuple[datetime, str]:
    return datetime.fromisoformat(d.date), d.id


def _entries_changed(d: Decision, revived: Mapping[str, Iterable[str]]) -> tuple[str, ...]:
    """The entries `d` lists in `changes`, and those it revives."""
    entries = (c.entry for c in d.changes if c.action is not Action.LINK)
    return tuple(dict.fromkeys((*entries, *revived.get(d.id, ()))))


def _revived(oldest_first: list[Decision], replaced_by: Links) -> dict[str, list[str]]:
    """For each decision, the entries whose last standing retirement it replaces."""
    retirements: dict[str, list[str]] = {}
    for d in oldest_first:
        for entry in dict.fromkeys(c.entry for c in d.changes if c.action is Action.RETIRE):
            retirements.setdefault(entry, []).append(d.id)
    order = {d.id: _order(d) for d in oldest_first}

    def first(retirement: str) -> tuple[datetime, str] | None:
        return min((order[r] for r in replaced_by.get(retirement, ())), default=None)

    found: dict[str, list[str]] = {}
    for entry, ids in retirements.items():
        for retirement in ids:
            at = first(retirement)
            if at is None or at[1] in ids:
                continue
            others = (first(u) for u in ids if u != retirement and order[u] < at)
            if all(f is not None and f <= at for f in others) and entry not in found.get(at[1], ()):
                found.setdefault(at[1], []).append(entry)
    return found


def _known(entries: Iterable[str], known: Mapping[str, object]) -> tuple[str, ...]:
    return tuple(e for e in entries if e in known)


def _reverse(
    newest_first: Iterable[Decision],
    targets_of: Callable[[Decision], Iterable[str]],
    known: Mapping[str, object],
) -> Links:
    """For each known target, the IDs of the decisions naming it."""
    found: dict[str, list[str]] = {}
    for d in newest_first:
        for target in targets_of(d):
            if target in known:
                found.setdefault(target, []).append(d.id)
    return {target: tuple(ids) for target, ids in found.items()}


def _behind_entry_edits(
    d: Decision,
    entries: Iterable[str],
    changes: Mapping[str, list[Decision]],
    counts: Callable[[Decision], bool],
    replaced_by: Links,
) -> list[str]:
    """The decisions behind the previous standing change of each entry `d` changes, when hers."""
    behind: list[str] = []
    for entry in entries:
        standing = [c for c in changes[entry][: changes[entry].index(d)] if c.id not in replaced_by]
        if standing and counts(standing[-1]):
            behind.append(standing[-1].id)
    return behind


def _flagged(
    s: Snapshot,
    oldest_first: list[Decision],
    touches: Mapping[str, tuple[str, ...]],
    changes: Mapping[str, list[Decision]],
    hers: set[str],
) -> set[str]:
    """The agent decisions and the imported decisions awaiting the author; see "Review flag"."""
    cleared = _cleared(s, oldest_first)
    undone = {
        t
        for later in oldest_first
        if is_author(later) and later.imported_from is None
        for t in later.replaces
        if t in s.decisions and not is_author(s.decisions[t]) and t not in hers
    }
    flagged: set[str] = set()
    for d in oldest_first:
        if d.id in cleared or (is_author(d) and d.imported_from is None):
            continue
        counts = _counts_for(d, hers)
        touches_author_decision = any(
            t in s.decisions and counts(s.decisions[t]) for t in (*d.replaces, *d.narrows)
        )
        follows_author_change = any(
            _follows_author_change(d, counts, changes[entry], undone) for entry in touches[d.id]
        )
        if touches_author_decision or follows_author_change:
            flagged.add(d.id)
    return flagged


def _cleared(s: Snapshot, oldest_first: list[Decision]) -> set[str]:
    """Decisions that a later, non-imported author decision confirms or replaces."""
    cleared: set[str] = set()
    for later in oldest_first:
        if is_author(later) and later.imported_from is None:
            for target in (*later.confirms, *later.replaces):
                if target in s.decisions and _order(s.decisions[target]) < _order(later):
                    cleared.add(target)
    return cleared


def _confirmed_by_her(oldest_first: list[Decision]) -> set[str]:
    """Decisions that a non-imported author decision confirms, whatever their order."""
    return {
        target
        for later in oldest_first
        if is_author(later) and later.imported_from is None
        for target in later.confirms
    }


def _counts_for(d: Decision, hers: set[str]) -> Callable[[Decision], bool]:
    """Which decisions raise a flag on `d`: author decisions and those she confirmed.

    An imported `d` is flagged only by non-imported ones.
    """

    def counts(other: Decision) -> bool:
        mine = is_author(other) or other.id in hers
        return mine and (d.imported_from is None or other.imported_from is None)

    return counts


def _follows_author_change(
    d: Decision, counts: Callable[[Decision], bool], changed_entry: list[Decision], undone: set[str]
) -> bool:
    """Whether the latest change to an entry before `d`'s, by date, is one that raises a flag.

    A change is skipped when a non-imported author decision replaces its decision and it is not
    hers.
    """
    before = [c for c in changed_entry[: changed_entry.index(d)] if c.id not in undone]
    return bool(before) and counts(before[-1])
