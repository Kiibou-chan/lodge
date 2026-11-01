"""Time the three adversarial shapes that a multi-area benchmark can hide.

uv run --frozen python docs/superpowers/plans/2026-10-31-lodge-at-scale/probes/shapes.py
Fixtures are synthetic snapshots, built without disk or a real repository.
"""

import argparse
import gc
import time
from datetime import UTC, datetime, timedelta

from lodge.core import (
    Action,
    Area,
    Change,
    CoreSettings,
    Decision,
    Scope,
    Snapshot,
    SpecEntry,
    change_facts,
    check_change,
    check_state,
    derive,
    new_record_path,
)


def snapshot(entries, decisions):
    return Snapshot(
        {d.id: d for d in decisions},
        {e.id: e for e in entries},
        {"harbour": Area("harbour", "Harbour", "", tuple(e.id for e in entries))},
        {r.id: new_record_path(r) for r in [*entries, *decisions]},
        (),
        frozenset(),
        {},
    )


def decision(number, entry, action=Action.EDIT, *, author=False):
    return Decision(
        f"d-{number:06x}",
        "Schedule a berth",
        Scope.PRODUCT,
        "author" if author else "coordinator",
        (datetime(2026, 1, 1, tzinfo=UTC) + timedelta(seconds=number)).isoformat(),
        "A berth has a crane.",
        changes=(Change(entry, action),),
    )


def shapes(size):
    empty = snapshot([], [])
    single = [SpecEntry("s-000000", "harbour", "Berth", "A berth has a crane.")]
    yield (
        "one entry, many decisions",
        empty,
        snapshot(
            single, [decision(n, single[0].id, author=n % 3 == 0) for n in range(size)]
        ),
    )
    chain = [
        SpecEntry(
            f"s-{n:06x}",
            "harbour",
            "Berth",
            "A berth has a crane.",
            rests_on=(f"s-{n - 1:06x}",) if n else (),
        )
        for n in range(size)
    ]
    yield "chain, no doubts", empty, snapshot(chain, [])
    entries = [
        SpecEntry(f"s-{n:06x}", "harbour", "Berth", "A berth has a crane.")
        for n in range(size)
    ]
    published = [decision(n, e.id, Action.CREATE) for n, e in enumerate(entries)]
    added = [decision(n + size, e.id) for n, e in enumerate(entries)]
    yield (
        "new decisions, published state",
        snapshot(entries, published),
        snapshot(entries, [*published, *added]),
    )


def measure(before, after):
    start = time.perf_counter()
    before_d, after_d = derive(before), derive(after)
    derived = time.perf_counter()
    before_result = check_state(before, derived=before_d)
    after_result = check_state(after, derived=after_d)
    checked = time.perf_counter()
    facts = change_facts(
        before,
        after,
        before=before_d,
        before_problems=before_result.problems,
        after_derived=after_d,
        after_problems=after_result.problems,
    )
    check_change(
        before, after, CoreSettings(), datetime(2026, 12, 31, tzinfo=UTC), facts=facts
    )
    finished = time.perf_counter()
    return derived - start, checked - derived, finished - checked, finished - start


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sizes", nargs="+", type=int, default=[2000, 4000, 8000])
    parser.add_argument("--runs", type=int, default=3)
    args = parser.parse_args()
    gc.disable()
    print(
        "| Shape | Size | Derive (s) | State checks (s) | Change checks (s) | Total (s) |"
    )
    print("|---|---:|---:|---:|---:|---:|")
    for size in args.sizes:
        for label, before, after in shapes(size):
            samples = [measure(before, after) for _ in range(args.runs)]
            best = [min(sample[i] for sample in samples) for i in range(4)]
            print(
                f"| {label} | {size} | "
                + " | ".join(f"{value:.4f}" for value in best)
                + " |",
                flush=True,
            )


if __name__ == "__main__":
    main()
