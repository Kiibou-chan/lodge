import pytest
from builders import at, decision, entry, snapshot_of

from lodge.core import (
    Action,
    AmbiguousRef,
    Change,
    Filters,
    Scope,
    derive,
    related,
    resolve,
    search,
    search_counted,
)


def test_resolve_case_insensitive() -> None:
    a = decision(id="d-aaaaaa", code="ITEM-1")
    s = snapshot_of(a, entry(id="s-bbbbbb", code="SPEC-2"))
    assert resolve(s, "D-AAAAAA") == "d-aaaaaa"
    assert resolve(s, "item-1") == "d-aaaaaa"
    assert resolve(s, "Spec-2") == "s-bbbbbb"
    assert resolve(s, "s-bbbbbb") == "s-bbbbbb"
    assert resolve(s, "nothing") is None


def test_resolve_ambiguous_code_raises() -> None:
    s = snapshot_of(decision(id="d-aaaaaa", code="ITEM-1"), entry(id="s-bbbbbb", code="ITEM-1"))
    with pytest.raises(AmbiguousRef, match="d-aaaaaa, s-bbbbbb"):
        resolve(s, "item-1")


def test_search_title_over_statement() -> None:
    in_statement = decision(id="d-aaaaaa", title="Other", statement="Retry the upload.", date=at(5))
    in_title = decision(id="d-bbbbbb", title="Retry upload", statement="Nothing.", date=at(1))
    s = snapshot_of(in_statement, in_title)
    assert search(s, derive(s), "retry", Filters()) == ["d-bbbbbb", "d-aaaaaa"]


def test_search_exact_id_or_code_first_then_ties_newest_first() -> None:
    older = decision(id="d-aaaaaa", title="Cache", date=at(1))
    newer = decision(id="d-bbbbbb", title="Cache", date=at(9))
    coded = decision(id="d-cccccc", title="Unrelated", code="ITEM-1", date=at(0))
    s = snapshot_of(older, newer, coded)
    assert search(s, derive(s), "cache", Filters()) == ["d-bbbbbb", "d-aaaaaa"]
    assert search(s, derive(s), "item-1 cache", Filters()) == ["d-bbbbbb", "d-aaaaaa"]
    assert search(s, derive(s), "ITEM-1", Filters()) == ["d-cccccc"]
    assert search(s, derive(s), "d-AAAAAA", Filters()) == ["d-aaaaaa"]


def test_search_words_split_on_non_letters_and_limit() -> None:
    ds = [decision(id=f"d-aaaaa{c}", title="Cache-key", date=at(i)) for i, c in enumerate("abc")]
    s = snapshot_of(*ds)
    assert search(s, derive(s), "KEY!", Filters(), limit=2) == ["d-aaaaac", "d-aaaaab"]


def test_search_empty_query_lists_what_the_filters_allow() -> None:
    a = decision(id="d-aaaaaa", date=at(1))
    b = decision(id="d-bbbbbb", date=at(2))
    s = snapshot_of(a, b)
    assert search(s, derive(s), "", Filters()) == ["d-bbbbbb", "d-aaaaaa"]


def test_search_each_filter() -> None:
    spec = entry(id="s-aaaaaa", title="Cache", area="storage")
    prod = decision(id="d-aaaaaa", title="Cache", changes=(Change("s-aaaaaa", Action.CREATE),))
    proc = decision(id="d-bbbbbb", title="Cache", scope=Scope.PROCESS, decided_by="author")
    s = snapshot_of(spec, prod, proc)
    d = derive(s)

    def ids(**kw: object) -> list[str]:
        return sorted(search(s, d, "cache", Filters(**kw)))  # type: ignore[arg-type]

    assert ids() == ["d-aaaaaa", "d-bbbbbb", "s-aaaaaa"]
    assert ids(kind="spec") == ["s-aaaaaa"]
    assert ids(kind="decision") == ["d-aaaaaa", "d-bbbbbb"]
    assert ids(scope=Scope.PROCESS) == ["d-bbbbbb"]
    assert ids(area="storage") == ["d-aaaaaa", "s-aaaaaa"]
    assert ids(area="other") == []
    assert ids(decided_by="author") == ["d-bbbbbb"]
    assert ids(decided_by="coordinator") == ["d-aaaaaa", "s-aaaaaa"]


def test_search_hides_replaced_unless_asked() -> None:
    old = decision(id="d-aaaaaa", title="Cache", date=at(0))
    new = decision(id="d-bbbbbb", title="Cache", date=at(1), replaces=("d-aaaaaa",))
    spec = entry(id="s-aaaaaa", title="Cache")
    kill = decision(
        id="d-cccccc", title="Other", date=at(2), changes=(Change("s-aaaaaa", Action.RETIRE),)
    )
    s = snapshot_of(old, new, spec, kill)
    d = derive(s)
    assert search(s, d, "cache", Filters()) == ["d-bbbbbb"]
    assert search(s, d, "cache", Filters(status="replaced")) == ["d-aaaaaa"]
    assert search(s, d, "cache", Filters(status="retired")) == ["s-aaaaaa"]
    assert search(s, d, "cache", Filters(status="any")) == ["s-aaaaaa", "d-bbbbbb", "d-aaaaaa"]


def test_related_shared_entry_first() -> None:
    spec = entry(id="s-aaaaaa")
    change = (Change("s-aaaaaa", Action.EDIT),)
    this = decision(id="d-aaaaaa", title="Cache the sessions", statement="Hold.", changes=change)
    shares = decision(id="d-bbbbbb", title="Unlike", changes=change, date=at(1))
    gone = decision(id="d-cccccc", title="Unlike", changes=change, date=at(2))
    words = decision(id="d-dddddd", title="Cache sessions", statement="Hold.", date=at(3))
    weak = decision(id="d-eeeeee", title="Other", statement="Sessions.", date=at(4))
    last = decision(id="d-ffffff", title="Last", replaces=("d-cccccc",), date=at(5))
    s = snapshot_of(spec, this, shares, gone, words, weak, last)
    d = derive(s)
    assert related(s, d, this, limit=10) == ["d-bbbbbb", "d-dddddd"]
    assert related(s, d, this, limit=1) == ["d-bbbbbb"]


def test_search_without_words_returns_exact_match_only() -> None:
    a = decision(id="d-aaaaaa", title="Cache", statement="Holds 42 items.", code="ITEM-1")
    b = decision(id="d-bbbbbb", title="Cache", statement="Holds few.", date=at(1))
    s = snapshot_of(a, b)
    d = derive(s)
    assert search(s, d, "%", Filters()) == []
    assert search(s, d, "the of", Filters()) == []
    assert search(s, d, "  ", Filters()) == ["d-bbbbbb", "d-aaaaaa"]
    assert search(s, d, "42", Filters()) == ["d-aaaaaa"]


def test_search_ties_larger_id_first() -> None:
    a, b = decision(id="d-aaaaaa", title="Cache"), decision(id="d-bbbbbb", title="Cache")
    s = snapshot_of(a, b)
    assert search(s, derive(s), "cache", Filters()) == ["d-bbbbbb", "d-aaaaaa"]
    assert search(s, derive(s), "", Filters()) == ["d-bbbbbb", "d-aaaaaa"]


def test_search_ignores_function_words() -> None:
    a = decision(id="d-aaaaaa", title="The cache", statement="It is small.")
    b = decision(id="d-bbbbbb", title="The queue", statement="It is long.")
    s = snapshot_of(a, b)
    assert search(s, derive(s), "the cache is", Filters()) == ["d-aaaaaa"]


def test_related_ignores_function_words_and_numbers() -> None:
    this = decision(id="d-aaaaaa", title="Cache", statement="The cache is small on 2026 10.")
    other = decision(id="d-bbbbbb", title="Queue", statement="The queue is long on 2026 10.")
    s = snapshot_of(this, other)
    assert related(s, derive(s), this) == []


def test_search_area_matches_decisions_changing_its_entries() -> None:
    spec = entry(id="s-aaaaaa", area="storage", title="Other")
    change = decision(id="d-aaaaaa", title="Cache", changes=(Change("s-aaaaaa", Action.CREATE),))
    plain = decision(id="d-bbbbbb", title="Cache")
    s = snapshot_of(spec, change, plain)
    assert search(s, derive(s), "cache", Filters(area="storage")) == ["d-aaaaaa"]


def test_related_needs_two_shared_words_not_one() -> None:
    draft = decision(id="d-aaaaaa", title="Records name the project they belong to", date=at(9))
    one = [
        decision(id="d-bbbbbb", title="Records", statement="Kept.", date=at(1)),
        decision(id="d-cccccc", title="Project", statement="Kept.", date=at(2)),
        decision(id="d-dddddd", title="Other", statement="They belong.", date=at(3)),
    ]
    two = decision(id="d-eeeeee", title="Records belong", statement="Kept.", date=at(4))
    s = snapshot_of(draft, *one, two)
    assert related(s, derive(s), draft) == ["d-eeeeee"]


def test_related_ignores_a_word_most_decisions_carry() -> None:
    names = ("alpha", "beta", "gamma", "delta", "epsilon")
    common = [
        decision(id=f"d-aaaaa{c}", title=f"Lodge {name}", statement="Records held.", date=at(i))
        for i, (c, name) in enumerate(zip("bcdef", names, strict=True))
    ]
    draft = decision(
        id="d-aaaaaa", title="Lodge zeta", statement="Records held; zeta holds it.", date=at(9)
    )
    s = snapshot_of(draft, *common)
    assert related(s, derive(s), draft) == []
    twin = decision(id="d-aaaaag", title="Zeta holds", statement="Held.", date=at(8))
    s = snapshot_of(draft, twin, *common)
    assert related(s, derive(s), draft) == ["d-aaaaag"]


def test_search_reports_how_many_matched_beyond_the_limit() -> None:
    ds = [decision(id=f"d-aaaaa{c}", title="Cache", date=at(i)) for i, c in enumerate("abcde")]
    s = snapshot_of(*ds)
    ids, total = search_counted(s, derive(s), "cache", Filters(), limit=2)
    assert (ids, total) == (["d-aaaaae", "d-aaaaad"], 5)
    assert search_counted(s, derive(s), "", Filters(), limit=2)[1] == 5
