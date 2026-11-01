"""Indexed reads with pinned inputs and an optional keep after output.

The listing assembler must stay equivalent to state.snapshot_of/read_checked;
test_outputs_print_as_in_memory compares both paths over synthetic stores.
"""

from collections.abc import Callable, Sequence
from dataclasses import replace
from datetime import datetime
from hashlib import sha1
from itertools import chain

from lodge import core
from lodge.app import read_model, reads
from lodge.app import threads as thread_reads
from lodge.app.errors import LodgeError
from lodge.app.index_lookups import Lookups, Miss, QueryFallback
from lodge.app.index_types import FileKey, level1_of
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
    cached_facts = index.facts(published.ident)
    complete = cached_facts is not None and cached_facts.status.keys() == (
        before.decisions.keys() | before.entries.keys()
    )
    change = read_model.change_facts_of(state, cached_facts) if complete and cached_facts else None
    if change is not None:
        assert cached_facts is not None
        checked = Checked(before, None, core.CheckResult((), ()), cached_facts)
        return finish_checked(w, state, checked, now, facts=change), tuple(misses)
    derived = core.derive(before)
    # Published problems only classify notes that finish_checked discards.
    # Exact readers and the gate still compute the published check in full.
    checked = Checked(before, derived, core.CheckResult((), ()))
    return finish_checked(w, state, checked, now), tuple(misses)


def _run[T](
    w: Wiring, memory: Callable[[Wiring], T], cached: Callable[[Lookups], T]
) -> tuple[T, Callable[[], None]]:
    index = w.index
    assert index is not None
    current, published = w.store.identities()
    key, now, epoch = state_key(current, published, w.settings), w.clock.now(), index.epoch()
    seen = False
    query_fallback = False
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
    except QueryFallback:
        query_fallback = True
    except LodgeError:
        raise
    except Exception:
        # A partial cached answer is discarded with its transaction.
        seen = index.seen(key)
    state, misses = _built(w, now, epoch)
    result = memory(replace(w, checked=state))
    if query_fallback:
        return result, _nothing
    files = len(state.current.blobs)
    if not seen:
        index.mark_seen(
            key,
            {k: state.parses[k] for k in misses},
            read_model.build_facts(state, current, published),
            files=files,
            used=state.parses,
            epoch=epoch,
        )
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
        if ref.lower() not in lookups.state.threads:
            raise lookups.not_found(f"thread named {ref}", ref)
        value = lookups.index.answer(lookups.state.key, f"thread:{ref.lower()}")
        if not isinstance(value, ThreadShown):
            raise Miss
        return replace(value, read=lookups.read)

    return _run(w, lambda w: thread_reads.show(w, ref), cached)


def search_many(
    w: Wiring, queries: Sequence[core.Query], filters: core.Filters, limit: int
) -> tuple[tuple[Listed, ...], Callable[[], None]]:
    def cached(lookups: Lookups) -> tuple[Listed, ...]:
        if any(core.needs_memory(q) for q in queries):
            raise QueryFallback
        seen: set[str] = set()
        results: list[Listed] = []
        for query in queries or [core.parse_query("")]:
            words = lookups.index.candidates(query.words, False)
            if words is None:
                raise QueryFallback
            members = (
                lookups.family(query.text.strip()) if core.is_code_token(query.text.strip()) else ()
            )
            citing: tuple[str, ...] = ()
            if members:
                code = query.text.strip().lower()
                found = lookups.index.citing(lookups.state.key, code, None)
                if found is None or len(found) != lookups.state.citers.get(code, -1):
                    raise Miss
                citing = found
            parsed = lookups.index.parses(list(words))
            if set(parsed) != set(words):
                raise Miss
            records: set[str] = set()
            # Several historical parses may name one ID; only its state row chooses the key.
            ids = {p.id for p in parsed.values() if isinstance(p, (core.Decision, core.SpecEntry))}
            exact = query.text.strip().lower()
            extras = {*members, *citing}
            if core.is_id(exact) and exact.startswith(("d-", "s-")):
                extras.add(exact)
            rows = (
                lookups.index.all_rows(lookups.state.key)
                if not query.text.strip()
                else lookups.index.rows(lookups.state.key, ids | extras)
            )
            if (
                rows is None
                or (not query.text.strip() and not rows)
                or not {*members, *citing} <= rows.keys()
            ):
                raise Miss
            assert rows is not None
            for key, record in parsed.items():
                if not isinstance(record, (core.Decision, core.SpecEntry)):
                    raise Miss
                if record.id in rows and rows[record.id].key == key:
                    records.add(record.id)
                    lookups.loaded[record.id] = rows[record.id], record
            candidates: list[core.Candidate] = []
            if not query.text.strip():
                candidates = lookups.empty_candidates(rows)
            wanted = set() if not query.text.strip() else records | (extras & rows.keys())
            for ident in wanted:
                if ident not in lookups.loaded:
                    # Resolve exact IDs, codes, and citers absent from the word candidates.
                    row = rows[ident]
                    value = lookups.index.parses([row.key]).get(row.key)
                    if not isinstance(value, (core.Decision, core.SpecEntry)) or value.id != ident:
                        raise Miss
                    lookups.loaded[ident] = row, value
                row, record = lookups.loaded[ident]
                held = words.get(row.key)
                if held is None:
                    title, statement = core.parse_words(record)
                    held = frozenset(title.split()), frozenset(statement.split())
                title_words, statement_words = held
                candidates.append(
                    core.Candidate(level1_of(row, record), row.areas, title_words, statement_words)
                )
            ids_ranked, _ = core.rank(candidates, query, filters, members, citing, len(candidates))
            above = tuple(i for i in ids_ranked if i in seen)
            fresh = [i for i in ids_ranked if i not in seen]
            shown = fresh[:limit]
            results.append(
                Listed(
                    tuple(lookups.view(i) for i in shown),
                    lookups.read,
                    len(fresh) - len(shown),
                    query.text,
                    above,
                )
            )
            seen.update(shown)
        return tuple(results)

    return _run(w, lambda w: reads.search_many(w, queries, filters, limit), cached)
