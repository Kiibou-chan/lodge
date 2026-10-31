from urllib.parse import urlsplit

from builders import area, entry
from fakes import MemoryStore
from support import wired

from lodge.core import Raises, SpecEntry
from lodge.viewer import pages, server
from viewer.test_post_gate import TOKEN
from viewer.test_post_routes import send
from viewer.world import staged_world

A, B, C = "s-aaaaaa", "s-bbbbbb", "s-cccccc"


def specification(*entries: SpecEntry, written: bool = False) -> str:
    lodge = wired(MemoryStore(area(order=(A, B, C)), *entries))
    return server.render(
        lambda: lodge, urlsplit("/spec" + ("?order=written" if written else "")), TOKEN
    )[1]


def test_threads_newest_last() -> None:
    make, _ = staged_world()
    send(make, "/threads", about=A, kind="doubt", text="First")
    send(make, "/threads", about=A, kind="question", text="Second")
    shown = make().show(A)
    text = pages.record_page(shown, TOKEN)
    assert len(shown.threads) == 2
    assert text.index('id="' + shown.threads[0].id) < text.index('id="' + shown.threads[1].id)
    assert "Doubt " in text and "Question " in text and "open" in text
    assert "author" in text and "2026-10-29 09:30" in text and "lodge viewer" in text


def test_entry_tree_down_to_roots_and_one_level_up() -> None:
    lodge = wired(MemoryStore(entry(id=A), entry(id=B, rests_on=(A,)), entry(id=C, rests_on=(B,))))
    shown = lodge.show(B)
    assert shown.rests_on[0].id == A and shown.supports[0].id == C
    text = pages.record_page(shown, TOKEN)
    down, up = text.split("Rests on</h2>")[1].split("Rests on it</h2>")
    assert "/r/" + A in down and "current" in down
    assert "/r/" + C in up and "current" in up
    assert "<ul><li>" in down


def test_spec_opens_by_dependency() -> None:
    text = specification(entry(id=A), entry(id=B), entry(id=C, rests_on=(A,)))
    assert text.index("/r/" + A) < text.index("/r/" + C) < text.index("/r/" + B)
    assert 'class="depth-1"' in text and "By dependency" in text and "As written" in text


def test_spec_also_rests_on_line() -> None:
    text = specification(entry(id=A), entry(id=B), entry(id=C, rests_on=(A, B)))
    assert 'also rests on <a href="/r/' + A in text


def test_thread_closed_without_text_shows_closed_by_author() -> None:
    make, store = staged_world()
    send(make, "/threads", about=A, kind="question", text="Why?")
    send(make, "/threads/q-111111/close", text="")
    assert make().thread("q-111111").thread.messages[-1].text == ""
    assert "Closed." not in store.files["lodge/threads/q-111111.md"]
    text = pages.record_page(make().show(A), TOKEN)
    assert "Closed by author" in text
    closing = text.split("Closed by author")[1].split("</section>")[0]
    assert "2026-10-29 09:30" in closing and "lodge viewer" in closing and "<p>" not in closing


def test_spec_as_written() -> None:
    text = specification(entry(id=A), entry(id=B), entry(id=C, rests_on=(A,)), written=True)
    assert text.index("/r/" + A) < text.index("/r/" + B) < text.index("/r/" + C)
    assert 'class="depth-1"' not in text


def test_spec_cross_area_line() -> None:
    text = specification(entry(id=A), entry(id=B, area="other", rests_on=(A,)))
    assert 'rests on <a href="/r/' + A + '">' + A + "</a> (storage)" in text


def test_area_page_lists_decisions_entries_and_hidden_ids() -> None:
    make, _ = staged_world()
    text = server.render(make, urlsplit("/spec?area=storage"), TOKEN)[1]
    assert "Decisions behind this area, not yet confirmed" in text
    assert 'name="id" value="d-cccccc"' in text and 'name="area" value="storage"' in text
    assert "Reword transcripts" in text and "/r/" + A in text and "(storage)" in text
    assert 'href="/spec?area=storage&amp;order=written"' in text
    assert 'href="/spec?area=storage"' in text


def test_area_page_without_unconfirmed_has_no_form() -> None:
    make, _ = staged_world()
    make().confirm(["d-cccccc"], "Read.")
    assert "<form" not in server.render(make, urlsplit("/spec?area=storage"), TOKEN)[1]


def test_waiting_page_has_both_groups() -> None:
    make, _ = staged_world()
    send(make, "/threads", about=A, kind="question", text="For agent")
    make().ask("d-cccccc", Raises.DOUBT, "reviewer", "For author")
    text = server.render(make, urlsplit("/waiting"), TOKEN)[1]
    assert "<h1>Waiting</h1>" in text
    assert text.index("Waiting for an agent") < text.index("Waiting for the author")
    assert "/r/s-aaaaaa#q-111111" in text and "Transcripts are kept" in text
    assert "Reword transcripts" in text and "Doubt" in text and "Question" in text
    assert "open" in text and "1 message" in text and "last by reviewer" in text
