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
    changed_doubts: dict[str, set[str]] = {}
    for decision in doubts & s.decisions.keys():
        for change in s.decisions[decision].changes:
            if change.action is Action.CREATE:
                changed_doubts.setdefault(change.entry, set()).add(decision)
    for ident, changes in changed_by.items():
        if changes and changes[0] in doubts:
            changed_doubts.setdefault(ident, set()).add(changes[0])
    for ident in sorted(s.decisions.keys() | s.entries.keys()):
        local: list[str] = []
        if ident in doubts:
            local.append("in doubt")
        if ident in questions:
            local.append("question open")
        if ident in s.entries:
            changed = changed_doubts.get(ident, set())
            local.extend(f"changed by {decision}, in doubt" for decision in sorted(changed))
            if ident in doubts or changed:
                affected.add(ident)
        if local:
            marks[ident] = local
    _propagate(s, affected, marks)
    return {ident: tuple(values) for ident, values in marks.items()}


def _open(s: Snapshot, kind: Raises) -> set[str]:
    return {t.about for t in s.threads.values() if t.state is ThreadState.OPEN and t.raises is kind}


def _propagate(s: Snapshot, affected: set[str], marks: dict[str, list[str]]) -> None:
    reverse: dict[str, list[str]] = {}
    for ident, entry in s.entries.items():
        for target in entry.rests_on:
            reverse.setdefault(target, []).append(ident)
    reached: dict[str, set[str]] = {}
    for source in affected:
        seen = {source}
        pending = list(reverse.get(source, ()))
        while pending:
            ident = pending.pop()
            if ident in seen:
                continue
            seen.add(ident)
            reached.setdefault(ident, set()).add(source)
            pending.extend(reverse.get(ident, ()))
    for ident in sorted(reached):
        marks.setdefault(ident, []).extend(
            f"rests on {t}, in doubt" for t in sorted(reached[ident])
        )
