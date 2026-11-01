"""Queries and ranking over plain search candidates."""

import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime

from lodge.core.codes import is_code_token
from lodge.core.filters import Filters
from lodge.core.views import Level1
from lodge.core.words import words


@dataclass(frozen=True)
class Query:
    text: str
    phrase: bool
    words: frozenset[str]
    tokens: tuple[str, ...]


def parse_query(text: str, phrase: bool = False) -> Query:
    return Query(text, phrase, frozenset(words(text)), tuple(re.findall(r"[^\W_]+", text.lower())))


def needs_memory(q: Query) -> bool:
    return not q.words and (q.phrase or is_code_token(q.text.strip()))


@dataclass(frozen=True)
class Candidate:
    view: Level1
    areas: frozenset[str]
    title_words: frozenset[str]
    statement_words: frozenset[str]


def rank(
    candidates: Iterable[Candidate],
    query: Query,
    filters: Filters,
    family: Sequence[str],
    citing: Sequence[str],
    limit: int,
) -> tuple[list[str], int]:
    kept = {c.view.id: c for c in candidates if _passes(c, filters)}
    newest = sorted(kept, key=lambda i: (_when(kept[i].view), i), reverse=True)
    if not query.text.strip():
        return newest[:limit], len(newest)
    exact = query.text.strip().lower()
    found = [i for i in newest if i.lower() == exact]
    if is_code_token(query.text.strip()) and family:
        found.extend(i for i in (*family, *citing) if i in kept)
    else:
        found.extend(i for i in newest if (kept[i].view.code or "").lower() == exact)
    used = set(found)
    full: list[str] = []
    partial: list[str] = []
    if query.words:
        scored = sorted(newest, key=lambda i: -_score(kept[i], query.words))
        for ident in scored:
            if ident in used:
                continue
            candidate = kept[ident]
            held = candidate.title_words | candidate.statement_words
            if query.phrase:
                matches = _contains(candidate.view.title, query.tokens) or _contains(
                    candidate.view.statement, query.tokens
                )
            else:
                matches = query.words <= held
            if matches:
                full.append(ident)
            elif query.words & held and not query.words <= held:
                partial.append(ident)
    found = list(dict.fromkeys([*found, *full, *partial]))
    return found[:limit], len(found)


def _passes(c: Candidate, f: Filters) -> bool:
    v = c.view
    return (
        (f.kind is None or v.kind == f.kind)
        and (f.scope is None or v.scope == f.scope)
        and (f.status == "any" or v.status == f.status)
        and (f.area is None or f.area in c.areas)
        and (f.decided_by is None or v.decided_by == f.decided_by)
    )


def _when(v: Level1) -> datetime:
    return datetime.fromisoformat(v.date) if v.date else datetime.min.replace(tzinfo=UTC)


def _score(c: Candidate, query: frozenset[str]) -> int:
    return 3 * len(query & c.title_words) + len(query & c.statement_words)


def _contains(text: str, tokens: tuple[str, ...]) -> bool:
    held = tuple(re.findall(r"[^\W_]+", text.lower()))
    return any(held[i : i + len(tokens)] == tokens for i in range(len(held) - len(tokens) + 1))
