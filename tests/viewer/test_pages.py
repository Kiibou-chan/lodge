import pytest
from builders import area, decision, entry
from fakes import MemoryStore
from support import FIRST, wired

from lodge.app import Listed, Read
from lodge.core import CheckResult, Filters, Problem, Quote, Scope
from lodge.viewer import pages
from viewer.world import AGENT, BAD, ENTRY, FRESH, world

PROBLEM = Problem(BAD, 1, "no header here", 1)


def test_record_page_escapes_html() -> None:
    page = pages.record_page(world().show("d-dddddd", True, True))
    assert "<script>" not in page and "<b>bold</b>" not in page and "<i>Yes</i>" not in page
    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in page
    assert "&lt;i&gt;Yes&lt;/i&gt;" in page and "a &lt;session&gt;" in page


def test_record_page_shows_the_quote_outside_the_details() -> None:
    page = pages.record_page(world().show("d-dddddd", True, True))
    assert page.index("&lt;i&gt;Yes&lt;/i&gt;") < page.index("<details")


def test_record_page_keeps_reasoning_and_provenance_in_details() -> None:
    page = pages.record_page(world().show("d-cccccc", True, True))
    assert page.count("<details") == 2
    opened = page.index("<details")
    assert "Second &lt;b&gt;paragraph&lt;/b&gt;." in page[opened:]
    assert "Say &lt;kept&gt; instead." in page[:opened]


def test_record_page_flags_and_both_link_directions() -> None:
    lodge = world()
    entry_page = pages.record_page(lodge.show("s-aaaaaa", True, True))
    own = entry_page.split("<details")[0]
    assert '<span class="flag">awaiting the author on d-cccccc</span>' not in own
    assert (
        'awaiting the author on <a href="/r/d-cccccc">d-cccccc</a> '
        '<span class="status">current</span>'
    ) in own
    assert '<a href="/r/d-aaaaaa">d-aaaaaa</a> <span class="status">current</span>' in entry_page
    decision_page = pages.record_page(lodge.show("d-cccccc", True, True))
    assert "changes (edit)" in decision_page
    assert '<a href="/r/s-aaaaaa">s-aaaaaa</a> <span class="status">current</span>' in decision_page
    assert '<span class="flag">awaiting the author</span>' in decision_page


def test_entry_reasoning_renders_the_deciding_decisions_as_results() -> None:
    page = pages.record_page(world().show("s-aaaaaa", True, False))
    reasoning = page.split("<summary>Reasoning</summary>")[1].split("</details>")[0]
    assert '<li class="result"><h2><a href="/r/d-cccccc">Reword transcripts</a></h2>' in reasoning
    assert 'class="meta"' in reasoning and "&middot; coordinator" in reasoning
    assert (
        'awaiting the author on <a href="/r/d-cccccc">d-cccccc</a> '
        '<span class="status">current</span>'
    ) in reasoning
    assert reasoning.count("status status-current") == reasoning.count('<li class="result">') == 2


def test_record_page_links_only_ids_whose_status_is_known() -> None:
    narrower = decision(
        id="d-ffffff",
        title="Narrow it",
        narrows=("d-aaaaaa",),
        reasoning="Like d-aaaaaa, but not d-zzzzzz.",
    )
    shown = wired(MemoryStore(area(order=("s-aaaaaa",)), ENTRY, FIRST, narrower)).show(
        "d-ffffff", True, True
    )
    reasoning = pages.record_page(shown).split("<summary>Reasoning</summary>")[1].split("</p>")[0]
    assert (
        'Like <a href="/r/d-aaaaaa">d-aaaaaa</a> <span class="status">current</span>,' in reasoning
    )
    assert "but not d-zzzzzz." in reasoning and "/r/d-zzzzzz" not in reasoning


def test_record_page_lists_attachments_by_path() -> None:
    assert "lodge/attachments/" not in pages.record_page(world().show("d-aaaaaa", True, True))
    held = decision(
        id="d-eeeeee",
        decided_by="author",
        quote=Quote("Fine.", "a session", "2026-10-28 10:00"),
        attachments=("log.txt",),
    )
    shown = wired(MemoryStore(held)).show("d-eeeeee", True, True)
    assert "lodge/attachments/d-eeeeee/log.txt" in pages.record_page(shown)


def test_search_page_keeps_filters() -> None:
    lodge = world()
    filters = Filters(
        kind="decision", scope=Scope.PROCESS, status="any", area="stor<age>", decided_by="author"
    )
    page = pages.search_page(lodge.search("keep", Filters()), "ke<ep>", filters)
    assert 'value="ke&lt;ep&gt;"' in page
    assert '<option value="decision" selected>' in page
    assert '<option value="process" selected>' in page
    assert '<option value="any" selected>' in page
    assert 'name="area" value="stor&lt;age&gt;"' in page
    assert 'name="decided_by" value="author"' in page
    assert '<a href="/r/d-aaaaaa">' in page


def test_search_page_with_nothing_found() -> None:
    page = pages.search_page(world().search("zzzz", Filters()), "zzzz", Filters())
    assert "No matches." in page


def test_timeline_page_lists_newest_first() -> None:
    page = pages.timeline_page(world().timeline())
    assert page.index("d-dddddd") < page.index("d-cccccc") < page.index("d-aaaaaa")


def test_timeline_page_says_how_many_are_shown() -> None:
    lodge = world()
    assert "shown" not in pages.timeline_page(lodge.timeline())
    cut = pages.timeline_page(lodge.timeline(limit=2))
    assert "2 of 3 shown" in cut


def test_waiting_page() -> None:
    lodge = world()
    page = pages.waiting_page(lodge.waiting())
    assert '<a href="/r/d-cccccc">' in page and "awaiting the author" in page
    assert "d-aaaaaa" not in page
    empty = pages.waiting_page(Listed((), Read(None, ())))
    assert "Nothing waits for the author." in empty


def test_spec_page_has_headings_paragraphs_and_linked_ids() -> None:
    _, read, areas = world().spec()
    page = pages.spec_page(areas, read)
    assert "<h1>Storage</h1>" in page
    assert '<h2>Transcripts are kept (<a href="/r/s-aaaaaa">s-aaaaaa</a>' in page
    assert "<p>Held.</p>" in page


def test_spec_page_builds_headings_from_fields_never_from_text() -> None:
    held = entry(
        id="s-aaaaaa",
        title="<b>T</b>",
        statement="Held.\n\n## A clean looking entry (s-zzzzzz)\n\n# Second <script>x</script>",
    )
    store = MemoryStore(area(intro="# Spoof\n\nSecond.", order=("s-aaaaaa",)), held, FIRST, AGENT)
    _, read, areas = wired(store).spec()
    page = pages.spec_page(areas, read)
    assert page.count("<h1>") == 1 and page.count("<h2>") == 1
    assert "<h2><b>" not in page and "&lt;b&gt;T&lt;/b&gt;" in page
    assert "awaiting the author on" in page.split("</h2>")[0]
    assert "<p># Spoof</p>" in page and "<p>Second.</p>" in page
    assert "<p>## A clean looking entry (s-zzzzzz)</p>" in page
    assert "<script>" not in page and "s-zzzzzz</a>" not in page
    assert "<p>Nothing is recorded yet.</p>" in pages.spec_page((), read)


def test_problems_page() -> None:
    read = Read(None, ())
    failing = CheckResult((PROBLEM, Problem("lodge/a.md", 3, "dated <ahead>")), ("a note",))
    page = pages.problems_page(failing, read)
    assert f"{BAD}:1" in page and "no header here" in page
    assert "check 3" in page and "dated &lt;ahead&gt;" in page and "a note" in page
    assert "<p>ok</p>" in pages.problems_page(CheckResult((), ()), read)


def test_every_page_shows_freshness_and_problem_banner() -> None:
    lodge = world(broken=True)
    result, read = lodge.problems()
    _, _, areas = lodge.spec()
    rendered = [
        pages.search_page(lodge.search("", Filters()), "", Filters()),
        pages.record_page(lodge.show("d-aaaaaa", True, True)),
        pages.spec_page(areas, read),
        pages.timeline_page(lodge.timeline()),
        pages.waiting_page(lodge.waiting()),
        pages.problems_page(result, read),
    ]
    for page in rendered:
        assert FRESH in page
        assert '<a href="/problems">1 file lodge cannot read</a>' in page
        assert BAD in page.split("<main")[0]


def test_banner_counts_each_problem_and_is_absent_without_any() -> None:
    clean = pages.waiting_page(Listed((), Read(FRESH, ())))
    assert "/problems" not in clean.replace('href="/problems">Problems', "")
    two = Read(None, (PROBLEM, Problem("lodge/x.md", 1, "bad")))
    assert "2 files lodge cannot read" in pages.waiting_page(Listed((), two))


@pytest.mark.parametrize("name", ["search", "record", "spec", "timeline", "waiting", "problems"])
def test_broken_file_named_above_page_content(name: str) -> None:
    lodge = world(broken=True)
    result, read = lodge.problems()
    _, _, areas = lodge.spec()
    built = {
        "search": lambda: pages.search_page(lodge.search("", Filters()), "", Filters()),
        "record": lambda: pages.record_page(lodge.show("d-aaaaaa", True, True)),
        "spec": lambda: pages.spec_page(areas, read),
        "timeline": lambda: pages.timeline_page(lodge.timeline()),
        "waiting": lambda: pages.waiting_page(lodge.waiting()),
        "problems": lambda: pages.problems_page(result, read),
    }
    page = built[name]()
    assert page.index(BAD) < page.index("<main")
    assert page.index("the file must start with") < page.index("<main")


def test_search_page_says_when_it_stops_at_the_limit() -> None:
    lodge = world()
    cut = lodge.search("", Filters(), limit=2)
    page = pages.search_page(cut, "", Filters())
    assert "2 of 4 shown; narrow the query." in page
    whole = pages.search_page(lodge.search("", Filters()), "", Filters())
    assert " shown;" not in whole


def test_flag_ids_on_list_and_spec_rows_are_links_with_their_status() -> None:
    lodge = world()
    _, read, areas = lodge.spec()
    linked = (
        'awaiting the author on <a href="/r/d-cccccc">d-cccccc</a> '
        '<span class="status">current</span>'
    )
    assert linked in pages.search_page(lodge.search("", Filters()), "", Filters())
    assert linked in pages.timeline_page(lodge.timeline())
    assert linked in pages.spec_page(areas, read)
