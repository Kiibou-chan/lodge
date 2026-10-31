"""Local doubt and question marks, and doubts carried through dependencies."""

from collections.abc import Mapping

from lodge.core.model import Action, Raises, ThreadState
from lodge.core.snapshot import Snapshot


def doubt_marks(
    s: Snapshot, changed_by: Mapping[str, tuple[str, ...]]
) -> dict[str, tuple[str, ...]]:
    doubts = _open(s, Raises.DOUBT)
    questions = _open(s, Raises.QUESTION)
    marks: dict[str, list[str]] = {}
    affected: set[str] = set()
    for ident in sorted(s.decisions.keys() | s.entries.keys()):
        local: list[str] = []
        if ident in doubts:
            local.append("in doubt")
        if ident in questions:
            local.append("question open")
        changed = False
        if ident in s.entries:
            for decision in sorted(doubts & s.decisions.keys()):
                created = any(
                    c.entry == ident and c.action is Action.CREATE
                    for c in s.decisions[decision].changes
                )
                if created or changed_by.get(ident, ())[:1] == (decision,):
                    changed = True
                    local.append(f"changed by {decision}, in doubt")
            if ident in doubts or changed:
                affected.add(ident)
        if local:
            marks[ident] = local
    _propagate(s, affected, marks)
    return {ident: tuple(values) for ident, values in marks.items()}


def _open(s: Snapshot, kind: Raises) -> set[str]:
    return {t.about for t in s.threads.values() if t.state is ThreadState.OPEN and t.raises is kind}


def _propagate(s: Snapshot, affected: set[str], marks: dict[str, list[str]]) -> None:
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
