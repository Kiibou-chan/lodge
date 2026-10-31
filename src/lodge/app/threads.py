"""Thread reads and checked, retryable message writes."""

from collections.abc import Mapping
from datetime import datetime

from lodge import core
from lodge.app.errors import Conflict, LodgeError
from lodge.app.ports import PublishOutcome
from lodge.app.results import AddOutcome, ThreadList, ThreadShown, ThreadsWaiting, Written
from lodge.app.state import State, Wiring, not_found, read_checked, read_state, resolve_ref
from lodge.app.writes import mint_unused
from lodge.core import Message, Raises, Thread, ThreadState, Tree


def _find(state: State, ref: str) -> Thread:
    thread = state.snapshot.threads.get(ref.lower())
    if thread is None:
        raise not_found(state, f"thread named {ref}", ref)
    return thread


def _message(
    now: datetime, by: str, text: str, where: str | None, when: str | None, close: bool
) -> Message:
    text = core.clean_text(text)
    if not text and not close:
        raise LodgeError("the message is empty")
    if not by.strip():
        raise LodgeError("by needs a non-empty role")
    if by != "author" and "author" in by.lower():
        raise LodgeError("write author exactly, or use your own role")
    if by == "author":
        if where is None or not where.strip():
            raise LodgeError("a message by author needs where, the place of the author's words")
        stamp = when if when is not None else now.strftime("%Y-%m-%d %H:%M")
    else:
        if where is not None or when is not None:
            raise LodgeError("where and when are for messages by author")
        stamp = now.isoformat(timespec="seconds")
    return Message(by, stamp, text, where)


def write(
    w: Wiring,
    ref: str,
    raises: Raises | None,
    by: str,
    text: str,
    where: str | None,
    when: str | None,
    commit: bool,
    close: bool = False,
) -> Written:
    for _ in range(3):
        state = read_state(w.store)
        now = w.clock.now()
        message = _message(now, by, text, where, when, close)
        s = state.snapshot
        if raises is not None:
            about = resolve_ref(state, ref)
            ident = mint_unused(w.ids, "q", {*s.decisions, *s.entries, *s.threads})
            thread = Thread(
                ident,
                about,
                raises,
                ThreadState.OPEN,
                now.isoformat(timespec="seconds"),
                (message,),
            )
            action = "doubt raised" if raises is Raises.DOUBT else "question asked"
            description = f"{action} by {by}"
        else:
            thread = _find(state, ref)
            if thread.state is ThreadState.CLOSED:
                raise LodgeError(f"{thread.id} is closed")
            thread = core.appended(thread, message, close)
            description = f"closed by {by}" if close else f"{by} reply"
        path = core.thread_path(thread.id)
        try:
            content = core.write_thread(thread)
        except ValueError as error:
            raise LodgeError(str(error)) from None
        after = core.load(
            Tree(
                state.current.rev, {**state.current.files, path: content}, state.current.attachments
            )
        )
        check = core.check_change(core.load(state.published), after, w.settings, now, s)
        if not check.ok:
            return Written((thread.id,), AddOutcome.CHECK_FAILED, check, about=thread.about)
        description = f"Thread {thread.id}: {description}"
        outcome = w.store.publish(state.current, {path: content}, description)
        if outcome is PublishOutcome.REJECTED:
            continue
        committed = (
            w.store.commit((path,), description)
            if commit and outcome is PublishOutcome.STAGED
            else None
        )
        added = AddOutcome.PUBLISHED if outcome is PublishOutcome.PUBLISHED else AddOutcome.STAGED
        return Written((thread.id,), added, check, committed, thread.about)
    raise Conflict("other changes reached the store three times; nothing was written, so try again")


def _titles(state: State, threads: tuple[Thread, ...]) -> Mapping[str, str]:
    s = state.snapshot
    records: Mapping[str, core.Decision | core.SpecEntry] = {**s.decisions, **s.entries}
    return {t.about: records[t.about].title for t in threads if t.about in records}


def list_open(w: Wiring) -> ThreadList:
    state = read_checked(w)
    threads = core.newest_last(
        t for t in state.snapshot.threads.values() if t.state is ThreadState.OPEN
    )
    return ThreadList(threads, _titles(state, threads), state.read)


def show(w: Wiring, ref: str) -> ThreadShown:
    state = read_checked(w)
    thread = _find(state, ref)
    about = core.level1(state.snapshot, state.derived, thread.about, state.failing)
    return ThreadShown(thread, about, state.read)


def waiting(w: Wiring) -> ThreadsWaiting:
    listed = list_open(w)
    return ThreadsWaiting(
        tuple(t for t in listed.items if t.messages[-1].by == "author"),
        tuple(t for t in listed.items if t.messages[-1].by != "author"),
        listed.titles,
        listed.read,
    )
