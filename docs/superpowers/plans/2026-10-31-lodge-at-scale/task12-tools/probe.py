"""Exclusive diagnostic phases and ranked candidate counts; synthetic stores only."""

import time

START = time.perf_counter()
import functools
import gc
import json
import sys

from lodge import core, main
from lodge.app import indexed, read_model, reads
from lodge.gitstore import index_states
from lodge.gitstore.index_db import IndexDB
from lodge.gitstore.index_states import IndexStates

stages = {}
stack = []
counts = {}
queries = []


def track(obj, name, label):
    original = getattr(obj, name)

    @functools.wraps(original)
    def measured(*a, **kw):
        frame = [time.perf_counter(), 0.0]
        stack.append(frame)
        counts[label] = counts.get(label, 0) + 1
        try:
            return original(*a, **kw)
        finally:
            elapsed = time.perf_counter() - frame[0]
            stack.pop()
            if stack:
                stack[-1][1] += elapsed
            stages[label] = stages.get(label, 0.0) + elapsed - frame[1]

    setattr(obj, name, measured)


opened = main.open_store


def open_store(*a, **kw):
    store = opened(*a, **kw)
    track(store, "identities", "identity")
    track(store, "listings", "listing")
    track(store, "texts", "miss texts")
    return store


main.open_store = open_store
for obj, name, label in [
    (main, "repo_root", "locate repository"),
    (main, "common_dir", "locate common dir"),
    (main, "_settings", "settings"),
    (main, "project_index", "open index"),
    (IndexDB, "epoch", "read epoch"),
    (IndexStates, "state", "state metadata lookup/decode"),
    (IndexStates, "seen", "marker lookup"),
    (indexed, "_built", "snapshot build other"),
    (core, "assemble", "assemble"),
    (core, "derive", "derive"),
    (core, "check_state", "check_state"),
    (core, "change_facts", "change facts"),
    (core, "check_change", "check_change"),
    (core, "family", "coded family"),
    (core, "citers", "citing records"),
    (reads, "_shown", "build show result"),
    (IndexDB, "parses", "parse lookup/decode"),
    (IndexStates, "facts", "facts lookup/decode"),
    (IndexStates, "rows", "row lookup/decode"),
    (IndexStates, "all_rows", "all row lookup/decode"),
    (IndexStates, "citing", "citer lookup/decode"),
    (IndexStates, "answer", "answer lookup/decode"),
    (IndexDB, "candidates", "FTS candidates"),
    (IndexStates, "keep_state", "keep SQL and encoding"),
    (IndexStates, "mark_seen", "marker SQL and encoding"),
    (index_states, "buckets", "bucket encoding"),
    (read_model, "build_rows", "build rows"),
    (read_model, "build_answers", "build answers"),
    (read_model, "build_citers", "build citers"),
    (read_model, "build_facts", "build facts"),
    (read_model, "build_state", "build state"),
]:
    track(obj, name, label)
rank = core.rank


def ranked(candidates, query, filters, *a, **kw):
    queries.append(dict(query=query.text, candidates=len(candidates)))
    return rank(candidates, query, filters, *a, **kw)


core.rank = ranked
track(core, "rank", "rank")
gc.disable()
ready = time.perf_counter() - START
start = time.perf_counter()
code = main.main(sys.argv[1:])
elapsed = time.perf_counter() - start
print(
    "TASK12_PHASES "
    + json.dumps(
        dict(
            stages=stages, counts=counts, queries=queries, import_seconds=ready, app_seconds=elapsed
        )
    ),
    file=sys.stderr,
)
raise SystemExit(code)
