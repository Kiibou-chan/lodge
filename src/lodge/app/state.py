"""One reading of the store: the snapshot, what derives from it, and what the check finds."""

from dataclasses import dataclass

from lodge import core
from lodge.app.errors import LodgeError, NotFound
from lodge.app.ports import Clock, IdSource, Store
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
    unrecorded_problems,
)


@dataclass(frozen=True)
class Wiring:
    store: Store
    clock: Clock
    ids: IdSource
    settings: CoreSettings


@dataclass(frozen=True)
class State:
    current: Tree
    published: Tree
    snapshot: Snapshot
    derived: Derived
    result: CheckResult
    failing: frozenset[str]
    read: Read


def read_state(store: Store) -> State:
    """The current state read once, with the one-state checks run on it."""
    current, published = store.trees()
    snapshot = load(current)
    result = core.check_state(snapshot)
    derived = core.derive(snapshot)
    return State(
        current,
        published,
        snapshot,
        derived,
        result,
        failing_ids(snapshot, result),
        Read(store.freshness(), unrecorded_problems(snapshot, result), derived.status),
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
