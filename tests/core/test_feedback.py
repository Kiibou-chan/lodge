from builders import at, decision, entry, snapshot_of

from lodge.core import (
    Action,
    Change,
    Feedback,
    LengthGuidance,
    NumberHandle,
    Record,
    Snapshot,
    SpecEntry,
    derive,
)
from lodge.core import feedback as give_feedback

LENGTH = LengthGuidance(
    title_chars=20, decision_statement_words=5, spec_statement_words=8, reasoning_words=6
)
ROOMY = LengthGuidance()


def given(snapshot: Snapshot, added: Record, length: LengthGuidance = ROOMY) -> list[Feedback]:
    return give_feedback([added], snapshot, derive(snapshot), length)


def test_clean_decision_no_feedback() -> None:
    d = decision(id="d-aaaaaa", title="Keep transcripts", statement="They are kept.")
    assert given(snapshot_of(d), d) == []


def test_title_over_guidance() -> None:
    d = decision(id="d-aaaaaa", title="A title that is much too long", statement="Short.")
    assert given(snapshot_of(d), d, LENGTH) == [
        Feedback("d-aaaaaa", "the title is 29 characters; guidance is 20 or fewer, on one line")
    ]


def test_decision_statement_over_guidance() -> None:
    d = decision(id="d-aaaaaa", title="Short", statement="One two three four five six.")
    assert given(snapshot_of(d), d, LENGTH) == [
        Feedback("d-aaaaaa", "the statement is 6 words; guidance is 5 or fewer for a decision")
    ]


def test_spec_statement_over_guidance() -> None:
    e = entry(
        id="s-aaaaaa", title="Short", statement="One two three four five six seven eight nine."
    )
    assert given(snapshot_of(e), e, LENGTH) == [
        Feedback(
            "s-aaaaaa", "the statement is 9 words; guidance is 8 or fewer for a specification entry"
        )
    ]


def test_statement_at_the_limit_is_clean() -> None:
    d = decision(id="d-aaaaaa", title="Short", statement="One two three four five.")
    assert given(snapshot_of(d), d, LENGTH) == []


def test_words_split_on_whitespace() -> None:
    d = decision(id="d-aaaaaa", title="Short", statement="a-b\tc\nd e f g")
    assert [f.message for f in given(snapshot_of(d), d, LENGTH)] == [
        "the statement is 6 words; guidance is 5 or fewer for a decision"
    ]


def test_reasoning_over_guidance() -> None:
    d = decision(id="d-aaaaaa", title="Short", statement="Short.", reasoning="a b c d e f g")
    assert given(snapshot_of(d), d, LENGTH) == [
        Feedback("d-aaaaaa", "the reasoning is 7 words; guidance is 6 or fewer")
    ]


def test_related_decision_asks_replace_or_narrow() -> None:
    old = decision(
        id="d-aaaaaa", title="Keep transcripts", changes=(Change("s-bbbbbb", Action.EDIT),)
    )
    new = decision(
        id="d-cccccc",
        title="Archive transcripts",
        date=at(5),
        changes=(Change("s-bbbbbb", Action.EDIT),),
    )
    s = snapshot_of(old, new, entry(id="s-bbbbbb"))
    assert given(s, new) == [
        Feedback(
            "d-cccccc",
            "it replaces and narrows nothing, but this current decision looks related: "
            "d-aaaaaa (Keep transcripts); does d-cccccc replace or narrow d-aaaaaa? If so, set "
            "replaces or narrows in the draft before adding it",
        )
    ]


def test_related_lists_each_with_its_title() -> None:
    first = decision(id="d-aaaaaa", title="First one", changes=(Change("s-bbbbbb", Action.EDIT),))
    second = decision(
        id="d-dddddd", title="Second one", date=at(3), changes=(Change("s-bbbbbb", Action.EDIT),)
    )
    new = decision(
        id="d-cccccc", title="Third", date=at(5), changes=(Change("s-bbbbbb", Action.EDIT),)
    )
    s = snapshot_of(first, second, new, entry(id="s-bbbbbb"))
    assert [f.message for f in given(s, new)] == [
        "it replaces and narrows nothing, but these current decisions look related: "
        "d-dddddd (Second one), d-aaaaaa (First one); does d-cccccc replace or narrow any of "
        "them? If so, set replaces or narrows in the draft before adding it"
    ]


def test_related_silent_when_it_replaces_or_narrows() -> None:
    old = decision(
        id="d-aaaaaa", title="Keep transcripts", changes=(Change("s-bbbbbb", Action.EDIT),)
    )
    for link in ({"replaces": ("d-aaaaaa",)}, {"narrows": ("d-aaaaaa",)}):
        new = decision(
            id="d-cccccc",
            title="Archive transcripts",
            date=at(5),
            changes=(Change("s-bbbbbb", Action.EDIT),),
            **link,
        )
        assert given(snapshot_of(old, new, entry(id="s-bbbbbb")), new) == []


def test_number_without_handle() -> None:
    d = decision(id="d-aaaaaa", title="Retries", statement="Retry 3 times, or 20% of calls.")
    assert given(snapshot_of(d), d) == [
        Feedback(
            "d-aaaaaa",
            "the text holds the numbers 3, 20% without a numbers handle; before adding the draft, "
            'give each one as `numbers: [{value: "…", handle: "…"}]`, the handle a record and '
            "key or a runnable command",
        )
    ]


def test_number_in_reasoning_counts() -> None:
    d = decision(id="d-aaaaaa", title="Retries", statement="Retry.", reasoning="It took 1.5 s.")
    assert next(f.message for f in given(snapshot_of(d), d)).startswith(
        "the text holds the number 1.5 "
    )


def test_numbers_in_backticks_ignored() -> None:
    d = decision(
        id="d-aaaaaa",
        title="Retries",
        statement="Run `pytest -n 4` first.",
        reasoning="```\nseq 1 10\n```\nThen stop.",
    )
    assert given(snapshot_of(d), d) == []


def test_numbers_ignore_ids_codes_and_dates() -> None:
    other = decision(id="d-bbbbbb", code="ITEM-1", date=at(9))
    d = decision(
        id="d-aaaaaa",
        title="Retries",
        statement="As d-3m8qk2 and s-4kq1zm say in item-1, since 2026-10-28.",
        reasoning="Written 2026-10-28T10:00:00+01:00.",
    )
    assert given(snapshot_of(d, other), d) == []


def test_number_in_a_word_that_is_not_a_code_is_flagged() -> None:
    other = decision(id="d-bbbbbb", code="ITEM-1", date=at(9))
    d = decision(id="d-aaaaaa", title="Hits", statement="Show the top-10 hits and Python-3.")
    message = next(f.message for f in given(snapshot_of(d, other), d))
    assert message.startswith("the text holds the numbers 10, 3 without")


def test_numbers_with_handle_are_clean() -> None:
    d = decision(
        id="d-aaaaaa",
        title="Retries",
        statement="Retry 3 times.",
        numbers=(NumberHandle("3", "uv run pytest"),),
    )
    assert given(snapshot_of(d), d) == []


def test_decision_derive_flags_waits_for_author() -> None:
    mine = decision(id="d-aaaaaa", title="Mine", decided_by="author")
    flagged = decision(id="d-bbbbbb", title="Theirs", date=at(5), replaces=("d-aaaaaa",))
    s = snapshot_of(mine, flagged)
    assert "d-bbbbbb" in derive(s).awaiting_author
    assert given(s, flagged) == [
        Feedback(
            "d-bbbbbb",
            "this decision will wait for the author: it takes effect at once, and a later "
            "author decision that confirms or replaces it clears the flag",
        )
    ]


def test_feedback_on_decision_with_changes_and_related() -> None:
    old = decision(
        id="d-aaaaaa",
        title="Keep transcripts",
        decided_by="author",
        changes=(Change("s-bbbbbb", Action.EDIT),),
    )
    new = decision(
        id="d-cccccc",
        title="Archive transcripts after 30 days",
        date=at(5),
        changes=(Change("s-bbbbbb", Action.EDIT),),
        statement="One two three four five six.",
    )
    s = snapshot_of(old, new, entry(id="s-bbbbbb"))
    messages = [f.message for f in given(s, new, LENGTH)]
    assert len(messages) == 4
    assert messages[0].startswith("the title is")
    assert messages[1].startswith("the statement is 6 words")
    assert messages[2].startswith("it replaces and narrows nothing")
    assert messages[3].startswith("this decision will wait")


def test_one_call_covers_every_added_record() -> None:
    d = decision(id="d-aaaaaa", title="A title that is much too long")
    e: SpecEntry = entry(id="s-bbbbbb", title="Another title that is far too long")
    s = snapshot_of(d, e)
    found = give_feedback([d, e], s, derive(s), LENGTH)
    assert [f.record_id for f in found] == ["d-aaaaaa", "s-bbbbbb"]


def agent_edit_she_replaces() -> list[Record]:
    return [
        entry(id="s-aaaaaa"),
        decision(
            id="d-aaaaaa",
            decided_by="author",
            date=at(0),
            changes=(Change("s-aaaaaa", Action.CREATE),),
        ),
        decision(id="d-bbbbbb", date=at(1), changes=(Change("s-aaaaaa", Action.EDIT),)),
    ]


def test_author_replacing_an_agent_edit_is_asked_whether_it_edits_back() -> None:
    new = decision(id="d-cccccc", decided_by="author", date=at(2), replaces=("d-bbbbbb",))
    s = snapshot_of(*agent_edit_she_replaces(), new)
    assert given(s, new) == [
        Feedback(
            "d-cccccc",
            "it replaces d-bbbbbb, whose edit of s-aaaaaa is still the latest edit of that "
            "entry; does d-cccccc edit s-aaaaaa back? If so, add an edit draft of s-aaaaaa "
            "and list it in changes with action edit",
        )
    ]


def test_no_edit_back_question_when_the_decision_edits_the_entry() -> None:
    edit = (Change("s-aaaaaa", Action.EDIT),)
    new = decision(
        id="d-cccccc", decided_by="author", date=at(2), replaces=("d-bbbbbb",), changes=edit
    )
    assert given(snapshot_of(*agent_edit_she_replaces(), new), new) == []


def test_no_edit_back_question_when_a_later_change_stands() -> None:
    later = decision(id="d-dddddd", date=at(3), changes=(Change("s-aaaaaa", Action.EDIT),))
    new = decision(id="d-cccccc", decided_by="author", date=at(2), replaces=("d-bbbbbb",))
    s = snapshot_of(*agent_edit_she_replaces(), new, later)
    assert given(s, new) == []


def test_replacing_her_retirement_says_which_entry_comes_back() -> None:
    items = agent_edit_she_replaces()[:2]
    retire = decision(
        id="d-bbbbbb", decided_by="author", date=at(1), changes=(Change("s-aaaaaa", Action.RETIRE),)
    )
    new = decision(id="d-cccccc", decided_by="author", date=at(2), replaces=("d-bbbbbb",))
    assert given(snapshot_of(*items, retire, new), new) == [
        Feedback(
            "d-cccccc",
            "it replaces d-bbbbbb, the last standing retirement of s-aaaaaa, so s-aaaaaa becomes "
            "current again; to keep it retired, list it in changes with action retire",
        )
    ]
