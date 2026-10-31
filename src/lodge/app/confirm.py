"""Author confirmations through the ordinary decision write path."""

from collections.abc import Sequence

from lodge import core
from lodge.app import writes
from lodge.app.errors import LodgeError, StaleList
from lodge.app.results import AddOutcome, Behind, Written
from lodge.app.state import State, Wiring, not_found, read_state
from lodge.core import VIEWER, Scope, clean_text, confirmation_draft, level1


def _behind(state: State, name: str) -> tuple[str, ...]:
    s = state.snapshot
    if name not in s.areas and all(e.area != name for e in s.entries.values()):
        raise not_found(state, f"area named {name}", name)
    return core.behind_area(s, state.derived, name)


def behind_area(w: Wiring, name: str) -> tuple[Behind, ...]:
    state = read_state(w.store)
    s = state.snapshot
    return tuple(
        Behind(
            level1(s, state.derived, i, state.failing),
            tuple(
                (e, s.entries[e].area)
                for e in dict.fromkeys(
                    c.entry for c in s.decisions[i].changes if c.entry in s.entries
                )
            ),
        )
        for i in _behind(state, name)
    )


def confirm(
    w: Wiring,
    ids: Sequence[str],
    words: str,
    area: str | None,
    commit: bool,
) -> Written:
    words = clean_text(words)
    if not words:
        raise LodgeError("your words are required; nothing was written")
    state = read_state(w.store)
    expected = (
        _behind(state, area)
        if area is not None
        else (
            (ids[0],)
            if len(ids) == 1 and ids[0] in core.confirmable_ids(state.snapshot, state.derived)
            else ()
        )
    )
    if not expected or len(ids) != len(expected) or set(ids) != set(expected):
        raise StaleList("the list changed since the page was loaded; nothing was written")
    scope = (
        Scope.PRODUCT
        if any(state.snapshot.decisions[i].scope is Scope.PRODUCT for i in expected)
        else Scope.PROCESS
    )
    try:
        draft = confirmation_draft(
            expected, scope, words, w.clock.now().strftime("%Y-%m-%d %H:%M"), area
        )
    except ValueError as error:
        raise LodgeError("your words hold a character lodge cannot store") from error
    added = writes.add(w, [(VIEWER, draft)], False, False)
    committed = None
    if added.outcome is AddOutcome.STAGED and commit:
        committed = w.store.commit(
            added.paths, f"Author confirmation from the viewer: {added.ids[0]}"
        )
    return Written(added.ids, added.outcome, added.check, committed)
