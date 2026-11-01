"""Build stored read values and snapshot facts from a checked state."""

from collections.abc import Mapping
from dataclasses import replace
from datetime import UTC, datetime
from itertools import chain

from lodge import core
from lodge.app import threads
from lodge.app.index_types import Row, StateFacts, StoredState
from lodge.app.results import Listed, Read, ThreadShown
from lodge.app.state import State


def build_rows(state: State) -> dict[str, Row]:
    s, d = state.snapshot, state.derived
    rows: dict[str, Row] = {}
    for record in chain[core.Decision | core.SpecEntry](s.decisions.values(), s.entries.values()):
        ident = record.id
        view = core.level1(s, d, ident, state.failing)
        path = s.paths[ident]
        areas = (
            {record.area}
            if isinstance(record, core.SpecEntry)
            else {s.entries[c.entry].area for c in record.changes if c.entry in s.entries}
        )
        rows[ident] = Row(
            (path, state.current.blobs[path]),
            view.status,
            view.decided_by,
            view.date,
            view.scope,
            view.area,
            view.flags,
            view.quote,
            core.level3(s, d, ident).links,
            d.changed_by.get(ident, ()),
            frozenset(areas),
        )
    return rows


def build_answers(state: State) -> dict[str, object]:
    s, d = state.snapshot, state.derived
    read = Read(None, state.read.unrecorded)
    waiting = sorted(
        d.awaiting_author,
        key=lambda i: (datetime.fromisoformat(s.decisions[i].date), i),
        reverse=True,
    )
    listed = Listed(tuple(core.level1(s, d, i, state.failing) for i in waiting), read)
    answers: dict[str, object] = {
        "waiting": (listed, replace(threads.waiting_in(state), read=read)),
        "threads": replace(threads.open_in(state), read=read),
    }
    for thread in s.threads.values():
        about = (
            core.level1(s, d, thread.about, state.failing)
            if thread.about in s.decisions or thread.about in s.entries
            else None
        )
        answers[f"thread:{thread.id}"] = ThreadShown(thread, about, read)
    return answers


def build_citers(state: State, codes: Mapping[str, tuple[str, ...]]) -> dict[str, tuple[str, ...]]:
    s, d = state.snapshot, state.derived
    roots = {code[:n] for code in codes for n, char in enumerate(code) if char == "."}
    citing: dict[str, list[str]] = {code: [] for code in (*codes, *roots)}
    dates: dict[str, datetime] = {}
    for record in chain[core.Decision | core.SpecEntry](s.decisions.values(), s.entries.values()):
        own = record.code.lower() if record.code else ""
        for token in core.code_tokens(record.title) | core.code_tokens(record.statement):
            if token in citing and own != token and not own.startswith(token + "."):
                citing[token].append(record.id)
        who = (
            record
            if isinstance(record, core.Decision)
            else s.decisions.get(next(iter(d.changed_by.get(record.id, ())), ""))
        )
        dates[record.id] = (
            datetime.fromisoformat(who.date) if who else datetime.min.replace(tzinfo=UTC)
        )
    return {
        code: tuple(sorted(ids, key=lambda i: (dates[i], i), reverse=True))
        for code, ids in citing.items()
    }


def change_facts_of(state: State, before: StateFacts) -> core.ChangeFacts | None:
    allowed: dict[str, core.Status] = {
        "current": "current",
        "replaced": "replaced",
        "retired": "retired",
    }
    if any(status not in allowed for status in before.status.values()):
        return None
    return core.ChangeFacts(
        {ident: allowed[status] for ident, status in before.status.items()},
        frozenset((p.path, p.check, p.message) for p in before.problems),
        state.derived,
        state.standing.problems,
    )


def build_facts(state: State, current: str, published: str) -> dict[str, StateFacts]:
    facts = {current: StateFacts(state.derived.status, state.standing.problems)}
    if state.published_state is not None:
        before = state.published_state
        if before.facts is not None:
            facts[published] = before.facts
        else:
            assert before.derived is not None
            facts[published] = StateFacts(before.derived.status, before.result.problems)
    return facts


def build_state(
    state: State,
    key: str,
    current: str,
    published: str,
    now: datetime,
    rows: Mapping[str, Row],
    answers: Mapping[str, object],
    citing: Mapping[str, tuple[str, ...]],
) -> StoredState:
    codes: dict[str, list[str]] = {}
    for record in chain[core.Decision | core.SpecEntry](
        state.snapshot.decisions.values(), state.snapshot.entries.values()
    ):
        if record.code:
            codes.setdefault(record.code.lower(), []).append(record.id)
    before = state.published_state.snapshot.decisions if state.published_state else {}
    dates = [
        datetime.fromisoformat(d.date)
        for i, d in state.snapshot.decisions.items()
        if i not in before
    ]
    past, future = [d for d in dates if d <= now], [d for d in dates if d > now]
    return StoredState(
        key,
        current,
        published,
        (1024, len(answers), len(citing)),
        max(past).isoformat() if past else None,
        min(future).isoformat() if future else None,
        {code: tuple(sorted(ids)) for code, ids in codes.items()},
        {code: len(ids) for code, ids in citing.items()},
        state.read.unrecorded,
        tuple(sorted(state.snapshot.threads)),
    )
