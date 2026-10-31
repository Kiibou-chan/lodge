"""Check 7: each area's order lists exactly the current entries of its folder."""

from collections.abc import Iterator, Mapping

from lodge.core.derive import Status
from lodge.core.fileformat import area_path
from lodge.core.model import Problem
from lodge.core.snapshot import Snapshot


def check_areas(s: Snapshot, status: Mapping[str, Status]) -> Iterator[Problem]:
    by_area: dict[str, list[str]] = {}
    for e in s.entries.values():
        by_area.setdefault(e.area, []).append(e.id)
    folders = sorted(by_area.keys() | s.areas.keys())
    for name in folders:
        entries = sorted(by_area.get(name, ()))
        if name not in s.areas:
            message = f"area {name}: has entries but no _area.md"
            yield Problem(area_path(name), 7, message)
            continue
        current = {i for i in entries if status[i] == "current"}
        order = s.areas[name].order
        counts: dict[str, int] = {}
        for entry_id in order:
            counts[entry_id] = counts.get(entry_id, 0) + 1
        for entry_id in entries:
            if entry_id in current and entry_id not in counts:
                message = f"{entry_id}: is not listed in the order of area {name}"
                yield Problem(s.paths[entry_id], 7, message)
        for entry_id in counts:
            if entry_id not in current:
                message = (
                    f"area {name}: order lists {entry_id}, which is not a current entry of the area"
                )
                yield Problem(area_path(name), 7, message)
            elif counts[entry_id] > 1:
                message = f"area {name}: order lists {entry_id} more than once"
                yield Problem(area_path(name), 7, message)
