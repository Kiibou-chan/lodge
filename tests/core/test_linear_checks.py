"""Checks retain their exact results while their input scans stay bounded."""

import importlib
import random
from dataclasses import replace

import pytest
from builders import area, at, decision, entry, snapshot_of
from checks import NOTES, NOW, OLD, SETTINGS, SPEC, creates, published, state
from linear_check_oracles import old_check_areas, old_check_cycles, old_dates
from linear_fixtures import Counted, ReadDecision, chain, fifty_areas, tracked_decision
from samples import EXAMPLE

from lodge.core import (
    Action,
    Change,
    Problem,
    change_facts,
    check_change,
    derive,
    new_record_path,
)
from lodge.core.check_areas import check_areas
from lodge.core.check_change import _dates, _missing
from lodge.core.check_cycles import check_cycles


def test_missing_builds_the_union_once() -> None:
    entries = [entry(id=f"s-{n:06x}") for n in range(2000)]
    before = snapshot_of(*entries)
    after = snapshot_of(*entries[:-1])
    decisions, specs, threads = (
        Counted(after.decisions),
        Counted(after.entries),
        Counted(after.threads),
    )
    after = replace(after, decisions=decisions, entries=specs, threads=threads)
    assert list(_missing(before, after)) == [
        Problem(
            before.paths[entries[-1].id],
            2,
            f"{entries[-1].id}: was published and is missing from this state",
        )
    ]
    assert [decisions.keys_calls, specs.keys_calls, threads.keys_calls] == [1, 1, 1]


def test_check_areas_same_problems_as_before(monkeypatch: pytest.MonkeyPatch) -> None:
    for snapshot in (snapshot_of(EXAMPLE), published(), fifty_areas()):
        assert list(check_areas(snapshot, derive(snapshot).status)) == list(
            old_check_areas(snapshot)
        )
    snapshot = fifty_areas()
    status = derive(snapshot).status
    module = importlib.import_module("lodge.core.check_areas")
    calls = []

    def redundant_derive(s: object) -> object:
        calls.append(s)
        return derive(snapshot)

    if hasattr(module, "derive"):
        monkeypatch.setattr(module, "derive", redundant_derive)
    list(check_areas(snapshot, status))
    assert not calls, "check_areas must use the supplied statuses"


def test_cycles_same_as_reachability() -> None:
    rng = random.Random(271828)
    for _ in range(200):
        ids = [f"s-{n:06x}" for n in range(rng.randint(1, 40))]
        snapshot = snapshot_of(
            *(
                entry(id=i, rests_on=tuple(rng.choices([*ids, "s-zzzzzz"], k=rng.randrange(6))))
                for i in ids
            )
        )
        assert list(check_cycles(snapshot)) == list(old_check_cycles(snapshot))
    snapshot = chain(80)
    counted = Counted(snapshot.entries)
    assert list(check_cycles(replace(snapshot, entries=counted))) == []
    assert counted.reads <= 8 * len(counted), "cycle detection must not walk from every entry"


def test_dates_same_as_before() -> None:
    rng = random.Random(314159)
    ids = [f"d-{n:06x}" for n in range(20)]
    specs = [f"s-{n:06x}" for n in range(8)]
    for size in range(1, 31):
        earlier = [
            decision(
                id=i,
                date=at(rng.randrange(60)),
                changes=tuple(Change(e, Action.EDIT) for e in rng.sample(specs, rng.randrange(4))),
            )
            for i in ids
        ]
        additions = [
            decision(
                id=f"d-{n + 100:06x}",
                date=at(rng.randrange(90)),
                imported_from=NOTES if n % 7 == 0 else None,
                replaces=tuple(rng.choices([*ids, "d-zzzzzz"], k=2)),
                narrows=tuple(rng.choices(ids, k=2)),
                confirms=tuple(rng.choices(ids, k=2)),
                changes=tuple(Change(e, Action.EDIT) for e in rng.sample(specs, rng.randrange(5))),
            )
            for n in range(size)
        ]
        before = snapshot_of(*earlier)
        after = snapshot_of(*earlier, *additions)
        current = snapshot_of(*earlier, *additions[: size // 2])
        for base in (None, current):
            assert list(_dates(before, after, NOW, base)) == list(
                old_dates(before, after, NOW, base)
            )
    earlier_tracked = [tracked_decision(n, f"s-{n:06x}") for n in range(30)]
    new_tracked = [tracked_decision(n + 100, f"s-{n + 100:06x}") for n in range(30)]
    before, after = snapshot_of(*earlier_tracked), snapshot_of(*earlier_tracked, *new_tracked)
    ReadDecision.changes_reads = 0
    assert list(_dates(before, after, NOW, None)) == []
    assert ReadDecision.changes_reads <= 300, "earlier changes must be indexed once"


def test_check_change_with_facts_equals_without() -> None:
    bad = decision(id="d-bbbbbb", decided_by="author", quote=None, date=at(1))
    new = entry(id="s-bbbbbb", title="Another")
    cases = [
        (published(), state()),
        (published(), state(drop=(OLD,))),
        (state(bad), state(bad)),
        (published(), state(area(order=(SPEC, new.id)), new, creates(new.id, date=at(30)))),
        (published(), state(entry(id=SPEC, statement="Changed."))),
    ]
    for verb in ("replaces", "narrows", "confirms"):
        for date in (at(0), at(30), "2027-01-01T00:00:00+00:00"):
            d = decision(decided_by="author", date=date, **{verb: (OLD,)})
            cases.append((published(), state(d)))
    before = fifty_areas()
    edited = replace(next(iter(before.entries.values())), statement="A revised berth rule.")
    d = decision(changes=(Change(edited.id, Action.EDIT),), date=at(30))
    after = replace(
        before,
        entries={**before.entries, edited.id: edited},
        decisions={**before.decisions, d.id: d},
        paths={**before.paths, d.id: new_record_path(d)},
    )
    cases.append((before, after))
    for before, after in cases:
        facts = change_facts(before, after)
        assert check_change(before, after, SETTINGS, NOW, facts=facts) == check_change(
            before, after, SETTINGS, NOW
        )
        assert check_change(before, after, SETTINGS, NOW, after, facts=facts) == check_change(
            before, after, SETTINGS, NOW, after
        )
