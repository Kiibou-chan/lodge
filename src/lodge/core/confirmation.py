"""The decisions an author can confirm, and the draft preserving her words."""

from collections.abc import Sequence

from lodge.core.derive import Derived, is_author, order_key
from lodge.core.model import Action, Scope
from lodge.core.snapshot import Snapshot
from lodge.core.yamlio import LINE_BREAKS_AND_TABS, quoted

VIEWER = "lodge viewer"
MINUTE_FORMAT = "%Y-%m-%d %H:%M"


def confirmable_ids(s: Snapshot, d: Derived) -> frozenset[str]:
    return frozenset(
        i
        for i, decision in s.decisions.items()
        if not is_author(decision) and d.status[i] == "current" and i not in d.confirmed_by
    )


def behind_area(s: Snapshot, d: Derived, area: str) -> tuple[str, ...]:
    """List confirmable creators and latest changers, including retired entries, oldest first."""
    entries = {i for i, entry in s.entries.items() if entry.area == area}
    found = {
        i
        for i in confirmable_ids(s, d)
        if any(c.entry in entries and c.action is Action.CREATE for c in s.decisions[i].changes)
        or any(d.changed_by.get(e, ())[:1] == (i,) for e in entries)
    }
    return tuple(sorted(found, key=lambda i: order_key(s.decisions[i])))


def confirmation_draft(
    confirms: Sequence[str],
    scope: Scope,
    words: str,
    when: str,
    area: str | None,
) -> str:
    """Preserve the author's words for one decision, or a list behind an area."""
    if area is None and len(confirms) != 1:
        raise ValueError("a confirmation without an area needs one decision")
    title = (
        f"Confirms {confirms[0]}" if area is None else f"Confirms the decisions behind area {area}"
    )
    if len(confirms) == 1:
        listed = confirms[0]
    elif len(confirms) == 2:
        listed = " and ".join(confirms)
    else:
        listed = ", ".join(confirms[:-1]) + f", and {confirms[-1]}"
    ids = ", ".join(quoted(i) for i in confirms)
    text = quoted(words, LINE_BREAKS_AND_TABS)
    return (
        f"---\nkind: decision\ntitle: {quoted(title)}\nscope: {scope.value}\n"
        f"decided_by: author\nconfirms: [{ids}]\n"
        f"quote: {{text: {text}, where: {quoted(VIEWER)}, when: {quoted(when)}}}\n---\n\n"
        f"The author confirms {listed}.\n\n## Reasoning\n\n{words}\n"
    )
