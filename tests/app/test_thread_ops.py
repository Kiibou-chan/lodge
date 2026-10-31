"""Thread operations over the made-up storage project."""

from datetime import timedelta

import pytest
from applying import area_text
from fakes import START, CountingIds, FixedClock, MemoryStore
from support import project, wired

from lodge.app import AddOutcome, Conflict, Lodge, LodgeError, NotFound
from lodge.core import Filters, Raises, Thread, ThreadState, Tree, load

Q = "q-111111"
PATH = f"lodge/threads/{Q}.md"


def opened(staged: bool = False) -> tuple[MemoryStore, Lodge]:
    store = project(staged)
    lodge = wired(store)
    lodge.ask("s-aaaaaa", Raises.DOUBT, "coordinator", "Why?")
    return store, lodge


def stored(store: MemoryStore) -> Thread:
    return load(Tree(None, store.files)).threads[Q]


def test_ask_writes_a_thread_file() -> None:
    store = project()
    written = wired(store).ask("s-aaaaaa", Raises.DOUBT, "coordinator", "Why?")
    assert list(store.publishes[0][0]) == [PATH]
    thread = stored(store)
    assert thread.about == written.about == "s-aaaaaa"
    assert thread.raises is Raises.DOUBT and thread.state is ThreadState.OPEN
    assert len(thread.messages) == 1
    assert thread.messages[0].by == "coordinator"
    assert thread.messages[0].when == START.isoformat(timespec="seconds")
    assert written.ids == (Q,) and written.check.ok


def test_ask_resolves_a_code() -> None:
    store = project()
    wired(store).ask("item-1", Raises.QUESTION, "reviewer", "Why?")
    assert stored(store).about == "d-aaaaaa"
    assert store.publishes[0][1] == f"Thread {Q}: question asked by reviewer"


def test_ask_on_an_unknown_ref_is_not_found() -> None:
    with pytest.raises(NotFound, match="no record named missing"):
        wired(project()).ask("missing", Raises.DOUBT, "agent", "Why?")


def test_author_message_needs_where() -> None:
    with pytest.raises(LodgeError, match="a message by author needs where"):
        wired(project()).ask("s-aaaaaa", Raises.DOUBT, "author", "Why?")


def test_author_when_defaults_to_the_minute() -> None:
    store = project()
    wired(store).ask("s-aaaaaa", Raises.DOUBT, "author", "Why?", where="a session")
    assert stored(store).messages[0].when == "2026-10-29 09:30"


@pytest.mark.parametrize("meta", [{"where": "a session"}, {"when": "yesterday"}])
def test_agent_message_may_not_carry_where(meta: dict[str, str]) -> None:
    with pytest.raises(LodgeError, match="where and when are for messages by author"):
        wired(project()).ask(
            "s-aaaaaa",
            Raises.DOUBT,
            "agent",
            "Why?",
            where=meta.get("where"),
            when=meta.get("when"),
        )


@pytest.mark.parametrize("by", ["Author", "the author", ""])
def test_role_like_author_refused(by: str) -> None:
    with pytest.raises(
        LodgeError,
        match=("write author exactly, or use your own role" if by else "by needs a non-empty role"),
    ):
        wired(project()).ask("s-aaaaaa", Raises.DOUBT, by, "Why?")


@pytest.mark.parametrize("text", ["", " \r\n "])
def test_empty_text_refused(text: str) -> None:
    store, lodge = opened()
    with pytest.raises(LodgeError, match="the message is empty"):
        lodge.ask("s-aaaaaa", Raises.DOUBT, "agent", text)
    with pytest.raises(LodgeError, match="the message is empty"):
        lodge.reply(Q, "agent", text)
    assert len(store.publishes) == 1


def test_text_loses_cr_and_outer_whitespace_only() -> None:
    store = project()
    wired(store).ask("s-aaaaaa", Raises.DOUBT, "agent", " \r\nA  B\r\n C \r\n ")
    assert stored(store).messages[0].text == "A  B\n C"


@pytest.mark.parametrize("field", ["where", "when"])
def test_unstorable_where_refused(field: str) -> None:
    store = project()
    meta = {"where": "a session", field: "a\x01"}
    with pytest.raises(LodgeError, match=field):
        wired(store).ask(
            "s-aaaaaa",
            Raises.DOUBT,
            "author",
            "Why?",
            where=meta.get("where"),
            when=meta.get("when"),
        )
    assert store.publishes == []


def test_reply_appends() -> None:
    store, lodge = opened()
    written = lodge.reply(Q.upper(), "author", "Here.", where="a session")
    assert [m.text for m in stored(store).messages] == ["Why?", "Here."]
    assert written.about == "s-aaaaaa"
    assert store.publishes[-1][1] == f"Thread {Q}: author reply"


def test_reply_to_closed_thread_refused() -> None:
    _, lodge = opened()
    lodge.close(Q, "agent")
    with pytest.raises(LodgeError, match=f"{Q} is closed"):
        lodge.reply(Q, "agent", "Again")
    with pytest.raises(LodgeError, match=f"{Q} is closed"):
        lodge.close(Q, "agent")


def test_close_appends_closed_by_the_closer() -> None:
    store, lodge = opened()
    lodge.close(Q, "reviewer")
    thread = stored(store)
    assert thread.state is ThreadState.CLOSED
    assert thread.messages[-1].text == "" and thread.messages[-1].by == "reviewer"
    assert store.publishes[-1][1] == f"Thread {Q}: closed by reviewer"


def test_close_without_text_passes_the_check() -> None:
    _, lodge = opened()
    assert lodge.close(Q, "agent").check.ok


@pytest.mark.parametrize("text,expected", [(" Answer.\r\n ", "Answer."), (" \r\n ", "")])
def test_close_with_text(text: str, expected: str) -> None:
    store, lodge = opened()
    lodge.close(Q, "agent", text)
    assert stored(store).messages[-1].text == expected


def test_rejected_publish_starts_again() -> None:
    store = project()
    store.reject_next({})
    written = wired(store).ask("s-aaaaaa", Raises.DOUBT, "agent", "Why?")
    assert written.outcome is AddOutcome.PUBLISHED and store.attempts == 2


def test_commit_after_staged_when_asked() -> None:
    store = project(staged=True)
    written = wired(store).ask(
        "s-aaaaaa", Raises.DOUBT, "author", "Why?", where="a session", commit=True
    )
    assert store.commits == [((PATH,), f"Thread {Q}: doubt raised by author")]
    assert written.committed is not None and written.committed.detail == ""


def test_no_commit_unless_asked() -> None:
    store, lodge = opened(staged=True)
    written = lodge.reply(Q, "agent", "Here.")
    assert store.commits == [] and written.committed is None


def test_no_commit_when_published() -> None:
    store = project()
    written = wired(store).ask("s-aaaaaa", Raises.DOUBT, "agent", "Why?", commit=True)
    assert store.commits == [] and written.committed is None


def test_threads_lists_open_newest_last() -> None:
    store = project()
    lodge = wired(store, FixedClock(step=timedelta(minutes=1)), CountingIds(first=9, step=-1))
    lodge.ask("s-aaaaaa", Raises.DOUBT, "agent", "First")
    lodge.ask("s-aaaaaa", Raises.QUESTION, "agent", "Second")
    third = lodge.ask("s-aaaaaa", Raises.DOUBT, "agent", "Third")
    lodge.close(third.ids[0], "agent")
    listed = lodge.threads()
    assert [t.id for t in listed.items] == ["q-999999", "q-888888"]
    assert listed.titles["s-aaaaaa"] == "Transcripts are kept"
    assert listed.read.freshness is not None


def test_thread_shows_one_thread() -> None:
    _, lodge = opened()
    shown = lodge.thread(Q.upper())
    assert shown.thread.id == Q and shown.about is not None and shown.about.id == "s-aaaaaa"
    assert shown.read.freshness is not None
    with pytest.raises(NotFound, match="no thread named q-000000"):
        lodge.thread("q-000000")


def test_threads_waiting_groups() -> None:
    _, lodge = opened()
    lodge.ask("s-aaaaaa", Raises.QUESTION, "author", "Second", where="a session")
    waiting = lodge.threads_waiting()
    assert [t.id for t in waiting.for_agent] == ["q-222222"]
    assert [t.id for t in waiting.for_author] == [Q]
    assert waiting.titles == {"s-aaaaaa": "Transcripts are kept"}
    assert waiting.read.freshness is not None


def test_show_carries_the_records_threads() -> None:
    _, lodge = opened()
    lodge.close(Q, "agent")
    assert [t.id for t in lodge.show("s-aaaaaa").threads] == [Q]
    assert lodge.show("item-1").threads == ()


def test_added_paths_lists_the_files_written() -> None:
    store = project()
    added = wired(store).add([("area.md", area_text("name: access"))])
    assert added.paths == ("lodge/spec/access/_area.md",)


def test_search_and_timeline_leave_threads_out() -> None:
    _, lodge = opened()
    assert {i.id for i in lodge.search("", Filters()).items} == {"s-aaaaaa", "d-aaaaaa"}
    assert [i.id for i in lodge.timeline().items] == ["d-aaaaaa"]


def test_thread_about_a_missing_record_reads() -> None:
    store, lodge = opened()
    store.files[PATH] = store.files[PATH].replace("s-aaaaaa", "s-zzzzzz")
    shown = lodge.thread(Q)
    assert shown.about is None
    assert shown.thread.messages[0].text == "Why?"
    assert lodge.threads().items[0].about == "s-zzzzzz"
    assert lodge.threads_waiting().for_author[0].id == Q


def test_three_rejections_are_a_conflict() -> None:
    store = project()
    store.reject_next({}, {}, {})
    with pytest.raises(Conflict, match="three times"):
        wired(store).ask("s-aaaaaa", Raises.DOUBT, "agent", "Why?")
    assert store.attempts == 3 and store.publishes == []
