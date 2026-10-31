"""Published threads are append-only."""

from dataclasses import replace
from datetime import datetime

import pytest
from builders import area, entry, files_of, message, snapshot_of, thread

from lodge.core import (
    CheckResult,
    CoreSettings,
    Raises,
    Thread,
    ThreadState,
    Tree,
    appended,
    check_change,
    check_state,
    load,
)


def changes(before: Thread, after: Thread) -> CheckResult:
    e = entry(id="s-aaaaaa")
    return check_change(
        snapshot_of(area(), e, before),
        snapshot_of(area(), e, after),
        CoreSettings(),
        datetime.fromisoformat("2026-10-30T12:00:00+01:00"),
    )


def test_open_thread_passes_every_check() -> None:
    t = thread()
    assert changes(t, t).ok
    assert check_state(snapshot_of(area(order=(t.about,)), entry(id=t.about), t)).ok


def test_unresolved_about_fails_check_2() -> None:
    result = check_state(snapshot_of(thread()))
    assert any(
        p.check == 2 and "about s-aaaaaa, which does not exist" in p.message
        for p in result.problems
    )


def test_duplicate_thread_id_fails_check_2() -> None:
    t = thread()
    files = files_of(t)
    files["lodge/threads/" + t.id + "-copy.md"] = next(iter(files.values()))
    assert len([p for p in load(Tree(None, files)).problems if p.check == 2]) == 2


def test_file_name_must_start_with_the_id() -> None:
    t = thread()
    assert any(
        p.check == 1
        for p in check_state(snapshot_of(t, paths={t.id: "lodge/threads/wrong.md"})).problems
    )


def test_appending_a_message_passes() -> None:
    t = thread()
    assert changes(t, appended(t, message())).ok


def test_closing_passes() -> None:
    t = thread()
    assert changes(t, appended(t, message(text=""), close=True)).ok


def fails(before: Thread, after: Thread, text: str) -> None:
    assert any(p.check == 5 and text in p.message for p in changes(before, after).problems)


def test_editing_a_published_message_fails_check_5() -> None:
    t = thread()
    fails(
        t,
        replace(t, messages=(message(text="Edited."),)),
        "a published message was changed or removed; messages are only appended",
    )


def test_removing_a_message_fails_check_5() -> None:
    t = thread(messages=(message(), message()))
    fails(t, replace(t, messages=t.messages[:1]), "a published message")


def test_changing_about_fails_check_5() -> None:
    t = thread()
    fails(t, replace(t, about="s-bbbbbb"), "about of a published thread was changed")


def test_changing_raises_fails_check_5() -> None:
    t = thread()
    fails(t, replace(t, raises=Raises.QUESTION), "raises of a published thread was changed")


def test_reopening_fails_check_5() -> None:
    t = thread(state=ThreadState.CLOSED)
    fails(t, replace(t, state=ThreadState.OPEN), "a closed thread was opened again")


def test_message_after_closing_fails_check_5() -> None:
    t = thread(state=ThreadState.CLOSED)
    fails(
        t,
        replace(t, messages=(*t.messages, message())),
        "a message was added after the thread was closed",
    )


def test_closing_without_a_message_fails_check_5() -> None:
    t = thread()
    fails(t, replace(t, state=ThreadState.CLOSED), "a thread was closed without a closing message")


@pytest.mark.parametrize("stale_path", [False, True])
def test_missing_published_thread_fails_check_2(stale_path: bool) -> None:
    t = thread()
    result = check_change(
        snapshot_of(t),
        snapshot_of(paths={t.id: "lodge/threads/old.md"} if stale_path else None),
        CoreSettings(),
        datetime.fromisoformat("2026-10-30T12:00:00+01:00"),
    )
    assert any(p.check == 2 and t.id in p.message for p in result.problems)
