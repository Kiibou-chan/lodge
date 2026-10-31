from datetime import timedelta

import pytest
from applying import area_text, decision_text, spec_text
from builders import at, decision, entry
from fakes import START, CountingIds, FixedClock, MemoryStore
from support import AREA, FIRST, project, wired

from lodge.app import AddOutcome, Conflict, LodgeError
from lodge.core import Feedback, Tree, check_state, load, parse_record

NEW_DECISION = decision_text("changes:", "  - {entry: s-bbbbbb, action: create}")
NEW_ENTRY = spec_text("id: s-bbbbbb", "area: storage", body="Everything is kept.")
PAIR = [("decision.md", NEW_DECISION), ("entry.md", NEW_ENTRY)]
MADE_ENTRY = "lodge/spec/storage/s-bbbbbb-transcripts.md"
MADE_DECISION = "lodge/decisions/d-111111-keep-transcripts.md"


def test_add_new_decision_entry_area() -> None:
    store = MemoryStore()
    drafts = [*PAIR, ("area.md", area_text("name: storage"))]
    added = wired(store).add(drafts)
    assert added.outcome is AddOutcome.PUBLISHED
    assert added.ids == ("d-111111", "s-bbbbbb")
    assert sorted(store.files) == [MADE_DECISION, "lodge/spec/storage/_area.md", MADE_ENTRY]
    assert store.publishes[0][1] == "lodge: add d-111111, s-bbbbbb Keep transcripts"
    assert check_state(load(Tree(None, store.files))).ok


def test_add_fills_id_and_date_from_ports() -> None:
    store = MemoryStore(AREA)
    clock = FixedClock(START.replace(microsecond=999_999))
    wired(store, clock, CountingIds(first=7)).add(PAIR)
    made = parse_record("x", store.files["lodge/decisions/d-777777-keep-transcripts.md"])
    assert made.id == "d-777777" and made.date == "2026-10-29T09:30:00+01:00"  # type: ignore[union-attr]


def test_add_date_and_check_time_from_one_reading() -> None:
    clock = FixedClock(step=timedelta(seconds=1))
    added = wired(MemoryStore(AREA), clock).add(PAIR)
    assert added.outcome is AddOutcome.PUBLISHED
    assert clock.calls == 1


def test_add_stale_base_conflicts_writes_nothing() -> None:
    store = project()
    stale = wired(store).draft("s-aaaaaa").replace("base: ", "base: 000")
    with pytest.raises(Conflict, match="it changed since the draft was made") as raised:
        wired(store).add([("edit.md", stale)])
    assert raised.value.exit_code == 1
    assert store.publishes == [] and store.attempts == 0


def test_add_failing_check_publishes_nothing() -> None:
    store = project()
    added = wired(store).add([("entry.md", NEW_ENTRY)])
    assert added.outcome is AddOutcome.CHECK_FAILED
    assert [p.check for p in added.check.problems] == [4]
    assert store.attempts == 0 and store.publishes == []


def test_add_returns_feedback_and_notes() -> None:
    added = wired(project()).add(PAIR)
    assert added.outcome is AddOutcome.PUBLISHED
    assert [f.record_id for f in added.feedback] == ["d-111111"]
    assert "d-aaaaaa" in added.feedback[0].message
    assert added.check.notes == ("area storage: order changed",)


def test_add_refuses_unreadable_or_unusable_drafts() -> None:
    store = project()
    broken = ("broken.md", "---\ntitle: [unclosed\n---\n")
    with pytest.raises(LodgeError, match=r"broken\.md:2") as raised:
        wired(store).add([broken])
    assert raised.value.exit_code == 2
    with pytest.raises(LodgeError, match=r"entry\.md.*needs an area"):
        wired(store).add([("entry.md", spec_text("id: s-bbbbbb"))])
    with pytest.raises(LodgeError, match="no drafts"):
        wired(store).add([])
    assert store.attempts == 0


def test_add_imports_only_when_asked() -> None:
    imported = decision_text("imported_from: {file: notes.md, heading: Storage}")
    with pytest.raises(LodgeError, match="--import"):
        wired(project()).add([("d.md", imported)])
    added = wired(project()).add([("d.md", imported)], importing=True)
    assert added.outcome is AddOutcome.CHECK_FAILED


def test_dry_run_publishes_nothing() -> None:
    store = project()
    added = wired(store).add(PAIR, dry_run=True)
    assert added.outcome is AddOutcome.DRY_RUN
    assert store.attempts == 0 and store.files == project().files


def test_dry_run_reports_feedback_and_check() -> None:
    real, dry = wired(project()).add(PAIR), wired(project()).add(PAIR, dry_run=True)
    assert (dry.ids, dry.feedback, dry.check) == (real.ids, real.feedback, real.check)
    failing = wired(project()).add([("entry.md", NEW_ENTRY)], dry_run=True)
    assert failing.outcome is AddOutcome.CHECK_FAILED


def test_feedback_skips_edited_decisions_which_the_check_refuses() -> None:
    wordy = decision(
        id="d-cccccc",
        title="Wordy",
        statement=" ".join(["word"] * 100),
        reasoning="First part.\n\nSecond part.",
        date=at(5),
    )
    long_entry = entry(id="s-aaaaaa", area="storage", title="Transcripts are kept")
    store = MemoryStore(AREA, long_entry, FIRST, wordy)
    lodge = wired(store)
    shorter = lodge.draft("d-cccccc").replace("\n\nSecond part.", "")
    longer = lodge.draft("s-aaaaaa").replace("What holds now.", " ".join(["word"] * 160))
    edit = decision_text("changes:", "  - {entry: s-aaaaaa, action: edit}")
    added = lodge.add([("a.md", shorter), ("b.md", longer), ("c.md", edit)])
    assert added.outcome is AddOutcome.CHECK_FAILED
    assert [p.check for p in added.check.problems] == [5]
    noted = {f.record_id for f in added.feedback}
    assert "s-aaaaaa" in noted and "d-cccccc" not in noted


def test_staged_second_edit_builds_on_first() -> None:
    store = project(staged=True)
    lodge = wired(store)
    edit = decision_text("changes:", "  - {entry: s-aaaaaa, action: edit}")
    for step, (old, new) in enumerate([("Held.", "Second."), ("Second.", "Third.")]):
        draft = lodge.draft("s-aaaaaa").replace(old, new)
        added = lodge.add([("e.md", draft), ("d.md", edit)])
        assert added.outcome is AddOutcome.STAGED, step
    path = next(p for p in store.files if p.startswith("lodge/spec/storage/s-"))
    assert "Third." in store.files[path]
    assert "Held." in store.published[path]
    assert sum(p.startswith("lodge/decisions/d-") for p in store.files) == 3


def test_mint_skips_taken() -> None:
    taken = decision(id="d-111111", date=at(5))
    ids = CountingIds()
    assert wired(MemoryStore(FIRST, taken), ids=ids).mint("d") == "d-222222"
    assert ids.draws == 2
    assert wired(MemoryStore(AREA, entry(id="s-111111")), ids=CountingIds()).mint("s") == "s-222222"


def test_mint_gives_up_after_ten_draws() -> None:
    ids = CountingIds(step=0)
    with pytest.raises(LodgeError, match="ten"):
        wired(MemoryStore(decision(id="d-111111", date=at(5))), ids=ids).mint("d")
    assert ids.draws == 10


def test_unchanged_draft_publishes_nothing() -> None:
    store = project()
    lodge = wired(store)
    added = lodge.add([("e.md", lodge.draft("s-aaaaaa")), ("a.md", lodge.draft("area:storage"))])
    assert added.outcome is AddOutcome.UNCHANGED
    assert added.check.notes == ()
    assert store.attempts == 0 and store.publishes == []


def test_only_changed_files_are_published() -> None:
    store = project()
    lodge = wired(store)
    edited = lodge.draft("s-aaaaaa").replace("Held.", "Changed.")
    edit = decision_text("changes:", "  - {entry: s-aaaaaa, action: edit}")
    lodge.add([("e.md", edited), ("a.md", lodge.draft("area:storage")), ("d.md", edit)])
    written = sorted(store.publishes[0][0])
    assert "lodge/spec/storage/_area.md" not in written and len(written) == 2


def test_add_area_sharing_a_rank_gives_feedback() -> None:
    store = MemoryStore()
    lodge = wired(store)
    lodge.add([("a.md", area_text("name: other", "rank: 1"))])
    added = lodge.add([("b.md", area_text("name: storage", "rank: 1"))])
    assert added.outcome is not AddOutcome.CHECK_FAILED
    assert (
        Feedback(
            "area:storage",
            "rank 1 is shared with area other; areas that share a rank are ordered by name",
        )
        in added.feedback
    )


def test_cycle_made_in_one_add_is_refused() -> None:
    store = project()
    lodge = wired(store)
    a = lodge.draft("s-aaaaaa").replace("---\n", "---\nrests_on: [s-bbbbbb]\n", 1)
    b = spec_text("id: s-bbbbbb", "area: storage", "rests_on: [s-aaaaaa]")
    d = decision_text("changes: [{entry: s-aaaaaa, action: link}, {entry: s-bbbbbb, action: link}]")
    added = lodge.add([("a.md", a), ("b.md", b), ("d.md", d)])
    assert added.outcome is AddOutcome.CHECK_FAILED
    assert len([p for p in added.check.problems if p.check == 8]) == 2
    assert store.publishes == []


def test_rest_on_entry_retired_in_the_same_add_is_refused() -> None:
    store = project()
    b = spec_text("id: s-bbbbbb", "area: storage", "rests_on: [s-aaaaaa]")
    d = decision_text(
        "changes: [{entry: s-aaaaaa, action: retire}, {entry: s-bbbbbb, action: create}]"
    )
    added = wired(store).add([("b.md", b), ("d.md", d)])
    assert added.outcome is AddOutcome.CHECK_FAILED
    assert any(p.check == 6 for p in added.check.problems)
    assert store.publishes == []
