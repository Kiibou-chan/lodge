"""What lodge prints after an add: soft notes on the records just written, never a refusal."""

import re
from collections.abc import Iterator, Sequence
from dataclasses import dataclass

from lodge.core.derive import Derived, is_author
from lodge.core.model import Action, Decision, Record
from lodge.core.search import related
from lodge.core.settings import LengthGuidance
from lodge.core.snapshot import Snapshot

_CODE_SPAN = re.compile(r"```.*?```|`[^`\n]*`", re.DOTALL)
_ID = re.compile(r"\b[ds]-[0-9a-hjkmnp-tv-z]{6}\b")
_CODE = re.compile(r"\b[A-Za-z][A-Za-z0-9]*-\d+\b")
_DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}(?:T[0-9:.]+(?:Z|[+-][0-9:]+)?)?")
_TEXT = (Action.CREATE, Action.EDIT)
_NUMBER = re.compile(r"\b\d+(?:[.,]\d+)*(?:\s?%)?")


@dataclass(frozen=True)
class Feedback:
    record_id: str
    message: str


def feedback(
    added: Sequence[Record], after: Snapshot, d: Derived, length: LengthGuidance
) -> list[Feedback]:
    """The notes on each added record, in the order of `added`."""
    return [
        Feedback(record.id, message)
        for record in added
        for message in _messages(record, after, d, length)
    ]


def _messages(record: Record, after: Snapshot, d: Derived, length: LengthGuidance) -> Iterator[str]:
    if len(record.title) > length.title_chars:
        yield (
            f"the title is {len(record.title)} characters; "
            f"guidance is {length.title_chars} or fewer, on one line"
        )
    if isinstance(record, Decision):
        yield from _decision_messages(record, after, d, length)
    else:
        words, limit = len(record.statement.split()), length.spec_statement_words
        if words > limit:
            yield (
                f"the statement is {words} words; "
                f"guidance is {limit} or fewer for a specification entry"
            )


def _decision_messages(
    decision: Decision, after: Snapshot, d: Derived, length: LengthGuidance
) -> Iterator[str]:
    words, limit = len(decision.statement.split()), length.decision_statement_words
    if words > limit:
        yield f"the statement is {words} words; guidance is {limit} or fewer for a decision"
    reasoning = len(decision.reasoning.split())
    if reasoning > length.reasoning_words:
        yield f"the reasoning is {reasoning} words; guidance is {length.reasoning_words} or fewer"
    if not decision.replaces and not decision.narrows:
        yield from _related_message(decision, after, d)
    if not decision.numbers:
        yield from _number_message(decision, after)
    yield from _already_replaced_message(decision, d)
    yield from _edit_back_message(decision, after, d)
    yield from _revival_message(decision, after, d)
    if decision.id in d.awaiting_author:
        yield (
            "this decision will wait for the author: it takes effect at once, and a later "
            "author decision that confirms or replaces it clears the flag"
        )


def _already_replaced_message(decision: Decision, d: Derived) -> Iterator[str]:
    """The decisions this one replaces that another decision has replaced already."""
    for target in decision.replaces:
        others = [i for i in d.replaced_by.get(target, ()) if i != decision.id]
        if others:
            yield f"{target} is already replaced by {_listed(others)}"


def _edit_back_message(decision: Decision, after: Snapshot, d: Derived) -> Iterator[str]:
    """An author decision replacing an agent edit that still stands asks whether to edit it back."""
    if not is_author(decision):
        return
    own = {c.entry for c in decision.changes}
    for target in decision.replaces:
        replaced = after.decisions.get(target)
        if replaced is None or is_author(replaced):
            continue
        edited = (c.entry for c in replaced.changes if c.action is Action.EDIT)
        for entry in sorted(dict.fromkeys(edited)):
            if entry not in own and _newest_text_change(entry, after, d) == replaced.id:
                yield (
                    f"it replaces {replaced.id}, whose edit of {entry} is still the latest edit "
                    f"of that entry; does {decision.id} edit {entry} back? "
                    f"If so, add an edit draft of {entry} and list it in changes with action edit"
                )


def _newest_text_change(entry: str, after: Snapshot, d: Derived) -> str | None:
    """The decision of the entry's newest create or edit, passing over retirements and revivals."""
    for i in d.changed_by.get(entry, ()):
        decision = after.decisions[i]
        if any(c.entry == entry and c.action in _TEXT for c in decision.changes):
            return i
    return None


def _revival_message(decision: Decision, after: Snapshot, d: Derived) -> Iterator[str]:
    """The entries that this decision makes current again by replacing their last retirements."""
    own = {c.entry for c in decision.changes}
    for entry in d.revived.get(decision.id, ()):
        if entry in own or d.status.get(entry) != "current":
            continue
        retirements = [
            t
            for t in decision.replaces
            if t in after.decisions
            and d.replaced_by.get(t, ())[-1:] == (decision.id,)
            and any(
                c.entry == entry and c.action is Action.RETIRE for c in after.decisions[t].changes
            )
        ]
        if not retirements:
            continue
        many = len(retirements) > 1
        yield (
            f"it replaces {_listed(retirements)}, the last standing "
            f"{'retirements' if many else 'retirement'} of {entry}, so {entry} "
            f"becomes current again; to keep it retired, list it in changes with action retire"
        )


def _listed(items: Sequence[str]) -> str:
    if len(items) < 3:
        return " and ".join(items)
    return f"{', '.join(items[:-1])}, and {items[-1]}"


def _related_message(decision: Decision, after: Snapshot, d: Derived) -> Iterator[str]:
    found = related(after, d, decision)
    if not found:
        return
    listed = ", ".join(f"{i} ({after.decisions[i].title})" for i in found)
    if len(found) > 1:
        these, target = "these current decisions look", "any of them"
    else:
        these, target = "this current decision looks", found[0]
    yield (
        f"it replaces and narrows nothing, but {these} related: {listed}; "
        f"does {decision.id} replace or narrow {target}? "
        "If so, set replaces or narrows in the draft before adding it"
    )


def _number_message(decision: Decision, after: Snapshot) -> Iterator[str]:
    records: list[Record] = [*after.decisions.values(), *after.entries.values()]
    codes = {r.code.lower() for r in records if r.code}
    found = list(dict.fromkeys(_numbers(f"{decision.statement}\n{decision.reasoning}", codes)))
    if found:
        noun = "the numbers" if len(found) > 1 else "the number"
        yield (
            f"the text holds {noun} {', '.join(found)} without a numbers handle; before adding "
            'the draft, give each one as `numbers: [{value: "…", handle: "…"}]`, the handle a '
            "record and key or a runnable command"
        )


def _numbers(text: str, codes: set[str]) -> list[str]:
    """The number tokens outside backticks, leaving out IDs, ISO dates, and the codes in `codes`."""
    for hidden in (_CODE_SPAN, _DATE, _ID):
        text = hidden.sub(" ", text)
    text = _CODE.sub(lambda m: " " if m.group().lower() in codes else m.group(), text)
    return [token.strip() for token in _NUMBER.findall(text)]
