"""A published state and helpers for building the state after a change; the project is made up."""

from datetime import datetime, timedelta, timezone

from builders import area, at, decision, entry, snapshot_of

from lodge.core import (
    Action,
    Area,
    Change,
    CheckResult,
    CoreSettings,
    Decision,
    Imported,
    Snapshot,
    SpecEntry,
    check_change,
)

SPEC, OLD = "s-aaaaaa", "d-aaaaaa"
LATER = at(30)
SETTINGS = CoreSettings(import_sources=("notes.md",))
NOW = datetime(2026, 10, 29, 12, tzinfo=timezone(timedelta(hours=1)))
NOTES = Imported("notes.md", "A heading")

Item = Area | Decision | SpecEntry


def key(item: Item) -> str:
    return item.name if isinstance(item, Area) else item.id


def creates(spec: str, **kw: object) -> Decision:
    return decision(changes=(Change(spec, Action.CREATE),), **kw)


def base_items() -> list[Item]:
    old = creates(SPEC, id=OLD, date=at(0), decided_by="author")
    return [area(order=(SPEC,)), entry(id=SPEC), old]


def old_decision() -> Decision:
    old = base_items()[2]
    assert isinstance(old, Decision)
    return old


def state(*items: Item, drop: tuple[str, ...] = ()) -> Snapshot:
    """The published items, with those of `items` added or, by ID or area name, replacing them."""
    merged = {key(item): item for item in base_items()}
    merged |= {key(item): item for item in items}
    return snapshot_of(*(item for k, item in merged.items() if k not in drop))


def published() -> Snapshot:
    return state()


def check(before: Snapshot, after: Snapshot) -> CheckResult:
    return check_change(before, after, SETTINGS, NOW)


def verdict(before: Snapshot, after: Snapshot) -> list[tuple[int, str]]:
    return [(p.check, p.message) for p in check(before, after).problems]


REMEDY_CHECK_5 = "; a correction is a new decision that replaces it"
REMEDY_CHECK_5_REASONING = (
    "; a correction or a shorter reasoning is a new decision that replaces it"
)
REMEDY_CHECK_4 = "; list it in the decision's changes"
REMEDY_CHECK_3 = (
    "; add quote: {text, where, when} with the author's words, or record it under your own role"
)
REMEDY_ATTACH = "; pass the file with --attach"
