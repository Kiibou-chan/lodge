from builders import area, snapshot_of

from lodge.core import Feedback, area_feedback, area_path


def test_shared_rank_feedback() -> None:
    s = snapshot_of(*(area(name=n, rank=2) for n in ("storage", "a", "b", "c")))
    assert area_feedback(s, [area_path("storage")]) == [
        Feedback(
            "area:storage",
            "rank 2 is shared with area a, b, and c; areas that share a rank are ordered by name",
        )
    ]
    for names, expected in [(("a",), "a"), (("a", "b"), "a and b")]:
        s = snapshot_of(area(rank=0), *(area(name=n, rank=0) for n in names))
        assert (
            area_feedback(s, [area_path("storage")])[0].message
            == f"rank 0 is shared with area {expected}; areas that share a rank are ordered by name"
        )


def test_unshared_rank_no_feedback() -> None:
    s = snapshot_of(area(rank=1), area(name="other", rank=2), area(name="plain"))
    assert area_feedback(s, [area_path(n) for n in s.areas]) == []


def test_unwritten_area_no_feedback() -> None:
    s = snapshot_of(area(rank=1), area(name="other", rank=1))
    assert area_feedback(s, []) == []
