"""Written reading order and the dependency traversal within each area."""

from collections.abc import Iterator
from dataclasses import dataclass

from lodge.core.derive import Derived
from lodge.core.snapshot import Snapshot


@dataclass(frozen=True)
class Placement:
    """An entry with its depth and last-placed dependency parent."""

    id: str
    depth: int
    under: str | None


def area_names(s: Snapshot) -> tuple[str, ...]:
    """Ranked areas by rank and name, then unranked areas by name."""
    names = {*s.areas, *(e.area for e in s.entries.values())}

    def key(name: str) -> tuple[bool, int, str]:
        area = s.areas.get(name)
        rank = area.rank if area else None
        return rank is None, rank if rank is not None else 0, name

    return tuple(sorted(names, key=key))


def written_order(s: Snapshot, d: Derived, area: str) -> tuple[str, ...]:
    """Current entries in the area order, then remaining entries by ID."""
    current = {i for i, e in s.entries.items() if e.area == area and d.status.get(i) == "current"}
    held = s.areas.get(area)
    ordered = [i for i in (held.order if held else ()) if i in current]
    return tuple(dict.fromkeys([*ordered, *sorted(current - set(ordered))]))


def derived_order(s: Snapshot, d: Derived, area: str) -> tuple[Placement, ...]:
    """Entries after their dependencies, depth first; cycles fall back to written order."""
    ordered = written_order(s, d, area)
    current = set(ordered)
    targets = {i: tuple(t for t in s.entries[i].rests_on if t in current) for i in ordered}
    placed: dict[str, Placement] = {}
    result: list[Placement] = []

    def place(i: str, under: str | None = None) -> None:
        depth = placed[under].depth + 1 if under is not None else 0
        p = Placement(i, depth, under)
        placed[i] = p
        result.append(p)

    while remaining := [i for i in ordered if i not in placed]:
        ready = next((i for i in remaining if all(t in placed for t in targets[i])), remaining[0])
        place(ready)
        stack = [ready]
        while stack:
            parent = stack[-1]
            child = next(
                (
                    j
                    for j in ordered
                    if j not in placed
                    and parent in targets[j]
                    and all(t in placed for t in targets[j])
                ),
                None,
            )
            if child is None:
                stack.pop()
            else:
                place(child, parent)
                stack.append(child)
    return tuple(result)


@dataclass(frozen=True)
class Branch:
    """An entry in a dependency tree, with its current derived status."""

    id: str
    title: str
    status: str
    children: tuple["Branch", ...]


def rests_on_tree(s: Snapshot, d: Derived, entry_id: str) -> tuple[Branch, ...]:
    """Expand each dependency once, retaining shared targets as leaf references."""
    expanded = {entry_id}
    if entry_id not in s.entries:
        return ()
    ancestors = {entry_id}
    stack: list[tuple[str, Iterator[str], list[Branch]]] = [
        (entry_id, iter(dict.fromkeys(s.entries[entry_id].rests_on)), [])
    ]
    while stack:
        ident, targets, children = stack[-1]
        target = next(targets, None)
        if target is None:
            stack.pop()
            ancestors.remove(ident)
            if not stack:
                return tuple(children)
            stack[-1][2].append(
                Branch(ident, s.entries[ident].title, d.status[ident], tuple(children))
            )
        elif target in s.entries and target not in ancestors:
            if target in expanded:
                children.append(Branch(target, s.entries[target].title, d.status[target], ()))
            else:
                expanded.add(target)
                ancestors.add(target)
                stack.append((target, iter(dict.fromkeys(s.entries[target].rests_on)), []))
    return ()
