from builders import area, at, decision, entry, snapshot_of
from checks import NOTES

from lodge.core import Action, Change, derive, render_spec, spec_view

NONE: frozenset[str] = frozenset()


def test_render_spec_skips_retired_follows_order() -> None:
    first = entry(id="s-aaaaaa", title="First", statement="One.", area="storage")
    second = entry(id="s-bbbbbb", title="Second", statement="Two.", area="storage")
    gone = entry(id="s-cccccc", title="Gone", statement="Three.", area="storage")
    loose = entry(id="s-dddddd", title="Loose", statement="Four.", area="storage")
    other = entry(id="s-eeeeee", title="Other", statement="Five.", area="access")
    kill = decision(id="d-aaaaaa", changes=(Change("s-cccccc", Action.RETIRE),), date=at(1))
    s = snapshot_of(
        area(
            name="storage",
            title="Storage",
            intro="How it keeps data.",
            order=("s-bbbbbb", "s-aaaaaa", "s-cccccc"),
        ),
        area(name="access", title="Access", intro="", order=("s-eeeeee",)),
        first,
        second,
        gone,
        loose,
        other,
        kill,
    )
    d = derive(s)
    assert render_spec(s, d, NONE) == (
        "# Access\n\n"
        "## Other (s-eeeeee)\n\nFive.\n\n"
        "# Storage\n\n"
        "How it keeps data.\n\n"
        "## Second (s-bbbbbb)\n\nTwo.\n\n"
        "## First (s-aaaaaa)\n\nOne.\n\n"
        "## Loose (s-dddddd)\n\nFour.\n"
    )
    assert render_spec(s, d, NONE, "access") == "# Access\n\n## Other (s-eeeeee)\n\nFive.\n"
    assert render_spec(s, d, NONE, "nowhere") == ""


def test_render_spec_entry_without_area_file_and_empty_store() -> None:
    s = snapshot_of(entry(id="s-aaaaaa", title="Lone", statement="Alone.", area="misc"))
    assert render_spec(s, derive(s), NONE) == "# misc\n\n## Lone (s-aaaaaa)\n\nAlone.\n"
    empty = snapshot_of()
    assert render_spec(empty, derive(empty), NONE) == ""


def test_render_spec_marks_flagged_failing_and_imported_entries() -> None:
    plain = entry(id="s-aaaaaa", title="Plain", statement="One.")
    flagged = entry(id="s-bbbbbb", title="Flagged", statement="Two.")
    imported = entry(id="s-cccccc", title="Old", statement="Three.", imported_from=NOTES)
    change = (Change("s-bbbbbb", Action.EDIT),)
    author = decision(id="d-aaaaaa", decided_by="author", date=at(0), changes=change)
    agent = decision(id="d-bbbbbb", date=at(1), changes=change)
    s = snapshot_of(
        area(order=("s-aaaaaa", "s-bbbbbb", "s-cccccc")), plain, flagged, imported, author, agent
    )
    got = render_spec(s, derive(s), frozenset({"s-aaaaaa"}))
    assert got == (
        "# Storage\n\n"
        "## Plain (s-aaaaaa \u00b7 fails check)\n\nOne.\n\n"
        "## Flagged (s-bbbbbb \u00b7 awaiting the author on d-bbbbbb)\n\nTwo.\n\n"
        "## Old (s-cccccc \u00b7 imported)\n\nThree.\n"
    )


def test_spec_view_gives_areas_with_level_one_entries_in_order() -> None:
    first = entry(id="s-aaaaaa", title="First", statement="One.")
    second = entry(id="s-bbbbbb", title="Second", statement="Two.")
    other = entry(id="s-cccccc", title="Other", statement="Three.", area="access")
    s = snapshot_of(
        area(intro="How it keeps data.", order=("s-bbbbbb", "s-aaaaaa")),
        area(name="access", title="Access", order=("s-cccccc",)),
        first,
        second,
        other,
    )
    d = derive(s)
    view = spec_view(s, d, NONE)
    assert [(a.name, a.title, a.intro) for a in view] == [
        ("access", "Access", ""),
        ("storage", "Storage", "How it keeps data."),
    ]
    assert [[v.id for v in a.entries] for a in view] == [["s-cccccc"], ["s-bbbbbb", "s-aaaaaa"]]
    assert view[1].entries[0].statement == "Two."
    assert [a.name for a in spec_view(s, d, NONE, "access")] == ["access"]
    assert spec_view(s, d, NONE, "nowhere") == ()


def test_render_spec_escapes_lines_that_start_with_a_hash() -> None:
    held = entry(
        id="s-aaaaaa", title="Held", statement="One.\n\n## Fake (s-zzzzzz)\n\nUnder it.\n# Also"
    )
    s = snapshot_of(area(intro="# Spoof\nPlain.", order=("s-aaaaaa",)), held)
    assert render_spec(s, derive(s), NONE) == (
        "# Storage\n\n"
        "\\# Spoof\nPlain.\n\n"
        "## Held (s-aaaaaa)\n\nOne.\n\n\\## Fake (s-zzzzzz)\n\nUnder it.\n\\# Also\n"
    )


def test_render_spec_escapes_indented_hashes_and_underline_headings() -> None:
    held = entry(
        id="s-aaaaaa",
        title="Held",
        statement="One.\n   ## Fake\nTitle\n===\nOther\n---  \n\n----\nlast",
    )
    s = snapshot_of(area(intro="Intro\n---", order=("s-aaaaaa",)), held)
    assert render_spec(s, derive(s), NONE) == (
        "# Storage\n\n"
        "Intro\n\\---\n\n"
        "## Held (s-aaaaaa)\n\n"
        "One.\n   \\## Fake\nTitle\n\\===\nOther\n\\---  \n\n\\----\nlast\n"
    )


def test_render_spec_follows_rank_then_derived_order() -> None:
    s = snapshot_of(
        area(rank=0, order=("s-aaaaaa", "s-bbbbbb")),
        area(name="access"),
        entry(id="s-aaaaaa", title="Later", rests_on=("s-bbbbbb",)),
        entry(id="s-bbbbbb", title="First"),
    )
    text = render_spec(s, derive(s), NONE)
    assert text.index("# Storage") < text.index("## First") < text.index("## Later")
    assert [a.name for a in spec_view(s, derive(s), NONE)] == ["storage", "access"]


def test_render_spec_lists_cross_area_targets() -> None:
    s = snapshot_of(
        entry(id="s-aaaaaa", statement="Held.", rests_on=("s-bbbbbb",)),
        entry(id="s-bbbbbb", area="other"),
    )
    assert "Held.\nrests on s-bbbbbb (other)" in render_spec(s, derive(s), NONE)


def test_spec_view_places_with_depth_under_and_also() -> None:
    s = snapshot_of(
        area(order=("s-aaaaaa", "s-bbbbbb", "s-cccccc")),
        entry(id="s-aaaaaa"),
        entry(id="s-bbbbbb"),
        entry(id="s-cccccc", rests_on=("s-aaaaaa", "s-bbbbbb")),
    )
    view = spec_view(s, derive(s), NONE)[0]
    p = view.placed[2]
    assert (p.entry.id, p.depth, p.under, p.also, p.across) == (
        "s-cccccc",
        1,
        "s-bbbbbb",
        ("s-aaaaaa",),
        (),
    )
    assert tuple(e.id for e in view.entries) == ("s-aaaaaa", "s-bbbbbb", "s-cccccc")


def test_cross_area_target_is_across_not_also() -> None:
    s = snapshot_of(
        entry(id="s-aaaaaa"),
        entry(id="s-bbbbbb", area="other"),
        entry(id="s-cccccc", rests_on=("s-bbbbbb", "s-aaaaaa")),
    )
    p = spec_view(s, derive(s), NONE, "storage")[0].placed[1]
    assert (p.under, p.also, p.across) == ("s-aaaaaa", (), (("s-bbbbbb", "other"),))
