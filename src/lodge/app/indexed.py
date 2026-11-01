"""Indexed reads with pinned inputs and an optional keep after output."""

from collections.abc import Callable, Sequence
from dataclasses import replace
from datetime import datetime
from hashlib import sha1
from itertools import chain

from lodge import core
from lodge.app import read_model, reads
from lodge.app import threads as thread_reads
from lodge.app.index_lookups import Lookups, Miss
from lodge.app.index_types import FileKey
from lodge.app.results import Listed, Read, ShownMany, ThreadList, ThreadShown, ThreadsWaiting
from lodge.app.state import Checked, State, Wiring, finish_checked


def state_key(current: str, published: str, settings: object) -> str:
    settings_digest = sha1(repr(settings).encode()).hexdigest()
    return sha1(
        repr((current, published, settings_digest)).encode("utf-8", "surrogateescape")
    ).hexdigest()


def _nothing() -> None:
    pass


def _built(w: Wiring, now: datetime, epoch: int) -> tuple[State, tuple[FileKey, ...]]:
    index = w.index
    assert index is not None
    current, published = w.store.listings()
    parses: dict[FileKey, core.Parsed | None] = {}
    misses: list[FileKey] = []

    def snapshot(listing: core.Listing) -> core.Snapshot:
        keys = [(path, blob) for path, blob in listing.blobs.items()]
        parses.update(index.parses([k for k in keys if k not in parses]))
        absent = [k for k in keys if k not in parses]
        texts = w.store.texts(listing, [p for p, _ in absent]) if absent else {}
        for path, blob in absent:
            if path not in texts:
                raise Miss
            parses[path, blob] = core.parse_file(path, texts[path])
        misses.extend(absent)
        return core.assemble({path: parses[path, blob] for path, blob in keys}, listing.attachments)

    s = snapshot(current)
    d = core.derive(s)
    result = core.check_state(s, derived=d)
    # These trees carry the pinned listing; record text lives in parses and the snapshot.
    a = core.Tree(current.rev, {}, current.attachments, current.blobs)
    b = core.Tree(published.rev, {}, published.attachments, published.blobs)
    state = State(
        a,
        b,
        s,
        d,
        result,
        result,
        core.failing_ids(s, result),
        Read(w.store.freshness(), core.unrecorded_problems(s, result), d.status),
        epoch=epoch,
        parses=parses,
    )
    if (current.blobs, current.attachments) == (published.blobs, published.attachments):
        return replace(state, published_state=Checked(s, d, result)), tuple(misses)
    before = snapshot(published)
    derived = core.derive(before)
    checked = Checked(before, derived, core.check_state(before, derived=derived))
    return finish_checked(w, state, checked, now), tuple(misses)


def _run[T](
    w: Wiring, memory: Callable[[Wiring], T], cached: Callable[[Lookups], T]
) -> tuple[T, Callable[[], None]]:
    index = w.index
    assert index is not None
    current, published = w.store.identities()
    key, now, epoch = state_key(current, published, w.settings), w.clock.now(), index.epoch()
    seen = False
    try:
        with index.reading():
            stored = index.state(key)
            if (
                stored is not None
                and (stored.valid_from is None or datetime.fromisoformat(stored.valid_from) <= now)
                and (stored.valid_until is None or now < datetime.fromisoformat(stored.valid_until))
            ):
                return cached(
                    Lookups(index, stored, Read(w.store.freshness(), stored.unrecorded))
                ), _nothing
            seen = index.seen(key)
    except Exception:
        # A partial cached answer is discarded with its transaction.
        seen = index.seen(key)
    state, misses = _built(w, now, epoch)
    result = memory(replace(w, checked=state))
    files = len(state.current.blobs)
    if not seen:
        index.mark_seen(key, {k: state.parses[k] for k in misses}, {}, files=files)
        return result, _nothing

    def keep() -> None:
        try:
            rows = read_model.build_rows(state)
            codes: dict[str, tuple[str, ...]] = {}
            for record in chain[core.Decision | core.SpecEntry](
                state.snapshot.decisions.values(), state.snapshot.entries.values()
            ):
                if record.code:
                    code = record.code.lower()
                    codes[code] = (*codes.get(code, ()), record.id)
            answers = read_model.build_answers(state)
            citing = read_model.build_citers(state, codes)
            facts = read_model.build_facts(state, current, published)
            stored = read_model.build_state(
                state, key, current, published, now, rows, answers, citing
            )
            index.keep_state(
                stored, rows, answers, citing, facts, state.parses, misses, epoch, files=files
            )
        except Exception:
            pass

    return result, keep


def show_many(
    w: Wiring, refs: Sequence[str], reasoning: bool, provenance: bool
) -> tuple[ShownMany, Callable[[], None]]:
    return _run(
        w,
        lambda w: reads.show_many(w, refs, reasoning, provenance),
        lambda lookups: lookups.show_many(refs, reasoning, provenance),
    )


def waiting_all(w: Wiring) -> tuple[tuple[Listed, ThreadsWaiting], Callable[[], None]]:
    def cached(lookups: Lookups) -> tuple[Listed, ThreadsWaiting]:
        value = lookups.index.answer(lookups.state.key, "waiting")
        if (
            not isinstance(value, tuple)
            or len(value) != 2
            or not isinstance(value[0], Listed)
            or not isinstance(value[1], ThreadsWaiting)
        ):
            raise Miss
        return replace(value[0], read=lookups.read), replace(value[1], read=lookups.read)

    return _run(w, reads.waiting_all, cached)


def threads(w: Wiring) -> tuple[ThreadList, Callable[[], None]]:
    def cached(lookups: Lookups) -> ThreadList:
        value = lookups.index.answer(lookups.state.key, "threads")
        if not isinstance(value, ThreadList):
            raise Miss
        return replace(value, read=lookups.read)

    return _run(w, thread_reads.list_open, cached)


def thread(w: Wiring, ref: str) -> tuple[ThreadShown, Callable[[], None]]:
    def cached(lookups: Lookups) -> ThreadShown:
        value = lookups.index.answer(lookups.state.key, f"thread:{ref.lower()}")
        if not isinstance(value, ThreadShown):
            raise Miss
        return replace(value, read=lookups.read)

    return _run(w, lambda w: thread_reads.show(w, ref), cached)
