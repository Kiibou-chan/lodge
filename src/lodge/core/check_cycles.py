"""Check 8: members of cycles in the entry dependency graph."""

from collections.abc import Iterator

from lodge.core.model import Problem
from lodge.core.snapshot import Snapshot


def check_cycles(s: Snapshot) -> Iterator[Problem]:
    def reachable(start: str) -> set[str]:
        found: set[str] = set()
        pending = list(s.entries[start].rests_on)
        while pending:
            target = pending.pop()
            if target in found or target not in s.entries:
                continue
            found.add(target)
            pending.extend(s.entries[target].rests_on)
        return found

    reach = {i: reachable(i) for i in s.entries}
    for i in sorted(reach):
        if i in reach[i]:
            others = sorted(t for t in reach[i] if t != i and i in reach[t])
            yield Problem(
                s.paths.get(i, ""),
                8,
                f"{i}: is in a cycle of rests_on links with {', '.join(others)}",
            )
