"""Search ranking and the candidate subset required by the future index."""

from dataclasses import replace
from random import Random

from builders import at, decision, entry, snapshot_of

from lodge.core import (
    Action,
    Candidate,
    Change,
    Filters,
    Query,
    Scope,
    Snapshot,
    citers,
    derive,
    family,
    level1,
    needs_memory,
    parse_query,
    rank,
    search_counted,
)
from lodge.core.words import tokens, words


def candidates(s: Snapshot) -> list[Candidate]:
    d = derive(s)
    result = []
    for ident in [*s.decisions, *s.entries]:
        v = level1(s, d, ident, frozenset())
        areas = (
            {v.area}
            if v.area
            else {
                s.entries[c.entry].area for c in s.decisions[ident].changes if c.entry in s.entries
            }
        )
        result.append(
            Candidate(
                v, frozenset(areas), parse_query(v.title).words, parse_query(v.statement).words
            )
        )
    return result


def ranked(
    s: Snapshot, text: str, phrase: bool = False, filters: Filters | None = None
) -> list[str]:
    q = parse_query(text, phrase)
    return rank(
        candidates(s), q, filters or Filters(), family(s, text), citers(s, derive(s), text), 1000
    )[0]


def test_exact_id_first() -> None:
    s = snapshot_of(
        decision(id="d-aaaaaa", title="Other", date=at(0)),
        decision(id="d-bbbbbb", title="d-aaaaaa", date=at(9)),
    )
    assert ranked(s, "D-AAAAAA") == ["d-aaaaaa", "d-bbbbbb"]


def test_code_family_then_citers_then_words() -> None:
    s = snapshot_of(
        decision(id="d-aaaaaa", code="BERTH-1", date=at(0)),
        decision(id="d-bbbbbb", code="BERTH-1.why", date=at(1)),
        decision(id="d-cccccc", statement="See BERTH-1.", date=at(2)),
        decision(id="d-dddddd", title="Berth 1 berth", date=at(9)),
    )
    assert ranked(s, "berth-1") == ["d-aaaaaa", "d-bbbbbb", "d-cccccc", "d-dddddd"]
    assert search_counted(s, derive(s), parse_query("berth-1"), Filters(), 20)[0] == ranked(
        s, "berth-1"
    )
    assert ranked(s, "berth")[:2] == ["d-dddddd", "d-cccccc"]


def test_code_without_family_ranks_as_words() -> None:
    s = snapshot_of(
        decision(id="d-aaaaaa", title="Crane 42"),
        decision(id="d-bbbbbb", title="Crane", date=at(9)),
    )
    assert ranked(s, "CRANE-42") == ["d-aaaaaa", "d-bbbbbb"]


def test_phrase_is_a_run_of_whole_words() -> None:
    s = snapshot_of(
        decision(id="d-aaaaaa", title="point settled", date=at(9)),
        decision(id="d-bbbbbb", title="unsettled points", date=at(8)),
        decision(id="d-cccccc", statement="settled, point.", date=at(0)),
        decision(id="d-dddddd", title="settled", statement="point", date=at(7)),
    )
    assert ranked(s, "settled point", True) == ["d-cccccc", "d-aaaaaa", "d-dddddd"]


def test_phrase_keeps_function_words() -> None:
    s = snapshot_of(
        decision(id="d-aaaaaa", title="of the berth"),
        decision(id="d-bbbbbb", title="berth of the", date=at(9)),
    )
    assert ranked(s, "of the berth", True) == ["d-aaaaaa", "d-bbbbbb"]
    assert parse_query("Of, the berth!", True).tokens == ("of", "the", "berth")


def test_needs_memory_cases() -> None:
    assert needs_memory(parse_query("of the", True))
    assert needs_memory(parse_query("NO-ONE"))
    assert needs_memory(parse_query("A"))
    assert not needs_memory(parse_query("the berth", True))
    assert not needs_memory(parse_query("of the"))


def test_function_words_only_finds_id_and_code_only() -> None:
    s = snapshot_of(
        decision(id="d-aaaaaa", title="the", code="OF THE"),
        decision(id="d-bbbbbb", title="the", code="OF"),
    )
    assert ranked(s, "of the") == ["d-aaaaaa"]
    assert ranked(s, "of") == ["d-bbbbbb"]
    assert ranked(s, "the") == []
    assert ranked(s, "of the", True) == ["d-aaaaaa"]


def test_all_words_before_some_words() -> None:
    s = snapshot_of(
        decision(id="d-aaaaaa", title="berth crane", statement="tide"),
        decision(id="d-bbbbbb", title="berth crane", date=at(9)),
        decision(id="d-cccccc", title="Other", statement="berth crane tide"),
    )
    assert ranked(s, "berth crane tide") == ["d-aaaaaa", "d-cccccc", "d-bbbbbb"]


def test_ties_newest_first() -> None:
    s = snapshot_of(*(decision(id=f"d-{n:06d}", title="berth", date=at(n // 2)) for n in range(4)))
    expected = ["d-000003", "d-000002", "d-000001", "d-000000"]
    assert ranked(s, "berth") == expected
    assert ranked(s, "") == expected


def test_filters_apply_to_family_and_citers() -> None:
    s = snapshot_of(
        entry(id="s-aaaaaa", code="X-1", area="port"),
        decision(id="d-aaaaaa", code="X-1.why", decided_by="author", scope=Scope.PROCESS),
        decision(id="d-bbbbbb", title="See X-1", changes=(Change("s-aaaaaa", Action.CREATE),)),
        decision(id="d-cccccc", title="See X-1", replaces=("d-aaaaaa",)),
    )
    assert ranked(s, "X-1", filters=Filters(kind="spec")) == ["s-aaaaaa"]
    assert ranked(s, "X-1", filters=Filters(area="port")) == ["s-aaaaaa", "d-bbbbbb"]
    assert ranked(s, "X-1", filters=Filters(scope=Scope.PROCESS)) == []
    assert ranked(s, "X-1", filters=Filters(status="replaced", decided_by="author")) == ["d-aaaaaa"]
    assert ranked(s, "X-1", filters=Filters(status="any"))[:2] == ["s-aaaaaa", "d-aaaaaa"]


def test_rank_over_candidates_equals_rank_over_all() -> None:
    rng = Random(608)
    vocabulary = ["berth", "crane", "tide", "of", "the", "cargo", "NO-ONE", "A", "PORT-1"]
    s = snapshot_of(
        *(
            decision(
                id=f"d-{n:06d}",
                date=at(n % 60),
                title=" ".join(rng.choices(vocabulary, k=3)),
                statement=" ".join(rng.choices(vocabulary, k=5)),
                decided_by="author" if n % 2 else "agent",
                changes=(Change(f"s-{n % 12:06d}", Action.EDIT),),
                code=("PORT-1" if n == 0 else f"PORT-1.{n}" if n < 10 else None),
            )
            for n in range(400)
        ),
        *(entry(id=f"s-{n:06d}", area=f"port-{n % 3}", title="crane berth") for n in range(12)),
        decision(id="D-ABCDEF", title="berth crane", code="ORPHAN.why"),
        decision(id="d-abcdef", title="crane berth", replaces=("d-000000",)),
    )
    all_candidates = candidates(s)
    d = derive(s)
    for step in range(300):
        text = (
            rng.choice([*vocabulary, "PORT", "of the", "", "d-000001", "D-ABCDEF", "ORPHAN"])
            if step % 3
            else " ".join(rng.choices(vocabulary, k=2))
        )
        q = parse_query(text, step % 4 == 0)
        if needs_memory(q):
            continue
        f = rng.choice(
            [
                Filters(),
                Filters(status="any"),
                Filters(kind="spec"),
                Filters(decided_by="author"),
                Filters(area="port-1"),
                Filters(status="replaced"),
            ]
        )
        fam, citing = family(s, text), citers(s, d, text)
        subset = [
            c
            for c in all_candidates
            if not text.strip()
            or c.view.id.lower() == text.strip().lower()
            or c.view.id in (*fam, *citing)
            or q.words & (c.title_words | c.statement_words)
        ]
        assert rank(subset, q, f, fam, citing, 13) == rank(all_candidates, q, f, fam, citing, 13), (
            step,
            q,
        )
        assert search_counted(s, d, q, f, 13) == rank(all_candidates, q, f, fam, citing, 13)
    # Explicitly cover reversed phrase words under a non-empty area filter.
    q = parse_query("berth crane", True)
    f = Filters(kind="spec", area="port-1")
    subset = [c for c in all_candidates if q.words & (c.title_words | c.statement_words)]
    assert rank(subset, q, f, (), (), 100) == rank(all_candidates, q, f, (), (), 100)
    assert rank(subset, q, f, (), (), 100)[1] == 4
    # Candidate word sets, rather than recomputed text, determine scores.
    q = Query("cargo", False, frozenset({"cargo"}), ("cargo",))
    c = replace(all_candidates[1], title_words=q.words, statement_words=frozenset())
    assert rank([c], q, Filters(), (), (), 1) == ([c.view.id], 1)


def test_phrase_and_words_share_tokens() -> None:
    text = "Of, İSland_berth! Straße 42"
    assert tokens(text) == ("of", "i", "sland", "berth", "straße", "42")
    assert parse_query(text, True).tokens == tokens(text)
    assert words(text) == set(tokens(text)) - {"of", "i"}
