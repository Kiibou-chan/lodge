"""One reading of the store: the snapshot, what derives from it, and what the check finds."""

from dataclasses import dataclass, field, replace
from datetime import datetime

from lodge import core
from lodge.app.errors import LodgeError, NotFound
from lodge.app.index_types import FileKey
from lodge.app.ports import Clock, IdSource, Index, Store
from lodge.app.results import Read
from lodge.core import (
    AmbiguousRef,
    CheckResult,
    CoreSettings,
    Derived,
    Snapshot,
    Tree,
    failing_ids,
    load,
    resolve,
    same_listing,
    unrecorded_problems,
)


@dataclass(frozen=True)
class Wiring:
    store: Store
    clock: Clock
    ids: IdSource
    settings: CoreSettings
    index: Index | None = None
    checked: "State | None" = None


@dataclass(frozen=True)
class Checked:
    snapshot: Snapshot
    derived: Derived
    result: CheckResult


@dataclass(frozen=True)
class State:
    current: Tree
    published: Tree
    snapshot: Snapshot
    derived: Derived
    result: CheckResult
    standing: CheckResult
    failing: frozenset[str]
    read: Read
    published_state: Checked | None = None
    epoch: int = 0
    parses: dict[FileKey, core.Parsed | None] = field(default_factory=dict)


def snapshot_of(
    tree: Tree,
    index: Index | None,
    memo: dict[FileKey, core.Parsed | None] | None = None,
    *,
    epoch: int | None = None,
) -> Snapshot:
    if index is None:
        return load(tree)
    epoch = index.epoch() if epoch is None else epoch
    keys = {path: (path, blob) for path, blob in tree.blobs.items() if path in tree.files}
    memo = memo if memo is not None else {}
    cached = {key: memo[key] for key in keys.values() if key in memo}
    cached.update(index.parses(tuple(key for key in keys.values() if key not in memo)))
    missing = {
        path: core.parse_file(path, text)
        for path, text in tree.files.items()
        if path not in keys or keys[path] not in cached
    }
    kept = {keys[path]: value for path, value in missing.items() if path in keys}
    memo.update(cached)
    memo.update(kept)
    index.keep_parses(kept, files=len(tree.files), used=memo, epoch=epoch)
    return core.assemble(
        {**{path: cached[key] for path, key in keys.items() if key in cached}, **missing},
        tree.attachments,
    )


def read_state(store: Store, index: Index | None = None) -> State:
    """The current state read once, with the one-state checks run on it."""
    current, published = store.trees()
    epoch = index.epoch() if index is not None else 0
    parses: dict[FileKey, core.Parsed | None] = {}
    snapshot = snapshot_of(current, index, parses, epoch=epoch)
    derived = core.derive(snapshot)
    result = core.check_state(snapshot, derived=derived)
    return State(
        current,
        published,
        snapshot,
        derived,
        result,
        result,
        failing_ids(snapshot, result),
        Read(store.freshness(), unrecorded_problems(snapshot, result), derived.status),
        epoch=epoch,
        parses=parses,
    )


def read_checked(w: Wiring) -> State:
    """`read_state`, with the checks against the published state folded into the failing records.

    Checks 4, 5, and 6 (LODGE-9) need the comparison; it is the one the gate makes, on the
    published tree the store returned, so a rewritten branch is compared with its accepted tip.
    Equal listings load to equal snapshots, and a state compared with itself finds nothing,
    so the comparison is skipped (d-zyqzkg).
    """
    if w.checked is not None:
        return w.checked
    state = read_state(w.store, w.index)
    if same_listing(state.current, state.published):
        return replace(state, published_state=Checked(state.snapshot, state.derived, state.result))
    published = snapshot_of(state.published, w.index, state.parses, epoch=state.epoch)
    before = core.derive(published)
    published_result = core.check_state(published, derived=before)
    return finish_checked(w, state, Checked(published, before, published_result), w.clock.now())


def finish_checked(w: Wiring, state: State, before_state: Checked, now: datetime) -> State:
    published, before, published_result = (
        before_state.snapshot,
        before_state.derived,
        before_state.result,
    )
    facts = core.change_facts(
        published,
        state.snapshot,
        before=before,
        before_problems=published_result.problems,
        after_derived=state.derived,
        after_problems=state.result.problems,
    )
    change = core.check_change(published, state.snapshot, w.settings, now, facts=facts)
    known = set(state.result.problems)
    problems = (*state.result.problems, *(p for p in change.problems if p not in known))
    result = CheckResult(
        tuple(sorted(problems, key=lambda p: (p.path, p.check, p.message))), state.result.notes
    )
    unrecorded = unrecorded_problems(state.snapshot, result)
    return replace(
        state,
        result=result,
        published_state=Checked(published, before, published_result),
        failing=failing_ids(state.snapshot, result),
        read=replace(state.read, unrecorded=unrecorded),
    )


def resolve_ref(state: State, ref: str) -> str:
    """The ID that `ref` names, an unknown or ambiguous one reported as a `LodgeError`."""
    try:
        found = resolve(state.snapshot, ref)
    except AmbiguousRef as error:
        raise LodgeError(str(error)) from error
    if found is None:
        raise not_found(state, f"record named {ref}", ref)
    return found


def not_found(state: State, what: str, needle: str) -> NotFound:
    """`no <what>`, naming the files that failed to read; those with `needle` in the path if any."""
    paths = [p.path for p in state.read.unrecorded if p.check == 1]
    named = [p for p in paths if needle.strip().lower() in p.lower()] or paths
    if not named:
        return NotFound(f"no {what}")
    return NotFound(f"no {what}; lodge could not read {', '.join(named)}, which may hold it")
