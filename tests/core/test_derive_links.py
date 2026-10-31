from builders import area, at, decision, entry, snapshot_of

from lodge.core import Action, Change, derive


def test_link_is_not_a_change() -> None:
    e = entry()
    link = decision(changes=(Change(e.id, Action.LINK),))
    d = derive(snapshot_of(area(), e, link))
    assert e.id not in d.changed_by
    assert d.linked_by[e.id] == (link.id,)


def test_link_raises_no_flag() -> None:
    e = entry()
    author = decision(decided_by="author", changes=(Change(e.id, Action.CREATE),))
    link = decision(date=at(30), changes=(Change(e.id, Action.LINK),))
    d = derive(snapshot_of(area(), e, author, link))
    assert link.id not in d.awaiting_author
    assert e.id not in d.touched_by_flagged


def test_supports_is_the_reverse_of_rests_on() -> None:
    a = entry(id="s-aaaaaa")
    b = entry(id="s-bbbbbb", rests_on=(a.id, "s-zzzzzz"))
    c = entry(id="s-cccccc", rests_on=(a.id,))
    d = derive(snapshot_of(area(), c, b, a))
    assert d.supports == {a.id: (b.id, c.id)}
