"""Local doubt and question marks, and doubts carried through dependencies."""

from collections.abc import Mapping

from lodge.core.model import Action, Raises, ThreadState
from lodge.core.snapshot import Snapshot


def doubt_marks(
    s: Snapshot, changed_by: Mapping[str, tuple[str, ...]]
) -> dict[str, tuple[str, ...]]:
    doubts = {
        t.about
        for t in s.threads.values()
        if t.state is ThreadState.OPEN and t.raises is Raises.DOUBT
    }
    questions = {
        t.about
        for t in s.threads.values()
        if t.state is ThreadState.OPEN and t.raises is Raises.QUESTION
    }
    marks: dict[str, list[str]] = {}
    affected: set[str] = set()
    for ident in sorted(s.decisions.keys() | s.entries.keys()):
        local: list[str] = []
        if ident in doubts:
            local.append("in doubt")
        if ident in questions:
            local.append("question open")
        if ident in s.entries:
            for decision in sorted(doubts & s.decisions.keys()):
                created = any(
                    c.entry == ident and c.action is Action.CREATE
                    for c in s.decisions[decision].changes
                )
                if created or changed_by.get(ident, ())[:1] == (decision,):
                    local.append(f"changed by {decision}, in doubt")
            if ident in doubts or any(m.startswith("changed by ") for m in local):
                affected.add(ident)
        if local:
            marks[ident] = local
    for ident, entry in sorted(s.entries.items()):
        seen = {ident}
        pending = list(entry.rests_on)
        reached: set[str] = set()
        while pending:
            target = pending.pop()
            if target in seen:
                continue
            seen.add(target)
            if target in affected:
                reached.add(target)
            if target in s.entries:
                pending.extend(s.entries[target].rests_on)
        if reached:
            marks.setdefault(ident, []).extend(f"rests on {t}, in doubt" for t in sorted(reached))
    return {ident: tuple(values) for ident, values in marks.items()}
