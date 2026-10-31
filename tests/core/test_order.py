from builders import area, decision, entry, snapshot_of

from lodge.core import (
    Action,
    Change,
    area_names,
    derive,
    derived_order,
    rests_on_tree,
    written_order,
)

A, B, C, D = "s-aaaaaa", "s-bbbbbb", "s-cccccc", "s-dddddd"


def test_ranked_areas_first_then_by_name() -> None:
    s = snapshot_of(area(name="b", rank=2), area(name="a", rank=1), area(name="z"), area(name="c"))
    assert area_names(s) == ("a", "b", "c", "z")


def test_shared_rank_ordered_by_name() -> None:
    assert area_names(snapshot_of(area(name="x", rank=1), area(name="w", rank=1))) == ("w", "x")


def test_folder_without_area_file_sorts_with_unranked() -> None:
    assert area_names(snapshot_of(area(name="z", rank=0), entry(area="a"), area(name="b"))) == (
        "z",
        "a",
        "b",
    )


def test_entry_after_what_it_rests_on() -> None:
    s = snapshot_of(area(order=(A, B, C)), entry(id=A, rests_on=(C,)), entry(id=B), entry(id=C))
    assert tuple(p.id for p in derived_order(s, derive(s), "storage")) == (B, C, A)


def test_no_links_keeps_written_order() -> None:
    s = snapshot_of(area(order=(B, A)), entry(id=A), entry(id=B), entry(id=C))
    assert written_order(s, derive(s), "storage") == (B, A, C)
    assert tuple(p.id for p in derived_order(s, derive(s), "storage")) == (B, A, C)


def test_under_is_the_target_placed_last() -> None:
    s = snapshot_of(area(order=(A, B, C)), entry(id=A), entry(id=B), entry(id=C, rests_on=(A, B)))
    got = derived_order(s, derive(s), "storage")
    assert tuple(p.id for p in got) == (A, B, C)
    assert (got[2].under, got[2].depth) == (B, 1)


def test_dependant_follows_what_it_rests_on() -> None:
    s = snapshot_of(area(order=(A, B, C)), entry(id=A), entry(id=B), entry(id=C, rests_on=(A,)))
    got = derived_order(s, derive(s), "storage")
    assert tuple(p.id for p in got) == (A, C, B)
    assert (got[1].depth, got[1].under, got[2].depth) == (1, A, 0)


def test_cycle_falls_back_to_written_order() -> None:
    s = snapshot_of(area(order=(A, B)), entry(id=A, rests_on=(B,)), entry(id=B, rests_on=(A,)))
    assert tuple(p.id for p in derived_order(s, derive(s), "storage")) == (A, B)


def test_retired_target_does_not_hold_an_entry_back() -> None:
    s = snapshot_of(
        area(order=(A, C)),
        entry(id=A, rests_on=(B,)),
        entry(id=B),
        entry(id=C),
        decision(changes=(Change(B, Action.RETIRE),)),
    )
    got = derived_order(s, derive(s), "storage")
    assert tuple(p.id for p in got) == (A, C)
    assert (got[0].depth, got[0].under) == (0, None)


def test_dependants_follow_depth_first() -> None:
    s = snapshot_of(
        area(order=(A, B, C, D)),
        entry(id=A),
        entry(id=B, rests_on=(A,)),
        entry(id=C, rests_on=(A,)),
        entry(id=D, rests_on=(B,)),
    )
    got = derived_order(s, derive(s), "storage")
    assert tuple(p.id for p in got) == (A, B, D, C)
    assert tuple((p.depth, p.under) for p in got) == ((0, None), (1, A), (2, B), (1, A))


def test_diamond_uses_last_placed_target_at_depth_two() -> None:
    s = snapshot_of(
        area(order=(A, B, C, D)),
        entry(id=A),
        entry(id=B, rests_on=(A,)),
        entry(id=C, rests_on=(A,)),
        entry(id=D, rests_on=(B, C)),
    )
    got = derived_order(s, derive(s), "storage")
    assert tuple(p.id for p in got) == (A, B, C, D)
    assert tuple((p.depth, p.under) for p in got) == ((0, None), (1, A), (1, A), (2, C))


def test_rests_on_tree_reaches_the_roots() -> None:
    s = snapshot_of(entry(id=A), entry(id=B, rests_on=(A,)), entry(id=C, rests_on=(B,)))
    tree = rests_on_tree(s, derive(s), C)
    assert tree[0].id == B and tree[0].children[0].id == A
    assert tree[0].children[0].children == ()
    assert tree[0].title == s.entries[B].title and tree[0].status == "current"


def test_rests_on_tree_stops_on_a_cycle() -> None:
    s = snapshot_of(entry(id=A, rests_on=(B,)), entry(id=B, rests_on=(A,)))
    tree = rests_on_tree(s, derive(s), A)
    assert tree[0].id == B and tree[0].children == ()
