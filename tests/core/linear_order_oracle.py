"""Pre-Task-2 traversals and branch rendering, retained as differential oracles."""

from lodge.core import Branch, Derived, Placement, Snapshot
from lodge.viewer.html import e, link


def old_written_order(s: Snapshot, d: Derived, area: str) -> tuple[str, ...]:
    """Current entries in the area order, then remaining entries by ID."""
    current = {i for i, e in s.entries.items() if e.area == area and d.status.get(i) == "current"}
    held = s.areas.get(area)
    ordered = [i for i in (held.order if held else ()) if i in current]
    return tuple(dict.fromkeys([*ordered, *sorted(current - set(ordered))]))


def old_derived_order(s: Snapshot, d: Derived, area: str) -> tuple[Placement, ...]:
    """Entries after their dependencies, depth first; cycles fall back to written order."""
    ordered = old_written_order(s, d, area)
    targets = {i: tuple(t for t in s.entries[i].rests_on if t in ordered) for i in ordered}
    placed: dict[str, Placement] = {}
    result: list[Placement] = []

    # Recursion depth is bounded by the number of current entries in the area.
    def visit(i: str, under: str | None = None) -> None:
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


def old_rests_on_tree(s: Snapshot, d: Derived, entry_id: str) -> tuple[Branch, ...]:
    """Expand each dependency once, retaining shared targets as leaf references."""
    expanded = {entry_id}

    def branch(target: str, ancestors: frozenset[str]) -> Branch:
        seen = target in expanded
        expanded.add(target)
        return Branch(
            target,
            s.entries[target].title,
            d.status[target],
            () if seen else children(target, ancestors | {target}),
        )

    def children(ident: str, ancestors: frozenset[str]) -> tuple[Branch, ...]:
        entry = s.entries.get(ident)
        if entry is None:
            return ()
        return tuple(
            branch(target, ancestors)
            for target in dict.fromkeys(entry.rests_on)
            if target in s.entries and target not in ancestors
        )

    return children(entry_id, frozenset({entry_id}))


def old_branches(branches: tuple[Branch, ...]) -> str:
    seen: set[str] = set()

    def render(items: tuple[Branch, ...]) -> str:
        rows = []
        for item in items:
            repeated = item.id in seen
            seen.add(item.id)
            detail = " (see above)" if repeated else render(item.children)
            rows.append(f"<li>{link(item.id, item.title)} {e(item.status)}{detail}</li>")
        return "<ul>" + "".join(rows) + "</ul>" if rows else ""

    return render(branches)
