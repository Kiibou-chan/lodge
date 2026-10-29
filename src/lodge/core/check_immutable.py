"""Check 5: a published decision is never rewritten; an agent decision's reasoning may shrink."""

from collections.abc import Iterator
from dataclasses import fields

from lodge.core.check_state import problem_at
from lodge.core.derive import is_author
from lodge.core.model import Decision, Problem
from lodge.core.snapshot import Snapshot

_APART = {"id", "reasoning"}
REMEDY = "; write a new decision that replaces or narrows it"


def check_immutable(published: Snapshot, after: Snapshot) -> tuple[list[Problem], list[str]]:
    """The problems, and the notes naming agent decisions whose reasoning shrank."""
    problems: list[Problem] = []
    notes: list[str] = []
    for decision_id in sorted(published.decisions.keys() & after.decisions.keys()):
        before, now = published.decisions[decision_id], after.decisions[decision_id]
        for name in _changed_fields(before, now):
            problems.append(
                problem_at(
                    after, decision_id, 5, f"{name} of a published decision was changed" + REMEDY
                )
            )
        if is_author(before):
            if before.reasoning != now.reasoning:
                message = "reasoning of a published author decision was changed" + REMEDY
                problems.append(problem_at(after, decision_id, 5, message))
            continue
        if before.reasoning.split() == now.reasoning.split():
            continue
        was, words = len(before.reasoning.split()), len(now.reasoning.split())
        if words < was:
            shrunk = f"reasoning of an agent decision shortened from {was} to {words} words"
            notes.append(f"{decision_id}: {shrunk}")
            continue
        elif words > was:
            message = (
                f"reasoning of a published agent decision grew from {was} to {words} words{REMEDY}"
            )
        else:
            message = "reasoning of a published agent decision was changed" + REMEDY
        problems.append(problem_at(after, decision_id, 5, message))
    return problems, notes


def _changed_fields(before: Decision, now: Decision) -> Iterator[str]:
    for item in fields(Decision):
        if item.name not in _APART and getattr(before, item.name) != getattr(now, item.name):
            yield item.name
