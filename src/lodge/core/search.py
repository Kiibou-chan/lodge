"""Finding records by ID, code, or words, and the decisions related to one."""

from collections.abc import Iterator

from lodge.core.codes import citers, family, is_code_token
from lodge.core.derive import Derived
from lodge.core.filters import Filters
from lodge.core.model import Decision, SpecEntry
from lodge.core.ranking import Candidate, Query, parse_query, passes, rank, score, when
from lodge.core.snapshot import Snapshot
from lodge.core.views import Level1, level1
from lodge.core.words import words as _words

_RELATED_SCORE = 2
_RELATED_WORDS = 2
_COMMON_FROM = 5
_NONE: frozenset[str] = frozenset()


class AmbiguousRef(LookupError):
    """A code that more than one record carries."""


def resolve(s: Snapshot, ref: str) -> str | None:
    """The ID that `ref` names, as an ID or a code, in any case."""
    wanted = ref.strip().lower()
    if wanted in s.decisions or wanted in s.entries:
        return wanted
    records: dict[str, Decision | SpecEntry] = {**s.decisions, **s.entries}
    coded = sorted(i for i, r in records.items() if r.code and r.code.lower() == wanted)
    if len(coded) > 1:
        raise AmbiguousRef(f"the code {ref} names more than one record: {', '.join(coded)}")
    return coded[0] if coded else None


def search(s: Snapshot, d: Derived, query: str, filters: Filters, limit: int = 20) -> list[str]:
    """An exact ID or code first, then by words in the title and statement, ties newest first.

    An empty query lists what the filters allow; a query without searchable words finds only
    the exact ID or code.
    """
    return search_counted(s, d, query, filters, limit)[0]


def search_counted(
    s: Snapshot, d: Derived, query: Query | str, filters: Filters, limit: int
) -> tuple[list[str], int]:
    """The first `limit` IDs of `search`, and how many matched in all."""
    q = parse_query(query) if isinstance(query, str) else query
    code = q.text.strip()
    members = family(s, code) if is_code_token(code) else ()
    citing = citers(s, d, code) if members else ()
    return rank(_candidates(s, d), q, filters, members, citing, limit)


def related(s: Snapshot, d: Derived, decision: Decision, limit: int = 3) -> list[str]:
    """Current decisions that share an entry with `decision`, then those that read like it."""
    views = sorted(
        (
            c
            for c in _candidates(s, d)
            if passes(c, Filters(kind="decision")) and c.view.id != decision.id
        ),
        key=lambda c: (when(c.view), c.view.id),
        reverse=True,
    )
    shared = {c.entry for c in decision.changes}
    sharing = [v for v in views if shared & {c.entry for c in s.decisions[v.view.id].changes}]
    common = _common_words(views)
    query = {w for w in _words(f"{decision.title} {decision.statement}") if not w.isdigit()}
    query -= common
    scored = [
        (v, score(v, frozenset(query))) for v in views if v not in sharing and _shared(v, query)
    ]
    ranked = sorted((p for p in scored if p[1] >= _RELATED_SCORE), key=lambda pair: -pair[1])
    return [v.view.id for v in [*sharing, *(v for v, _ in ranked)]][:limit]


def _shared(v: Candidate, query: set[str]) -> bool:
    """Whether `v` shares at least two distinct words with `query`."""
    return len(query & (v.title_words | v.statement_words)) >= _RELATED_WORDS


def _common_words(views: list[Candidate]) -> set[str]:
    """Words in the title or statement of more than a third of the decisions, once there are
    enough decisions for that to mean anything."""
    if len(views) < _COMMON_FROM:
        return set()
    counts: dict[str, int] = {}
    for v in views:
        for word in v.title_words | v.statement_words:
            counts[word] = counts.get(word, 0) + 1
    return {word for word, n in counts.items() if n * 3 > len(views)}


def _candidates(s: Snapshot, d: Derived) -> Iterator[Candidate]:
    for i in (*s.decisions, *s.entries):
        v = level1(s, d, i, _NONE)
        yield Candidate(
            v, frozenset(_areas(s, v)), frozenset(_words(v.title)), frozenset(_words(v.statement))
        )


def _areas(s: Snapshot, v: Level1) -> set[str]:
    """An entry's area; a decision's, the areas of the entries it changes."""
    if v.area is not None:
        return {v.area}
    return {s.entries[c.entry].area for c in s.decisions[v.id].changes if c.entry in s.entries}
