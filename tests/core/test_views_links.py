from builders import area, at, decision, entry, snapshot_of

from lodge.core import Action, Change, Level1, Level3, derive, level1, level3


def views(*, retire: bool = False, later: Action | None = None) -> tuple[Level1, Level3, Level3]:
    a = entry(id="s-aaaaaa", rests_on=("s-bbbbbb",))
    b = entry(id="s-bbbbbb")
    own = decision(id="d-aaaaaa", decided_by="author", changes=(Change(a.id, Action.CREATE),))
    target = decision(
        id="d-bbbbbb",
        date=at(10),
        changes=(Change(b.id, Action.RETIRE if retire else Action.EDIT),),
    )
    extra = (
        ()
        if later is None
        else (decision(id="d-cccccc", date=at(20), changes=(Change(a.id, later),)),)
    )
    s = snapshot_of(area(), a, b, own, target, *extra)
    d = derive(s)
    return level1(s, d, a.id, frozenset()), level3(s, d, a.id), level3(s, d, b.id)


def test_rests_on_retired_mark() -> None:
    assert "rests on s-bbbbbb, retired" in views(retire=True)[0].flags


def test_rests_on_changed_since_mark() -> None:
    assert "rests on s-bbbbbb, changed since" in views()[0].flags


def test_edit_with_unchanged_text_clears_changed_since() -> None:
    assert "rests on s-bbbbbb, changed since" not in views(later=Action.EDIT)[0].flags


def test_link_after_the_change_keeps_changed_since() -> None:
    assert "rests on s-bbbbbb, changed since" in views(later=Action.LINK)[0].flags


def test_entry_level1_keeps_the_author_after_a_link() -> None:
    assert views(later=Action.LINK)[0].decided_by == "author"


def test_level3_lists_rests_on_supports_and_linked_by() -> None:
    _, own, target = views(later=Action.LINK)
    assert own.links == (
        ("changed by", "d-aaaaaa", "current"),
        ("rests on", "s-bbbbbb", "current"),
        ("linked by", "d-cccccc", "current"),
    )
    assert ("supports", "s-aaaaaa", "current") in target.links
