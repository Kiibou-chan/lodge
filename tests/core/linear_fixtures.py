"""Synthetic scale fixtures and operation counters, with no timing assertions."""

from collections.abc import Iterator, KeysView, Mapping
from dataclasses import replace
from typing import Any, ClassVar

from builders import area, at, decision, entry, snapshot_of

from lodge.core import Action, Change, Decision, Snapshot


class Counted[T](Mapping[str, T]):
    def __init__(self, values: Mapping[str, T]) -> None:
        self.values_by_id = values
        self.keys_calls = 0
        self.reads = 0

    def __getitem__(self, key: str) -> T:
        self.reads += 1
        return self.values_by_id[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self.values_by_id)

    def __len__(self) -> int:
        return len(self.values_by_id)

    def keys(self) -> KeysView[str]:
        self.keys_calls += 1
        return super().keys()


class ReadDecision(Decision):
    changes_reads: ClassVar[int] = 0

    def __getattribute__(self, name: str) -> Any:
        if name == "changes":
            ReadDecision.changes_reads += 1
        return super().__getattribute__(name)


def fifty_areas() -> Snapshot:
    entries = [entry(id=f"s-{n:06x}", area=f"area-{n // 2:03d}") for n in range(100)]
    areas = [
        area(name=f"area-{n:03d}", order=tuple(e.id for e in entries if e.area == f"area-{n:03d}"))
        for n in range(49)
    ]
    areas[0] = replace(areas[0], order=areas[0].order[:1])
    areas[2] = replace(areas[2], order=(*areas[2].order, areas[2].order[0]))
    retired = decision(changes=(Change(entries[2].id, Action.RETIRE),))
    return snapshot_of(*areas, *entries, retired)


def chain(size: int) -> Snapshot:
    entries = [
        entry(id=f"s-{n:06x}", rests_on=(f"s-{n - 1:06x}",) if n else ()) for n in range(size)
    ]
    return snapshot_of(area(order=tuple(e.id for e in entries)), *entries)


def tracked_decision(number: int, spec: str) -> ReadDecision:
    d = decision(id=f"d-{number:06x}", date=at(number % 60), changes=(Change(spec, Action.EDIT),))
    return ReadDecision(**vars(d))
