from collections.abc import Callable

import pytest
from builders import area, at, decision, entry
from fakes import MemoryStore
from support import AREA, ENTRY, FIRST, project, wired

from lodge.app import Gate, Lodge, LodgeError, NotFound, Read, core_settings
from lodge.core import Action, Change, Filters, Quote, Tree, content_hash

BAD = "lodge/decisions/d-bbbbbb-broken.md"


def test_show_of_an_entry_carries_the_deciding_views_with_its_reasoning() -> None:
    lodge = wired(project())
    assert lodge.show("s-aaaaaa").changing == ()
    assert lodge.show("d-aaaaaa", reasoning=True).changing == ()
    entry_views = lodge.show("s-aaaaaa", reasoning=True).changing
    assert [v.id for v in entry_views] == ["d-aaaaaa"]


def test_show_resolves_code_and_levels() -> None:
    lodge = wired(project())
    shown = lodge.show("item-1")
    assert (shown.level1.id, shown.level1.code, shown.level1.decided_by) == (
        "d-aaaaaa",
        "ITEM-1",
        "author",
    )
    assert shown.level2 is None and shown.level3 is None
    full = lodge.show("D-AAAAAA", reasoning=True, provenance=True)
    assert full.level2 == "Because they are evidence."
    assert full.level3 is not None and full.level3.quote == Quote(
        "Do it.", "a session", "2026-10-28 10:00"
    )
    assert full.read.freshness == "fetched 2026-10-29T08:00:00+00:00"


def test_show_unknown_ref_is_an_error() -> None:
    with pytest.raises(NotFound, match="no record named nothing") as raised:
        wired(project()).show("nothing")
    assert raised.value.exit_code == 2


def test_show_ambiguous_code_is_an_error() -> None:
    twin = decision(id="d-cccccc", code="item-1", date=at(5))
    with pytest.raises(LodgeError, match="more than one record") as raised:
        wired(MemoryStore(area(), FIRST, twin)).show("ITEM-1")
    assert not isinstance(raised.value, NotFound)


def test_show_flags_a_failing_record() -> None:
    unquoted = decision(id="d-cccccc", decided_by="author", quote=None, date=at(5))
    shown = wired(MemoryStore(FIRST, unquoted)).show("d-cccccc")
    assert "fails check" in shown.level1.flags


def test_search_listed_with_read() -> None:
    listed = wired(project()).search("transcripts", Filters())
    assert [v.id for v in listed.items] == ["s-aaaaaa", "d-aaaaaa"]
    assert listed.read.freshness == "fetched 2026-10-29T08:00:00+00:00"
    assert listed.read.unrecorded == ()


def test_search_honours_filters() -> None:
    listed = wired(project()).search("", Filters(kind="decision"))
    assert [v.id for v in listed.items] == ["d-aaaaaa"]


def _broken() -> MemoryStore:
    store = project()
    store.files[BAD] = "no header here\n"
    return store


@pytest.mark.parametrize(
    "read",
    [
        lambda lodge: lodge.search("", Filters()).read,
        lambda lodge: lodge.show("d-aaaaaa").read,
        lambda lodge: lodge.waiting().read,
        lambda lodge: lodge.timeline().read,
        lambda lodge: lodge.spec()[1],
        lambda lodge: lodge.problems()[1],
        lambda lodge: lodge.check(gate=False)[1],
        lambda lodge: lodge.check(gate=True)[1],
    ],
    ids=["search", "show", "waiting", "timeline", "spec", "problems", "check", "gate"],
)
def test_unparsable_file_reported_by_every_read(read: Callable[[Lodge], Read]) -> None:
    assert [p.path for p in read(wired(_broken())).unrecorded] == [BAD]


def test_waiting_lists_flagged() -> None:
    agent = decision(
        id="d-cccccc",
        title="Reword transcripts",
        changes=(Change("s-aaaaaa", Action.EDIT),),
        date=at(10),
    )
    listed = wired(
        MemoryStore(area(order=("s-aaaaaa",)), entry(id="s-aaaaaa"), FIRST, agent)
    ).waiting()
    assert [v.id for v in listed.items] == ["d-cccccc"]
    assert "awaiting the author" in listed.items[0].flags
    assert wired(project()).waiting().items == ()


def test_timeline_newest_first_and_limited() -> None:
    later = [
        decision(id=f"d-{c}{c}{c}{c}{c}{c}", title=f"Later {c}", date=at(i))
        for i, c in ((5, "c"), (9, "d"), (7, "e"))
    ]
    store = MemoryStore(FIRST, *later)
    assert [v.id for v in wired(store).timeline().items] == [
        "d-dddddd",
        "d-eeeeee",
        "d-cccccc",
        "d-aaaaaa",
    ]
    cut = wired(store).timeline(limit=2)
    assert [v.id for v in cut.items] == ["d-dddddd", "d-eeeeee"] and cut.more == 2
    assert wired(store).timeline().more == 0


def test_spec_renders_and_narrows_to_an_area() -> None:
    other = entry(id="s-bbbbbb", area="access", title="Open to all", statement="Anyone.")
    access = area(name="access", title="Access", order=("s-bbbbbb",))
    store = MemoryStore(area(order=("s-aaaaaa",)), entry(id="s-aaaaaa"), access, other, FIRST)
    lodge = wired(store)
    text, read, areas = lodge.spec()
    assert "# Access" in text and "## An entry (s-aaaaaa)" in text and read.unrecorded == ()
    assert [(a.name, [v.id for v in a.entries]) for a in areas] == [
        ("access", ["s-bbbbbb"]),
        ("storage", ["s-aaaaaa"]),
    ]
    assert lodge.spec("access")[0] == "# Access\n\n## Open to all (s-bbbbbb)\n\nAnyone.\n"
    assert [a.name for a in lodge.spec("access")[2]] == ["access"]
    with pytest.raises(NotFound, match="no area named nowhere"):
        lodge.spec("nowhere")


def test_problems_run_the_one_state_checks() -> None:
    unquoted = decision(id="d-cccccc", decided_by="author", quote=None, date=at(5))
    result, _ = wired(MemoryStore(AREA, ENTRY, FIRST, unquoted)).problems()
    assert [p.check for p in result.problems] == [3]


def test_check_gate_compares_with_the_published_state() -> None:
    store = project(staged=True)
    path = next(p for p in store.files if p.startswith("lodge/spec/storage/s-"))
    store.files[path] = store.files[path].replace("Held.", "Changed.")
    plain, _ = wired(store).check(gate=False)
    gate, _ = wired(store).check(gate=True)
    assert [p.check for p in plain.problems] == [p.check for p in gate.problems] == [4]


def _edited(store: MemoryStore, old: str, new: str) -> Tree:
    path = next(p for p in store.files if p.startswith("lodge/spec/storage/s-"))
    return Tree(None, {**store.files, path: store.files[path].replace(old, new)})


def test_check_gate_names_the_state_that_fails() -> None:
    store = project()
    bad = _edited(store, "Held.", "Changed.")
    store.gate_for = Gate(
        Tree(None, dict(store.files)),
        (("committed", bad), ("working tree", Tree(None, dict(store.files)))),
    )
    result, _ = wired(store).check(gate=True)
    assert [(p.check, p.message.split(":")[0]) for p in result.problems] == [(4, "committed")]
    assert result.problems[0].message.startswith("committed: s-aaaaaa: edited")


def test_check_gate_merges_a_problem_both_states_have() -> None:
    store = project()
    bad = _edited(store, "Held.", "Changed.")
    store.gate_for = Gate(
        Tree(None, dict(store.files)), (("committed", bad), ("working tree", bad))
    )
    result, _ = wired(store).check(gate=True)
    assert [
        p.message.startswith("committed and working tree: s-aaaaaa") for p in result.problems
    ] == [True]


def test_check_gate_prints_the_gate_notes() -> None:
    store = project()
    store.gate_for = Gate(
        Tree(None, dict(store.files)), (("", Tree(None, dict(store.files))),), ("hello",)
    )
    result, _ = wired(store).check(gate=True)
    assert result.ok and result.notes == ("hello",)


def _with_base(text: str) -> str:
    return text.replace("---\n", f"---\nbase: {content_hash(text)}\n", 1)


def test_draft_prints_file_with_base() -> None:
    store = project()
    entry_path = next(p for p in store.files if p.startswith("lodge/spec/storage/s-"))
    decision_path = next(p for p in store.files if p.startswith("lodge/decisions/"))
    assert wired(store).draft("s-aaaaaa") == _with_base(store.files[entry_path])
    assert wired(store).draft("item-1") == _with_base(store.files[decision_path])


def test_draft_area() -> None:
    store = project()
    text = wired(store).draft("area:storage")
    path = "lodge/spec/storage/_area.md"
    assert text.startswith(f"---\nname: storage\nbase: {content_hash(store.files[path])}\n")
    with pytest.raises(NotFound, match="no area named nowhere"):
        wired(store).draft("area:nowhere")
    with pytest.raises(NotFound, match="no record named nothing"):
        wired(store).draft("nothing")


def test_core_settings_error_becomes_lodge_error() -> None:
    assert core_settings({"length": {"title_chars": 50}}).length.title_chars == 50
    with pytest.raises(LodgeError, match="unknown key"):
        core_settings({"bogus": 1})


GHOST = "lodge/spec/ghost/_area.md"
UNREADABLE_DECISION = "lodge/decisions/d-aaaaaa-keep-whole-transcripts.md"


def _unreadable(path: str) -> MemoryStore:
    store = project()
    store.files[path] = "no header here\n"
    return store


@pytest.mark.parametrize(
    ("path", "call"),
    [
        (UNREADABLE_DECISION, lambda lodge: lodge.show("d-aaaaaa")),
        (UNREADABLE_DECISION, lambda lodge: lodge.draft("d-aaaaaa")),
        (GHOST, lambda lodge: lodge.spec("ghost")),
        (GHOST, lambda lodge: lodge.draft("area:ghost")),
    ],
    ids=["show", "draft", "spec", "draft-area"],
)
def test_not_found_names_the_files_lodge_cannot_read(
    path: str, call: Callable[[Lodge], object]
) -> None:
    with pytest.raises(NotFound, match=f"no .* named .*; lodge could not read {path}"):
        call(wired(_unreadable(path)))


def test_not_found_lists_all_unreadable_files_when_none_matches() -> None:
    store = _unreadable(GHOST)
    store.files["lodge/decisions/d-bbbbbb-other.md"] = "nothing\n"
    with pytest.raises(NotFound) as raised:
        wired(store).show("d-zzzzzz")
    assert f"lodge/decisions/d-bbbbbb-other.md, {GHOST}, which" in str(raised.value)


def test_timeline_refuses_a_negative_limit() -> None:
    with pytest.raises(LodgeError, match="limit"):
        wired(project()).timeline(limit=-1)


def test_not_found_does_not_call_a_missing_file_unreadable() -> None:
    store = MemoryStore(ENTRY, FIRST)
    assert [p.path for p in wired(store).search("", Filters()).read.unrecorded] == [
        "lodge/spec/storage/_area.md"
    ]
    with pytest.raises(NotFound) as raised:
        wired(store).show("d-zzzzzz")
    assert str(raised.value) == "no record named d-zzzzzz"


def test_search_says_how_many_more_matched_beyond_the_limit() -> None:
    many = [decision(id=f"d-0000{i:02d}", title="Cache", date=at(i)) for i in range(21)]
    lodge = wired(MemoryStore(area(), *many))
    cut = lodge.search("", Filters())
    assert (len(cut.items), cut.more) == (20, 1)
    assert lodge.search("cache", Filters()).more == 1
    assert lodge.search("", Filters(), limit=21).more == 0
    assert len(lodge.search("", Filters(), limit=21).items) == 21
