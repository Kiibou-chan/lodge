"""The read operations: each reads the store once and checks what it read."""

from collections.abc import Iterable
from dataclasses import replace
from datetime import datetime

from lodge import core
from lodge.app.errors import LodgeError
from lodge.app.ports import Clock, Store
from lodge.app.results import Listed, Read, Shown
from lodge.app.state import State, not_found, read_state, resolve_ref
from lodge.core import (
    CheckResult,
    CoreSettings,
    Filters,
    Level1,
    Problem,
    SpecArea,
    area_path,
    content_hash,
    level1,
    level2,
    level2_views,
    level3,
    load,
    render_spec,
    spec_view,
)

_AREA = "area:"


def search_records(store: Store, query: str, filters: Filters, limit: int) -> Listed:
    state = read_state(store)
    ids, total = core.search_counted(state.snapshot, state.derived, query, filters, limit)
    return Listed(_views(state, ids), state.read, total - len(ids))


def show(store: Store, ref: str, reasoning: bool, provenance: bool) -> Shown:
    state = read_state(store)
    record_id = resolve_ref(state, ref)
    s, d = state.snapshot, state.derived
    return Shown(
        level1(s, d, record_id, state.failing),
        level2(s, d, record_id, state.failing) if reasoning else None,
        level3(s, d, record_id) if provenance else None,
        state.read,
        level2_views(s, d, record_id, state.failing) if reasoning else (),
    )


def waiting(store: Store) -> Listed:
    state = read_state(store)
    return Listed(_newest_first(state, state.derived.awaiting_author), state.read)


def timeline(store: Store, limit: int) -> Listed:
    if limit < 0:
        raise LodgeError(f"the limit must not be negative, got {limit}")
    state = read_state(store)
    everything = _newest_first(state, state.snapshot.decisions)
    return Listed(everything[:limit], state.read, max(0, len(everything) - limit))


def spec(store: Store, area: str | None) -> tuple[str, Read, tuple[SpecArea, ...]]:
    state = read_state(store)
    s = state.snapshot
    if area is not None and area not in s.areas and all(e.area != area for e in s.entries.values()):
        raise not_found(state, f"area named {area}", area)
    text = render_spec(s, state.derived, state.failing, area)
    return text, state.read, spec_view(s, state.derived, state.failing, area)


def check(
    store: Store, clock: Clock, settings: CoreSettings, gate: bool
) -> tuple[CheckResult, Read]:
    """The one-state checks, or with `gate` the comparison with the published state."""
    state = read_state(store)
    if not gate:
        return state.result, state.read
    base = store.gate(state.current)
    published, now = load(base.published), clock.now()
    found: dict[Problem, list[str]] = {}
    notes: dict[str, None] = {}
    for label, tree in base.checked:
        snapshot = state.snapshot if tree is state.current else load(tree)
        result = core.check_change(published, snapshot, settings, now)
        for problem in result.problems:
            found.setdefault(problem, []).append(label)
        notes.update(dict.fromkeys(result.notes))
    notes.update(dict.fromkeys(base.notes))
    problems = [_labelled(p, labels) for p, labels in sorted(found.items(), key=_by_position)]
    return CheckResult(tuple(problems), tuple(notes)), state.read


def _by_position(item: tuple[Problem, list[str]]) -> tuple[str, int, str]:
    problem = item[0]
    return problem.path, problem.check, problem.message


def _labelled(problem: Problem, labels: list[str]) -> Problem:
    """`problem` with the states that have it named before its message."""
    named = " and ".join(label for label in labels if label)
    return replace(problem, message=f"{named}: {problem.message}") if named else problem


def draft(store: Store, ref: str) -> str:
    """The file of a record or area, with a `base` key and for an area a `name` key added."""
    state = read_state(store)
    s = state.snapshot
    if ref.startswith(_AREA):
        name = ref.removeprefix(_AREA)
        if name not in s.areas:
            raise not_found(state, f"area named {name}", name)
        path, extra = area_path(name), f"name: {name}\n"
    else:
        path, extra = s.paths[resolve_ref(state, ref)], ""
    text = state.current.files[path].replace("\r\n", "\n")
    return text.replace("---\n", f"---\n{extra}base: {content_hash(text)}\n", 1)


def _newest_first(state: State, decision_ids: Iterable[str]) -> tuple[Level1, ...]:
    decisions = state.snapshot.decisions
    ordered = sorted(
        decision_ids, key=lambda i: (datetime.fromisoformat(decisions[i].date), i), reverse=True
    )
    return _views(state, ordered)


def _views(state: State, ids: Iterable[str]) -> tuple[Level1, ...]:
    return tuple(level1(state.snapshot, state.derived, i, state.failing) for i in ids)
