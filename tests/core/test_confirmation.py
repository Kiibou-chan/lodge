import pytest
from builders import at, decision, entry, snapshot_of

from lodge.core import (
    Action,
    Change,
    Decision,
    Draft,
    Scope,
    behind_area,
    confirmable_ids,
    confirmation_draft,
    derive,
    parse_draft,
    record_from_draft,
)


def test_confirmable_ids_skip_author_confirmed_and_replaced() -> None:
    s = snapshot_of(
        decision(id="d-aaaaaa"),
        decision(id="d-bbbbbb"),
        decision(id="d-cccccc"),
        decision(id="d-dddddd", decided_by="author", confirms=("d-aaaaaa",)),
        decision(id="d-eeeeee", replaces=("d-bbbbbb",)),
    )
    assert confirmable_ids(s, derive(s)) == frozenset({"d-cccccc", "d-eeeeee"})


def test_behind_area_lists_creators_and_last_changers_oldest_first() -> None:
    s = snapshot_of(
        entry(id="s-aaaaaa"),
        decision(id="d-aaaaaa", date=at(2), changes=(Change("s-aaaaaa", Action.EDIT),)),
        decision(id="d-cccccc", date=at(0), changes=(Change("s-aaaaaa", Action.CREATE),)),
        decision(id="d-bbbbbb", date=at(1), changes=(Change("s-aaaaaa", Action.EDIT),)),
    )
    assert behind_area(s, derive(s), "storage") == ("d-cccccc", "d-aaaaaa")


def test_behind_area_includes_the_retirer_of_a_retired_entry() -> None:
    s = snapshot_of(
        entry(id="s-aaaaaa"),
        decision(
            id="d-aaaaaa",
            changes=(Change("s-aaaaaa", Action.RETIRE),),
        ),
    )
    assert behind_area(s, derive(s), "storage") == ("d-aaaaaa",)


def test_confirmation_draft_single() -> None:
    words = 'Read: "yes".\nStill a caveat.'
    draft = parse_draft(
        "viewer",
        confirmation_draft(
            ["d-aaaaaa"],
            Scope.PRODUCT,
            words,
            "2026-10-29 09:30",
            None,
        ),
    )
    assert isinstance(draft, Draft)
    made = record_from_draft(draft, "d-bbbbbb", at(1), None)
    assert isinstance(made, Decision)
    assert made.title == "Confirms d-aaaaaa"
    assert made.statement == "The author confirms d-aaaaaa."
    assert made.reasoning == words
    assert made.quote and made.quote.where == "lodge viewer"


def test_confirmation_draft_area_lists_with_the_oxford_comma() -> None:
    draft = parse_draft(
        "viewer",
        confirmation_draft(
            ["d-aaaaaa", "d-bbbbbb", "d-cccccc"],
            Scope.PROCESS,
            "Read.",
            "now",
            "storage",
        ),
    )
    assert isinstance(draft, Draft)
    made = record_from_draft(draft, "d-dddddd", at(1), None)
    assert isinstance(made, Decision)
    assert made.title == "Confirms the decisions behind area storage"
    assert made.statement == "The author confirms d-aaaaaa, d-bbbbbb, and d-cccccc."


def test_behind_area_same_date_uses_id_tie_break() -> None:
    s = snapshot_of(
        entry(id="s-aaaaaa"),
        decision(id="d-cccccc", date=at(0), changes=(Change("s-aaaaaa", Action.CREATE),)),
        decision(id="d-aaaaaa", date=at(0), changes=(Change("s-aaaaaa", Action.CREATE),)),
    )
    assert behind_area(s, derive(s), "storage") == ("d-aaaaaa", "d-cccccc")


def test_confirmation_draft_two_uses_and() -> None:
    draft = parse_draft(
        "viewer",
        confirmation_draft(["d-aaaaaa", "d-bbbbbb"], Scope.PRODUCT, "Read.", "now", "storage"),
    )
    assert isinstance(draft, Draft)
    made = record_from_draft(draft, "d-cccccc", at(1), None)
    assert isinstance(made, Decision)
    assert made.statement == "The author confirms d-aaaaaa and d-bbbbbb."


@pytest.mark.parametrize("ids", [[], ["d-aaaaaa", "d-bbbbbb"]])
def test_confirmation_draft_without_area_requires_one_id(ids: list[str]) -> None:
    with pytest.raises(ValueError, match="one decision"):
        confirmation_draft(ids, Scope.PRODUCT, "Read.", "now", None)
