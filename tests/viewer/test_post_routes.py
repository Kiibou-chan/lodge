import threading
from collections.abc import Callable, Mapping
from urllib.parse import urlencode, urlsplit

import pytest

from lodge.app import CommitOutcome, Committed, Lodge, PublishOutcome
from lodge.core import Tree
from lodge.viewer import server, writes
from viewer.test_post_gate import HEADERS, TOKEN
from viewer.world import staged_world


def test_confirm_redirects_with_done_code() -> None:
    make, store = staged_world()
    reply = writes.handle_post(
        make,
        writes.Gatekeeper(TOKEN, writes.allowed_hosts(8787, ())),
        "/confirm",
        HEADERS,
        urlencode({"token": TOKEN, "id": "d-cccccc", "words": "Read."}).encode(),
    )
    assert reply.status == 303
    assert reply.location == "/r/d-cccccc?done=committed"
    assert len(store.publishes) == 1


def test_get_with_done_shows_notice() -> None:
    make, _ = staged_world()
    assert (
        "Written and committed." in server.render(make, urlsplit("/r/d-aaaaaa?done=committed"))[1]
    )


def test_staged_on_base_gives_staged_base() -> None:
    make, store = staged_world()
    store.commit_result = Committed(CommitOutcome.ON_BASE)
    result = make().confirm(["d-cccccc"], "Read.", commit=True)
    assert writes.done_code(result) == "staged-base"


def test_area_confirm_redirects_to_the_area() -> None:
    make, _ = staged_world()
    assert (
        send(make, "/confirm", id="d-cccccc", words="Yes", area="storage").location
        == "/spec?area=storage&done=committed"
    )


def test_stale_list_redirects_with_stale() -> None:
    make, store = staged_world()
    send(make, "/confirm", id="d-cccccc", words="Yes")
    assert send(make, "/confirm", id="d-cccccc", words="Yes").location == "/r/d-cccccc?done=stale"
    assert len(store.publishes) == 1


def test_failed_check_answers_400_and_writes_nothing() -> None:
    make, store = staged_world()
    store.files["lodge/decisions/d-bbbbbb-broken.md"] = "no header\n"
    result = send(make, "/confirm", id="d-cccccc", words="Yes")
    assert result.status == 400
    assert 'href="/r/d-cccccc"' in result.text
    assert not store.publishes


def test_ask_from_viewer_records_her_words() -> None:
    make, _ = staged_world()
    result = send(make, "/threads", about="d-cccccc", kind="doubt", text="  Why?\r\nReally.  ")
    assert result.location == "/r/d-cccccc?done=committed#q-111111"
    message = make().thread("q-111111").thread.messages[0]
    assert (message.by, message.where, message.when, message.text) == (
        "author",
        "lodge viewer",
        "2026-10-29 09:30",
        "Why?\nReally.",
    )


def test_unknown_kind_400() -> None:
    make, store = staged_world()
    assert send(make, "/threads", about="d-cccccc", kind="other", text="Why?").status == 400
    assert not store.publishes


def test_reply_and_close_redirect_to_the_thread() -> None:
    make, _ = staged_world()
    send(make, "/threads", about="d-cccccc", kind="question", text="Why?")
    for action, text in (("reply", "Yes"), ("close", "")):
        result = send(make, f"/threads/q-111111/{action}", text=text)
        assert result.location == "/r/d-cccccc?done=committed#q-111111"
    assert make().thread("q-111111").thread.state.value == "closed"


def test_viewer_writes_only_new_decisions_and_thread_files() -> None:
    make, store = staged_world()
    before = set(store.files)
    send(make, "/confirm", id="d-cccccc", words="Yes")
    send(make, "/threads", about="d-cccccc", kind="question", text="Why?")
    send(make, "/threads/q-111111/reply", text="Yes")
    send(make, "/threads/q-111111/close", text="")
    assert len(store.publishes) == 4
    assert all(
        p.startswith("lodge/threads/") or (p.startswith("lodge/decisions/") and p not in before)
        for paths, _ in store.publishes
        for p in paths
    )


def test_two_concurrent_confirmations_write_once(monkeypatch: pytest.MonkeyPatch) -> None:
    make, store = staged_world()
    entered, release = threading.Event(), threading.Event()
    real = store.publish
    calls = 0

    def factory() -> Lodge:
        nonlocal calls
        calls += 1
        if calls == 2:
            entered.set()
        return make()

    def publish(base: Tree, paths: Mapping[str, str], message: str) -> PublishOutcome:
        assert entered.wait(5)
        assert release.wait(5)
        return real(base, paths, message)

    monkeypatch.setattr(store, "publish", publish)
    results = []

    def work() -> None:
        location = send(factory, "/confirm", id="d-cccccc", words="Yes").location
        assert location is not None
        results.append(location)

    first = threading.Thread(target=work)
    first.start()
    second = threading.Thread(target=work)
    second.start()
    assert entered.wait(5)
    release.set()
    first.join(5)
    second.join(5)
    assert not first.is_alive() and not second.is_alive()
    assert sorted(results) == ["/r/d-cccccc?done=committed", "/r/d-cccccc?done=stale"]
    assert len(store.publishes) == 1


def send(make: Callable[[], Lodge], path: str, **fields: str) -> writes.Reply:
    return writes.handle_post(
        make,
        writes.Gatekeeper(TOKEN, writes.allowed_hosts(8787, ())),
        path,
        HEADERS,
        urlencode({"token": TOKEN} | fields).encode(),
    )


@pytest.mark.parametrize("action", ["reply", "close"])
def test_orphaned_thread_post_does_not_fail(action: str) -> None:
    make, store = staged_world()
    send(make, "/threads", about="d-cccccc", kind="question", text="Why?")
    path = "lodge/threads/q-111111.md"
    store.files[path] = store.files[path].replace("d-cccccc", "s-zzzzzz")
    result = send(make, f"/threads/q-111111/{action}", text="Answer")
    assert result.status == 400
    assert 'href="/r/s-zzzzzz"' in result.text
    assert "s-zzzzzz" in result.text
    assert len(store.publishes) == 1
