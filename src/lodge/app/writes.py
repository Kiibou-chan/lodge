"""The write operations: minting IDs and adding drafts."""

from collections.abc import Collection, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from lodge import core
from lodge.app.errors import Conflict, LodgeError
from lodge.app.ports import Clock, IdSource, PublishOutcome
from lodge.app.results import Added, AddOutcome
from lodge.app.state import State, Wiring, read_state
from lodge.core import (
    Decision,
    Draft,
    Problem,
    Record,
    Snapshot,
    StaleBase,
    Tree,
    apply_drafts,
    attachment_path,
    load,
    mint_id,
    parse_draft,
)

_MINT_DRAWS = 10
_ATTEMPTS = 3
_WAITS = 3


@dataclass(frozen=True)
class _Request:
    drafts: list[Draft]
    importing: bool
    dry_run: bool
    attached: Mapping[str, str]


def mint(w: Wiring, prefix: Literal["d", "s"]) -> str:
    s = read_state(w.store).snapshot
    return _mint(w.ids, prefix, {*s.decisions, *s.entries})


def add(
    w: Wiring,
    drafts: Sequence[tuple[str, str]],
    importing: bool,
    dry_run: bool,
    attachments: Sequence[tuple[str, str]] = (),
) -> Added:
    """Apply `drafts` to the store; a rejected publish starts again from reading the store.

    `attachments` are (name, text) files that go beside the one new decision the add creates.
    """
    parsed = _parse(drafts)
    request = _Request(parsed, importing, dry_run, _attached(attachments, parsed))
    first: Snapshot | None = None
    for _ in range(_ATTEMPTS):
        state = read_state(w.store)
        first = first or state.snapshot
        added = _attempt(w, state, first, request)
        if added is not None:
            return added
    raise Conflict(
        "other changes reached the store three times while this one was being published; "
        "nothing was written, so add the drafts again"
    )


def _attempt(w: Wiring, state: State, first: Snapshot, request: _Request) -> Added | None:
    """One pass over `state`; None when the store moved before the publish.

    `first` is the snapshot of the first attempt: a refusal over something that appeared
    since is a race, so a `Conflict`.
    """
    drafts, importing = request.drafts, request.importing
    s = state.snapshot
    now = _after_newest(w.clock, s)
    new_ids: list[str] = []
    for _ in range(sum(d.kind == "decision" and "id" not in d.header for d in drafts)):
        new_ids.append(_mint(w.ids, "d", {*s.decisions, *s.entries, *new_ids}))
    applied = apply_drafts(
        s, state.current, drafts, new_ids, now.isoformat(timespec="seconds"), importing
    )
    if isinstance(applied, list):
        raise _refusal(applied, raced=_raced(drafts, first, s))
    current = state.current
    files = {p: t for p, t in applied.files.items() if current.files.get(p) != t}
    placed = {attachment_path(new_ids[0], name): text for name, text in request.attached.items()}
    after_tree = Tree(current.rev, {**current.files, **files}, current.attachments | placed.keys())
    after = load(after_tree)
    if request.attached:
        _require_listed(after.decisions[new_ids[0]], request.attached)
    check = core.check_change(load(state.published), after, w.settings, now, s)
    notes = tuple(
        core.feedback(_written(s, after, applied.ids), after, core.derive(after), w.settings.length)
    )
    if not check.ok:
        return Added(
            applied.ids, notes, check, AddOutcome.CHECK_FAILED, state.read.freshness, tuple(new_ids)
        )
    if request.dry_run:
        return Added(applied.ids, notes, check, AddOutcome.DRY_RUN, minted=tuple(new_ids))
    if not files:
        return Added(applied.ids, notes, check, AddOutcome.UNCHANGED)
    outcome = w.store.publish(current, {**files, **placed}, _message(after, applied.ids))
    if outcome is PublishOutcome.REJECTED:
        return None
    published = AddOutcome.PUBLISHED if outcome is PublishOutcome.PUBLISHED else AddOutcome.STAGED
    return Added(applied.ids, notes, check, published)


def _attached(attachments: Sequence[tuple[str, str]], drafts: Sequence[Draft]) -> dict[str, str]:
    """The attachments by name; refused unless the drafts create one decision, names plain."""
    if not attachments:
        return {}
    created = sum(d.kind == "decision" and "id" not in d.header for d in drafts)
    if created != 1:
        raise LodgeError(f"--attach needs the add to create one decision, not {created}")
    named: dict[str, str] = {}
    for name, text in attachments:
        if name in {"", ".", "..", ".git"} or any(c in name for c in "/\\\0"):
            raise LodgeError(f"{name!r} is not a plain file name")
        if name in named:
            raise LodgeError(f"{name} is attached twice")
        named[name] = text
    return named


def _require_listed(decision: Decision, attached: Mapping[str, str]) -> None:
    listed, wanted = sorted(set(decision.attachments)), sorted(attached)
    if listed != wanted:
        raise LodgeError(
            f"the new decision lists [{', '.join(listed)}] in attachments, "
            f"but the attached files are [{', '.join(wanted)}]; list exactly the attached names"
        )


def _after_newest(clock: Clock, s: Snapshot) -> datetime:
    """The time, once its whole second is later than the newest decision's: dates are to the
    second, so no two decisions that share one are left to a tie.

    A newest decision more than `_WAITS` seconds ahead of the clock is not waited for, and one
    that stays ahead after the waits is left to check 1, which refuses a change related to it.
    """
    newest = max((datetime.fromisoformat(d.date) for d in s.decisions.values()), default=None)
    now = clock.now()
    if newest is not None and (newest - now).total_seconds() > _WAITS:
        return now
    for _ in range(_WAITS):
        if newest is None or now.replace(microsecond=0) > newest:
            break
        clock.sleep(1.0 - now.microsecond / 1_000_000)
        now = clock.now()
    return now


def _parse(drafts: Sequence[tuple[str, str]]) -> list[Draft]:
    if not drafts:
        raise LodgeError("no drafts to add")
    parsed = [parse_draft(source, text) for source, text in drafts]
    problems = [p for p in parsed if isinstance(p, Problem)]
    if problems:
        raise _refusal(problems)
    return [d for d in parsed if isinstance(d, Draft)]


def _refusal(problems: Sequence[Problem], raced: bool = False) -> LodgeError:
    """A `Conflict` when a base is stale or `raced`, otherwise a `LodgeError`; a line a problem."""
    lines = [f"{p.path}{f':{p.line}' if p.line else ''}: {p.message}" for p in problems]
    conflict = raced or any(isinstance(p, StaleBase) for p in problems)
    return (Conflict if conflict else LodgeError)("\n".join(lines))


def _raced(drafts: Sequence[Draft], first: Snapshot, now: Snapshot) -> bool:
    """Whether an area or entry that a draft names has appeared since `first`."""
    for draft in drafts:
        if draft.kind == "area":
            name = draft.header.get("name")
            if isinstance(name, str) and name in now.areas and name not in first.areas:
                return True
        elif draft.kind == "spec":
            given = draft.header.get("id")
            if isinstance(given, str) and given in now.entries and given not in first.entries:
                return True
    return False


def _mint(ids: IdSource, prefix: Literal["d", "s"], taken: Collection[str]) -> str:
    for _ in range(_MINT_DRAWS):
        candidate = mint_id(prefix, ids.entropy())
        if candidate not in taken:
            return candidate
    raise LodgeError("no unused ID was found in ten draws")


def _written(before: Snapshot, after: Snapshot, ids: Sequence[str]) -> list[Record]:
    """The new decisions and every written entry, in draft order; an edited decision is left out."""
    found: list[Record] = []
    for record_id in ids:
        if record_id in after.entries:
            found.append(after.entries[record_id])
        elif record_id in after.decisions and record_id not in before.decisions:
            found.append(after.decisions[record_id])
    return found


def _message(after: Snapshot, ids: Sequence[str]) -> str:
    records: dict[str, Record] = {**after.decisions, **after.entries}
    title = records[ids[0]].title if ids else ""
    return f"lodge: add {', '.join(ids) or 'areas'} {title}".rstrip()
