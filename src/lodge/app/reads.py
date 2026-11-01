"""The read operations: each reads the store once and checks what it read."""

from collections.abc import Iterable, Sequence
from dataclasses import replace
from datetime import datetime

from lodge import core
from lodge.app import threads
from lodge.app.errors import LodgeError
from lodge.app.results import Listed, Read, Shown, ShownMany, ThreadsWaiting
from lodge.app.state import Checked, State, Wiring, not_found, read_checked, read_state, resolve_ref
from lodge.core import (
    CheckResult,
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
    newest_last,
    render_spec,
    spec_view,
)

_AREA = "area:"


def search_records(w: Wiring, query: str, filters: Filters, limit: int) -> Listed:
    return search_many(w, [core.parse_query(query)], filters, limit)[0]


def search_many(
    w: Wiring, queries: Sequence[core.Query], filters: Filters, limit: int
) -> tuple[Listed, ...]:
    state = read_checked(w)
    seen: set[str] = set()
    results: list[Listed] = []
    count = len(state.snapshot.decisions) + len(state.snapshot.entries)
    for query in queries or [core.parse_query("")]:
        ids, _ = core.search_counted(state.snapshot, state.derived, query, filters, count)
        above = tuple(i for i in ids if i in seen)
        fresh = [i for i in ids if i not in seen]
        shown = fresh[:limit]
        results.append(
            Listed(_views(state, shown), state.read, len(fresh) - len(shown), query.text, above)
        )
        seen.update(shown)
    return tuple(results)


def show(w: Wiring, ref: str, reasoning: bool, provenance: bool, *, context: bool = True) -> Shown:
    """Read a record with code context unless the caller explicitly declines it."""
    state = read_checked(w)
    return _shown(state, resolve_ref(state, ref), reasoning, provenance, context=context)


def _shown(
    state: State, record_id: str, reasoning: bool, provenance: bool, *, context: bool = True
) -> Shown:
    s, d = state.snapshot, state.derived
    view = level1(s, d, record_id, state.failing)
    code = view.code if context else None
    siblings = tuple(i for i in core.family(s, code) if i != record_id) if code else ()
    citing = core.citers(s, d, code) if code else ()
    return Shown(
        view,
        level2(s, d, record_id, state.failing) if reasoning else None,
        level3(s, d, record_id) if provenance else None,
        state.read,
        level2_views(s, d, record_id, state.failing) if reasoning else (),
        newest_last(t for t in s.threads.values() if t.about == record_id),
        record_id in core.confirmable_ids(s, d),
        core.rests_on_tree(s, d, record_id),
        _views(state, d.supports.get(record_id, ())),
        siblings=_views(state, siblings[:10]),
        citers=_views(state, citing[:10]),
        left_out=(max(0, len(siblings) - 10), max(0, len(citing) - 10)),
    )


def show_many(w: Wiring, refs: Sequence[str], reasoning: bool, provenance: bool) -> ShownMany:
    """Each ref in order from one checked read, retaining failures and marking repeats."""
    state = read_checked(w)
    seen: dict[str, Shown] = {}
    items: list[tuple[str, Shown | LodgeError]] = []
    for ref in refs:
        try:
            ident = resolve_ref(state, ref)
            if ident in seen:
                shown = replace(seen[ident], repeat=True)
            else:
                shown = _shown(state, ident, reasoning, provenance)
                seen[ident] = shown
            items.append((ref, shown))
        except LodgeError as error:
            items.append((ref, error))
    return ShownMany(tuple(items), state.read)


def waiting_all(w: Wiring) -> tuple[Listed, ThreadsWaiting]:
    state = read_checked(w)
    listed = Listed(_newest_first(state, state.derived.awaiting_author), state.read)
    return listed, threads.waiting_in(state)


def timeline(w: Wiring, limit: int) -> Listed:
    if limit < 0:
        raise LodgeError(f"the limit must not be negative, got {limit}")
    state = read_checked(w)
    everything = _newest_first(state, state.snapshot.decisions)
    return Listed(everything[:limit], state.read, max(0, len(everything) - limit))


def spec(w: Wiring, area: str | None) -> tuple[str, Read, tuple[SpecArea, ...]]:
    state = read_checked(w)
    s = state.snapshot
    if area is not None and area not in s.areas and all(e.area != area for e in s.entries.values()):
        raise not_found(state, f"area named {area}", area)
    text = render_spec(s, state.derived, state.failing, area)
    return text, state.read, spec_view(s, state.derived, state.failing, area)


def check(w: Wiring, gate: bool) -> tuple[CheckResult, Read]:
    """The one-state checks, or with `gate` the comparison with the published state."""
    state = read_checked(w)
    if not gate:
        return state.result, state.read
    base = w.store.gate(state.current)
    cached = state.published_state if base.published is state.published else None
    if cached is None:
        published = load(base.published)
        before = core.derive(published)
        cached = Checked(published, before, core.check_state(published, derived=before))
    published, now = cached.snapshot, w.clock.now()
    found: dict[Problem, list[str]] = {}
    notes: dict[str, None] = {}
    for label, tree in base.checked:
        snapshot = state.snapshot if tree is state.current else load(tree)
        derived = state.derived if tree is state.current else core.derive(snapshot)
        standing_problems = (
            state.standing.problems
            if tree is state.current
            else core.check_state(snapshot, derived=derived).problems
        )
        facts = core.change_facts(
            published,
            snapshot,
            before=cached.derived,
            before_problems=cached.result.problems,
            after_derived=derived,
            after_problems=standing_problems,
        )
        result = core.check_change(published, snapshot, w.settings, now, facts=facts)
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


def draft(w: Wiring, ref: str) -> str:
    """The file of a record or area, with a `base` key and for an area a `name` key added."""
    state = read_state(w.store)
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
