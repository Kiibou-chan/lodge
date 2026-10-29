import pytest
from applying import area_text, decision_text, spec_text
from builders import area, at, decision, entry, files_of
from fakes import MemoryStore
from support import AREA, project, wired

from lodge.app import AddOutcome, Conflict, LodgeError
from lodge.core import Action, Change, Tree, check_state, load

NEW = [
    ("d.md", decision_text("changes:", "  - {entry: s-bbbbbb, action: create}")),
    ("s.md", spec_text("id: s-bbbbbb", "area: storage", body="Everything is kept.")),
]
CONCURRENT = files_of(
    area(
        name="storage",
        title="Storage",
        intro="How it keeps data.",
        order=("s-aaaaaa", "s-cccccc"),
    ),
    entry(id="s-cccccc", area="storage", title="Another entry"),
    decision(id="d-cccccc", changes=(Change("s-cccccc", Action.CREATE),), date=at(20)),
)
NOISE = [{f"lodge/attachments/d-aaaaaa/{i}.txt": "x"} for i in range(5)]


def test_add_retry_keeps_concurrent_entry() -> None:
    store = project()
    store.reject_next(CONCURRENT)
    added = wired(store).add(NEW)
    assert added.outcome is AddOutcome.PUBLISHED
    assert store.attempts == 2
    s = load(Tree(None, store.files))
    assert s.areas["storage"].order == ("s-aaaaaa", "s-cccccc", "s-bbbbbb")
    assert {"d-cccccc", added.ids[0]} <= set(s.decisions)
    assert check_state(s).ok


def test_add_retry_concurrent_edit_of_same_entry_conflicts() -> None:
    store = project()
    lodge = wired(store)
    draft = lodge.draft("s-aaaaaa").replace("Held.", "Mine.")
    edit = decision_text("changes:", "  - {entry: s-aaaaaa, action: edit}")
    path = next(p for p in store.files if p.startswith("lodge/spec/storage/s-"))
    store.reject_next({path: store.files[path].replace("Held.", "Theirs.")})
    with pytest.raises(Conflict, match="it changed since the draft was made"):
        lodge.add([("e.md", draft), ("d.md", edit)])
    assert store.publishes == [] and store.attempts == 1
    assert "Theirs." in store.files[path]


def test_add_gives_up_after_three() -> None:
    store = MemoryStore(AREA)
    store.reject_next(*NOISE[:4])
    with pytest.raises(Conflict, match="three times") as raised:
        wired(store).add(NEW)
    assert raised.value.exit_code == 1
    assert store.attempts == 3 and store.publishes == []


def test_ref_moving_between_reads_retries() -> None:
    store = MemoryStore(AREA)
    store.moves_after_read(NOISE[0])
    added = wired(store).add(NEW)
    assert added.outcome is AddOutcome.PUBLISHED
    assert store.attempts == 2
    assert "lodge/attachments/d-aaaaaa/0.txt" in store.files


def test_area_created_by_another_add_is_a_conflict() -> None:
    store = MemoryStore()
    store.reject_next(files_of(area(name="storage", title="Storage")))
    drafts = [*NEW, ("a.md", area_text("name: storage"))]
    with pytest.raises(Conflict) as raised:
        wired(store).add(drafts)
    assert raised.value.exit_code == 1 and store.publishes == []


def test_entry_created_by_another_add_is_a_conflict() -> None:
    store = MemoryStore(AREA)
    store.reject_next(
        files_of(
            entry(id="s-bbbbbb", area="storage", title="Theirs"),
            decision(id="d-cccccc", changes=(Change("s-bbbbbb", Action.CREATE),), date=at(20)),
        )
    )
    with pytest.raises(Conflict) as raised:
        wired(store).add(NEW)
    assert raised.value.exit_code == 1
    assert store.attempts == 1 and store.publishes == []


def test_refusal_on_the_first_attempt_is_a_usage_error() -> None:
    store = MemoryStore(AREA)
    store.reject_next(NOISE[0])
    with pytest.raises(LodgeError) as raised:
        wired(store).add([("e.md", spec_text("id: s-bbbbbb"))])
    assert not isinstance(raised.value, Conflict) and raised.value.exit_code == 2
    assert store.attempts == 0


@pytest.mark.parametrize(
    "text",
    [
        area_text("name: [a, b]"),
        spec_text("id: [s-bbbbbb]", "area: storage"),
        spec_text("id: {x: 1}", "area: storage"),
    ],
    ids=["area-name-list", "entry-id-list", "entry-id-mapping"],
)
def test_unhashable_names_are_usage_errors(text: str) -> None:
    store = project()
    with pytest.raises(LodgeError) as raised:
        wired(store).add([("x.md", text)])
    assert not isinstance(raised.value, Conflict)
