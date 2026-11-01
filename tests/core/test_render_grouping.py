"""Whole-spec rendering groups entries once instead of scanning for every area."""

from collections.abc import ItemsView, Iterator, Mapping
from dataclasses import replace

from builders import area, entry, snapshot_of

from lodge.core import SpecEntry, derive, render_spec


class CountedEntries(Mapping[str, SpecEntry]):
    def __init__(self, entries: Mapping[str, SpecEntry]) -> None:
        self.entries = entries
        self.scans = 0

    def __getitem__(self, key: str) -> SpecEntry:
        return self.entries[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self.entries)

    def __len__(self) -> int:
        return len(self.entries)

    def items(self) -> ItemsView[str, SpecEntry]:
        self.scans += 1
        return ItemsView(self)


def test_whole_spec_groups_entries_once() -> None:
    entries = [entry(id=f"s-{n:06d}", area=f"area-{n}") for n in range(20)]
    s = snapshot_of(*entries, *(area(name=e.area, order=(e.id,)) for e in entries))
    d = derive(s)
    expected = render_spec(s, d, frozenset())
    counted = CountedEntries(s.entries)
    counted.scans = 0
    actual = render_spec(replace(s, entries=counted), d, frozenset())
    assert actual == expected
    assert counted.scans <= 1
