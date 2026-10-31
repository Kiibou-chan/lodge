from builders import area, entry, snapshot_of

from lodge.core import LengthGuidance, derive, feedback


def notes(statement: str, rests_on: tuple[str, ...] = ()) -> list[str]:
    a = entry(id="s-aaaaaa", statement=statement, rests_on=rests_on)
    b = entry(id="s-bbbbbb")
    s = snapshot_of(area(), a, b)
    return [f.message for f in feedback([a], s, derive(s), LengthGuidance())]


def test_statement_naming_an_unlisted_entry_asks() -> None:
    assert notes("s-bbbbbb and s-bbbbbb, s-cccccc.") == [
        "the statement names s-bbbbbb, but rests_on does not list it; "
        "does s-aaaaaa rest on s-bbbbbb? If so, add it to rests_on"
    ]


def test_listed_named_entry_no_feedback() -> None:
    assert notes("s-bbbbbb", ("s-bbbbbb",)) == []


def test_own_id_no_feedback() -> None:
    assert notes("s-aaaaaa") == []
