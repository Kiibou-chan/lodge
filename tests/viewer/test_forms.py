from html.parser import HTMLParser
from urllib.parse import urlencode

from builders import decision
from fakes import MemoryStore
from support import wired

from lodge.core import Raises
from lodge.viewer import forms, pages, spec, writes
from viewer.test_post_gate import HEADERS, TOKEN
from viewer.world import AGENT, staged_world, world


class Forms(HTMLParser):
    def __init__(self, text: str) -> None:
        super().__init__()
        self.forms: list[tuple[str, dict[str, str]]] = []
        self.feed(text)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        held = dict(attrs)
        if tag == "form":
            assert held["method"] == "post"
            self.forms.append((held["action"] or "", {}))
        if tag in {"input", "textarea"} and held.get("name"):
            self.forms[-1][1][held["name"] or ""] = held.get("value") or ""


def test_confirm_form_on_a_confirmable_decision() -> None:
    text = pages.record_page(world().show("d-cccccc"), TOKEN)
    assert 'action="/confirm"' in text and f'name="token" value="{TOKEN}"' in text
    assert 'name="words" required' in text and "Your words" in text and ">Confirm<" in text
    assert "The decision stays the agent&#x27;s, and your words are kept exactly as written" in text
    assert "read, not fully understood" in text


def test_no_confirm_form_on_author_confirmed_or_replaced_decisions() -> None:
    lodge = world()
    lodge.confirm(["d-cccccc"], "Read.")
    for ident in ("d-aaaaaa", "d-dddddd", "d-cccccc"):
        assert 'action="/confirm"' not in pages.record_page(lodge.show(ident), TOKEN)
    replaced = wired(MemoryStore(AGENT, decision(id="d-eeeeee", replaces=("d-cccccc",))))
    shown = replaced.show("d-cccccc")
    assert shown.level1.status == "replaced"
    text = pages.record_page(shown, TOKEN)
    assert 'action="/confirm"' not in text
    assert f'name="token" value="{TOKEN}"' in text


def test_doubt_and_question_forms_on_every_record() -> None:
    for ident in ("d-aaaaaa", "s-aaaaaa"):
        text = pages.record_page(world().show(ident), TOKEN)
        forms = Forms(text).forms
        assert [f[1]["kind"] for f in forms] == ["doubt", "question"]
        assert all(f[1]["about"] == ident for f in forms)
        assert "Raise a doubt" in text and "Ask a question" in text


def threaded(closed: bool = False) -> str:
    make, _ = staged_world()
    lodge = make()
    lodge.ask("s-aaaaaa", Raises.QUESTION, "author", "<script>Why?</script>", where="viewer")
    if closed:
        lodge.close("q-111111", "author", "", where="viewer")
    return pages.record_page(lodge.show("s-aaaaaa"), TOKEN)


def test_open_thread_has_reply_and_close() -> None:
    text = threaded()
    assert 'action="/threads/q-111111/reply"' in text
    assert 'action="/threads/q-111111/close"' in text
    assert ">Reply<" in text and ">Close<" in text


def test_closed_thread_has_neither() -> None:
    text = threaded(True)
    assert 'id="q-111111"' in text
    assert "/q-111111/reply" not in text and "/q-111111/close" not in text


def test_thread_text_is_escaped() -> None:
    text = threaded()
    assert "<script>" not in text and "&lt;script&gt;Why?&lt;/script&gt;" in text


def test_forms_post_to_relative_actions_only() -> None:
    forms = Forms(threaded()).forms
    assert len(forms) == 4
    for action, fields in forms:
        assert action.startswith("/") and not action.startswith("//")
        assert fields["token"] == TOKEN


def test_rendered_forms_post_through_handle_post() -> None:
    for which in ("decision", "area", "entry"):
        make, _ = staged_world()
        lodge = make()
        if which == "entry":
            lodge.ask("s-aaaaaa", Raises.QUESTION, "author", "Why?", where="viewer")
        if which == "area":
            _, read, areas = lodge.spec("storage")
            text = spec.spec_page(
                areas, read, TOKEN, "dependency", "storage", lodge.behind_area("storage")
            )
        else:
            text = pages.record_page(
                lodge.show("s-aaaaaa" if which == "entry" else "d-cccccc"), TOKEN
            )
        forms = Forms(text).forms
        assert len(forms) == {"decision": 3, "area": 1, "entry": 4}[which]
        for action, fields in forms:
            fresh, _ = staged_world()
            if which == "entry":
                fresh().ask("s-aaaaaa", Raises.QUESTION, "author", "Why?", where="viewer")
            fields = {k: ("Read." if k in {"words", "text"} else v) for k, v in fields.items()}
            expected = {"token", "words", "id"} if action == "/confirm" else {"token", "text"}
            if which == "area":
                expected.add("area")
            if action == "/threads":
                expected |= {"about", "kind"}
            assert set(fields) == expected
            reply = writes.handle_post(
                fresh,
                writes.Gatekeeper(TOKEN, writes.allowed_hosts(8787, ())),
                action,
                HEADERS,
                urlencode(fields).encode(),
            )
            assert reply.status == 303, reply.text


def test_confirm_note_matches_number_of_decisions() -> None:
    for ids in (("d-aaaaaa",), ("d-aaaaaa", "d-bbbbbb")):
        text = forms.confirm_form(ids, TOKEN, "storage")
        expected = (
            "The decision stays the agent" if len(ids) == 1 else "The decisions stay the agents"
        )
        assert expected in text
