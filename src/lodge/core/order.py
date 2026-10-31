"""Written reading order and the dependency traversal within each area."""

from dataclasses import dataclass

from lodge.core.derive import Derived
from lodge.core.snapshot import Snapshot


@dataclass(frozen=True)
class Placement:
    id: str
    depth: int
    under: str | None


def area_names(s: Snapshot) -> tuple[str, ...]:
    names = {*s.areas, *(e.area for e in s.entries.values())}

    def key(name: str) -> tuple[bool, int, str]:
        area = s.areas.get(name)
        rank = area.rank if area else None
        return rank is None, rank if rank is not None else 0, name

    return tuple(sorted(names, key=key))


def written_order(s: Snapshot, d: Derived, area: str) -> tuple[str, ...]:
    current = {i for i, e in s.entries.items() if e.area == area and d.status.get(i) == "current"}
    held = s.areas.get(area)
    ordered = [i for i in (held.order if held else ()) if i in current]
    return tuple(dict.fromkeys([*ordered, *sorted(current - set(ordered))]))


def derived_order(s: Snapshot, d: Derived, area: str) -> tuple[Placement, ...]:
    ordered = written_order(s, d, area)
    targets = {i: tuple(t for t in s.entries[i].rests_on if t in ordered) for i in ordered}
    placed: dict[str, Placement] = {}
    result: list[Placement] = []

    def visit(i: str, trigger: str | None = None) -> None:
        under = trigger
        depth = placed[under].depth + 1 if under is not None else 0
        p = Placement(i, depth, under)
        placed[i] = p
        result.append(p)
        while child := next(
            (
                j
                for j in ordered
                if j not in placed and i in targets[j] and all(t in placed for t in targets[j])
            ),
            None,
        ):
            visit(child, i)

    while remaining := [i for i in ordered if i not in placed]:
        ready = next((i for i in remaining if all(t in placed for t in targets[i])), remaining[0])
        visit(ready)
    return tuple(result)
