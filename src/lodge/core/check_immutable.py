"""Check 5: a published decision is never rewritten, its reasoning included."""

from collections.abc import Iterator
from dataclasses import fields

from lodge.core.check_state import problem_at
from lodge.core.derive import is_author
from lodge.core.model import Decision, Problem, ThreadState
from lodge.core.snapshot import Snapshot

_APART = {"id"}
REMEDY = "; a correction is a new decision that replaces it"
REASONING_REMEDY = "; a correction or a shorter reasoning is a new decision that replaces it"


def check_immutable(published: Snapshot, after: Snapshot) -> list[Problem]:
    """One problem for each field of a published decision that `after` changed."""
    problems: list[Problem] = []
    for decision_id in sorted(published.decisions.keys() & after.decisions.keys()):
        before, now = published.decisions[decision_id], after.decisions[decision_id]
        who = "author" if is_author(before) else "agent"
        for name in _changed_fields(before, now):
            if name == "reasoning":
                message = f"reasoning of a published {who} decision was changed{REASONING_REMEDY}"
            else:
                message = f"{name} of a published decision was changed{REMEDY}"
            problems.append(problem_at(after, decision_id, 5, message))
    for ident in sorted(published.threads.keys() & after.threads.keys()):
        old, new = published.threads[ident], after.threads[ident]
        messages: list[str] = []
        for name in ("about", "raises", "opened"):
            if getattr(old, name) != getattr(new, name):
                messages.append(f"{name} of a published thread was changed")
        if new.messages[: len(old.messages)] != old.messages:
            messages.append(
                "a published message was changed or removed; messages are only appended"
            )
        if old.state is ThreadState.CLOSED:
            if new.state is ThreadState.OPEN:
                messages.append("a closed thread was opened again")
            if len(new.messages) > len(old.messages):
                messages.append("a message was added after the thread was closed")
        elif new.state is ThreadState.CLOSED and len(new.messages) <= len(old.messages):
            messages.append("a thread was closed without a closing message")
        problems.extend(problem_at(after, ident, 5, message) for message in messages)
    return problems


def _changed_fields(before: Decision, now: Decision) -> Iterator[str]:
    for item in fields(Decision):
        if item.name not in _APART and getattr(before, item.name) != getattr(now, item.name):
            yield item.name
