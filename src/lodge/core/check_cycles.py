"""Check 8: members of cycles in the entry dependency graph."""

from collections.abc import Iterator

from lodge.core.model import Problem
from lodge.core.snapshot import Snapshot


def check_cycles(s: Snapshot) -> Iterator[Problem]:
    """Iterative Tarjan traversal; only non-singleton components belong to check 8."""
    indices: dict[str, int] = {}
    low: dict[str, int] = {}
    active: set[str] = set()
    pending: list[str] = []
    components: dict[str, tuple[str, ...]] = {}
    for root in s.entries:
        if root in indices:
            continue
        indices[root] = low[root] = len(indices)
        active.add(root)
        pending.append(root)
        stack = [(root, iter(s.entries[root].rests_on))]
        while stack:
            ident, targets = stack[-1]
            target = next(targets, None)
            if target is not None:
                if target not in s.entries:
                    continue
                if target not in indices:
                    indices[target] = low[target] = len(indices)
                    active.add(target)
                    pending.append(target)
                    stack.append((target, iter(s.entries[target].rests_on)))
                elif target in active:
                    low[ident] = min(low[ident], indices[target])
                continue
            stack.pop()
            if stack:
                parent = stack[-1][0]
                low[parent] = min(low[parent], low[ident])
            if low[ident] == indices[ident]:
                group = []
                while True:
                    member = pending.pop()
                    active.remove(member)
                    group.append(member)
                    if member == ident:
                        break
                if len(group) > 1:
                    members = tuple(sorted(group))
                    components.update((member, members) for member in members)
    for ident in sorted(components):
        others = ", ".join(t for t in components[ident] if t != ident)
        yield Problem(
            s.paths.get(ident, ""), 8, f"{ident}: is in a cycle of rests_on links with {others}"
        )
