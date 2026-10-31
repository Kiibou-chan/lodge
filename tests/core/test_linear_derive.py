"""Differential derivation and doubt tests, plus a checked-read call budget."""

import importlib
import random
import sys
from dataclasses import replace
from pathlib import Path
from typing import ClassVar

import pytest
from builders import area, at, decision, entry, snapshot_of, thread
from linear_check_oracles import old_doubt_marks
from linear_derive_oracle import old_derive
from linear_fixtures import Counted, chain

from lodge import core
from lodge.app.state import Wiring, read_checked
from lodge.core import (
    Action,
    Change,
    CoreSettings,
    Decision,
    Imported,
    Raises,
    Snapshot,
    ThreadState,
)
from lodge.core.doubts import doubt_marks

APP_TESTS = str(Path(__file__).resolve().parents[1] / "app")
if APP_TESTS not in sys.path:
    sys.path.insert(0, APP_TESTS)

from fakes import CountingIds, FixedClock, MemoryStore  # noqa: E402


class ComparedDecision(Decision):
    comparisons: ClassVar[int] = 0

    def __eq__(self, other: object) -> bool:
        ComparedDecision.comparisons += 1
        return isinstance(other, Decision) and self.id == other.id


def test_derive_same_as_before() -> None:
    rng = random.Random(161803)
    specs = [entry(id=f"s-{n:06x}") for n in range(4)]
    for size in range(1, 61):
        changes: list[Decision] = []
        for n in range(size):
            ids = [d.id for d in changes]
            d = decision(
                id=f"d-{n:06x}",
                date=at(rng.randrange(60)),
                decided_by="author" if n % 3 == 0 else "coordinator",
                imported_from=Imported("harbour.md", "Berths") if n % 4 == 0 else None,
                changes=tuple(
                    Change(e.id, rng.choice(list(Action)))
                    for e in rng.sample(specs, rng.randint(1, 3))
                ),
                replaces=tuple(rng.choices(ids, k=rng.randrange(3))) if ids else (),
                narrows=tuple(rng.choices(ids, k=rng.randrange(3))) if ids else (),
                confirms=tuple(rng.choices(ids, k=rng.randrange(3))) if ids else (),
            )
            changes.append(d)
        snapshot = snapshot_of(*specs, *changes)
        assert core.derive(snapshot) == old_derive(snapshot), f"seed 161803, size {size}"
    changes = [
        ComparedDecision(
            **vars(
                decision(
                    id=f"d-{n:06x}",
                    date=at(n),
                    decided_by="author" if n % 2 == 0 else "coordinator",
                    changes=(Change(specs[0].id, Action.EDIT),),
                )
            )
        )
        for n in range(60)
    ]
    snapshot = snapshot_of(specs[0], *changes)
    expected = old_derive(snapshot)
    ComparedDecision.comparisons = 0
    assert core.derive(snapshot) == expected
    assert ComparedDecision.comparisons <= 240, (
        "predecessors must not use list.index or prefix scans"
    )


def test_doubt_marks_same_as_before() -> None:
    rng = random.Random(141421)
    for size in range(1, 41):
        ids = [f"s-{n:06x}" for n in range(size)]
        specs = [
            entry(id=i, rests_on=tuple(rng.choices([*ids, "s-zzzzzz"], k=rng.randrange(4))))
            for i in ids
        ]
        decisions = [
            decision(
                changes=tuple(Change(i, rng.choice(list(Action))) for i in rng.choices(ids, k=3)),
                date=at(n),
            )
            for n in range(6)
        ]
        threads = [
            thread(about=i, raises=rng.choice(list(Raises)), state=rng.choice(list(ThreadState)))
            for i in [*ids, *(d.id for d in decisions)]
            if rng.random() < 0.4
        ]
        snapshot = snapshot_of(*specs, *decisions, *threads)
        changed_by = old_derive(snapshot).changed_by
        assert doubt_marks(snapshot, changed_by) == old_doubt_marks(snapshot, changed_by)
        assert tuple(doubt_marks(snapshot, changed_by).items()) == tuple(
            old_doubt_marks(snapshot, changed_by).items()
        )
    snapshot = chain(100)
    counted = Counted(snapshot.entries)
    assert doubt_marks(replace(snapshot, entries=counted), {}) == {}
    assert counted.reads <= 8 * len(counted), "no doubts must not trigger a walk from every entry"


def test_derive_once_per_checked_read(monkeypatch: pytest.MonkeyPatch) -> None:
    spec = entry()
    store = MemoryStore(area(order=(spec.id,)), spec, staged=True)
    original = core.derive
    calls: dict[int, int] = {}

    def counted(snapshot: Snapshot) -> core.Derived:
        calls[id(snapshot)] = calls.get(id(snapshot), 0) + 1
        return original(snapshot)

    for name in (
        "lodge.core",
        "lodge.core.check_change",
        "lodge.core.check_state",
        "lodge.core.check_areas",
        "lodge.core.check_entries",
    ):
        module = importlib.import_module(name)
        if hasattr(module, "derive"):
            monkeypatch.setattr(module, "derive", counted)
    read_checked(Wiring(store, FixedClock(), CountingIds(), CoreSettings()))
    assert sum(calls.values()) == 1
    assert sorted(calls.values()) == [1]
