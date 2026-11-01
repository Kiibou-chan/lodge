"""Synthetic states, direct keeps, and printed CLI comparisons."""

import io
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import replace
from itertools import chain

from builders import area, at, decision, entry, files_of, message, thread
from fakes import CountingIds, FixedClock, MemoryStore
from support import project

from lodge import core
from lodge.app import Index, Lodge, LodgeError, read_model
from lodge.app.indexed import state_key
from lodge.app.state import State, Wiring, read_checked
from lodge.cli import run
from lodge.core import Action, Change, CoreSettings, Raises


def large_store() -> MemoryStore:
    records = [
        decision(id=f"d-{n:06x}", code=f"B.{n}", date=at(n), statement="See B.1 and A.")
        for n in range(240)
    ]
    entries = [entry(id=f"s-{n:06x}", code=f"E.{n}") for n in range(240)]
    records[1] = replace(records[1], decided_by="author")
    records[2] = replace(records[2], replaces=(records[0].id,))
    records[3] = replace(records[3], narrows=(records[1].id,))
    records[4] = replace(records[4], confirms=(records[1].id,), decided_by="author")
    records[5] = replace(records[5], changes=(Change(entries[0].id, Action.RETIRE),))
    records[6] = replace(records[6], changes=(Change(entries[1].id, Action.CREATE),))
    store = MemoryStore(
        area(order=tuple(e.id for e in entries)),
        *records,
        *entries,
        *(decision(id=f"d-{n + 300:06x}") for n in range(20)),
    )
    store.files.update(
        files_of(
            thread(id="q-aaaaaa", about=entries[1].id),
            thread(
                id="q-bbbbbb",
                about=records[1].id,
                raises=Raises.QUESTION,
                messages=(
                    message(by="author", where="synthetic session", when="2026-10-28 10:00"),
                ),
            ),
        )
    )
    return store


def samples() -> list[MemoryStore]:
    broken = project(True)
    path = next(p for p in broken.files if "d-aaaaaa" in p)
    broken.files[path] = broken.files[path].replace("evidence", "logs")
    broken.files["lodge/decisions/broken.md"] = "broken"
    return [project(), broken, MemoryStore(decision(code="A")), MemoryStore(), large_store()]


def app(
    store: MemoryStore,
    index: Index | None = None,
    clock: FixedClock | None = None,
    settings: CoreSettings | None = None,
) -> Lodge:
    return Lodge(store, clock or FixedClock(), CountingIds(), settings or CoreSettings(), index)


def printed(lodge: Lodge, args: list[str]) -> tuple[int, str, str]:
    out, err = io.StringIO(), io.StringIO()
    with redirect_stdout(out), redirect_stderr(err):
        try:
            code = run(args, lambda: lodge, lambda: "", lambda *_: 0, lambda: 0)
        except LodgeError as error:
            print(f"lodge: {error}", file=err)
            code = error.exit_code
    return code, out.getvalue(), err.getvalue()


def checked(store: MemoryStore) -> State:
    return read_checked(Wiring(store, FixedClock(), CountingIds(), CoreSettings()))


def seed(store: MemoryStore, index: Index) -> str:
    state = checked(store)
    current, published = store.identities()

    key = state_key(current, published, CoreSettings())
    rows = read_model.build_rows(state)
    codes: dict[str, tuple[str, ...]] = {}
    for record in chain[core.Decision | core.SpecEntry](
        state.snapshot.decisions.values(), state.snapshot.entries.values()
    ):
        if record.code:
            codes[record.code.lower()] = (*codes.get(record.code.lower(), ()), record.id)
    citing = read_model.build_citers(state, codes)
    answers = read_model.build_answers(state)
    stored = read_model.build_state(
        state, key, current, published, FixedClock().now(), rows, answers, citing
    )

    parses = {
        (path, state.current.blobs[path]): core.parse_file(path, text)
        for path, text in state.current.files.items()
        if path in state.current.blobs
    }
    index.keep_state(
        stored,
        rows,
        answers,
        citing,
        read_model.build_facts(state, current, published),
        parses,
        tuple(parses),
        index.epoch(),
        files=len(state.current.files),
    )
    return key
