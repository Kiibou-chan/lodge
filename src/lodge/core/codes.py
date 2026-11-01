"""Code families and whole-token citations in level-1 text."""

import re
from datetime import UTC, datetime
from itertools import chain

from lodge.core.derive import Derived
from lodge.core.fields import CODE_PATTERN
from lodge.core.model import Record
from lodge.core.snapshot import Snapshot

_RUN = re.compile(r"[a-z0-9._-]+")
_ALNUM = frozenset("abcdefghijklmnopqrstuvwxyz0123456789")
_NEVER = datetime.min.replace(tzinfo=UTC)


def is_code_token(query: str) -> bool:
    """One token of the code grammar, without surrounding whitespace."""
    return CODE_PATTERN.fullmatch(query) is not None


def family(s: Snapshot, code: str) -> tuple[str, ...]:
    """Exact code first, then its dotted descendants by lower-cased code and ID."""
    wanted = code.lower()
    members = [
        (r.code.lower(), r.id)
        for r in chain[Record](s.decisions.values(), s.entries.values())
        if r.code and (r.code.lower() == wanted or r.code.lower().startswith(wanted + "."))
    ]
    return tuple(ident for _, ident in sorted(members, key=lambda p: (p[0] != wanted, *p)))


def code_tokens(text: str) -> frozenset[str]:
    """Each maximal run of [a-z0-9._-] in the lower-cased text, and each prefix
    of a run that ends before a dot not followed by a letter or digit.
    """
    tokens: set[str] = set()
    for run in _RUN.findall(text.lower()):
        tokens.add(run)
        tokens.update(
            run[:i]
            for i, char in enumerate(run)
            if char == "." and (i + 1 == len(run) or run[i + 1] not in _ALNUM)
        )
    return frozenset(tokens)


def cites(text: str, code: str) -> bool:
    """Whether level-1 text holds this whole code, allowing a sentence's final dot."""
    return code.lower() in code_tokens(text)


def citers(s: Snapshot, d: Derived, code: str) -> tuple[str, ...]:
    """Citing records outside the family, newest first by their level-1 date and ID."""
    excluded = set(family(s, code))
    wanted = code.lower()
    found = (
        r.id
        for r in chain[Record](s.decisions.values(), s.entries.values())
        if r.id not in excluded
        and (wanted in r.title.lower() or wanted in r.statement.lower())
        and cites(f"{r.title}\n{r.statement}", code)
    )

    def key(ident: str) -> tuple[datetime, str]:
        decision = s.decisions.get(ident)
        if decision is None:
            changing = d.changed_by.get(ident, ())
            decision = s.decisions[changing[0]] if changing else None
        return (datetime.fromisoformat(decision.date) if decision else _NEVER), ident

    return tuple(sorted(found, key=key, reverse=True))
