from dataclasses import replace

import pytest
from builders import area, at, decision, entry
from fakes import MemoryStore
from support import wired

from lodge.app import AddOutcome, LodgeError, NotFound, StaleList
from lodge.core import Action, Change, Decision, Scope, Tree, load

AGENT = decision(id="d-aaaaaa", changes=(Change("s-aaaaaa", Action.CREATE),))
OTHER = decision(id="d-bbbbbb", date=at(1), changes=(Change("s-bbbbbb", Action.CREATE),))


def store_for(*, staged: bool = False) -> MemoryStore:
    return MemoryStore(area(), entry(id="s-aaaaaa"), AGENT, staged=staged)


def made(store: MemoryStore) -> Decision:
    return load(Tree(None, store.files)).decisions["d-111111"]


def test_confirm_one_decision() -> None:
    store = store_for()
    result = wired(store).confirm([AGENT.id], "Read.")
    assert result.outcome is AddOutcome.PUBLISHED
    assert made(store).decided_by == "author"
    assert made(store).confirms == (AGENT.id,)
    quote = made(store).quote
    assert quote and quote.when == "2026-10-29 09:30"
    assert store.commits == []


def test_confirm_writes_only_a_new_decision_file() -> None:
    store = store_for()
    before = set(store.files)
    wired(store).confirm([AGENT.id], "Read.")
    paths = tuple(store.publishes[0][0])
    assert len(paths) == 1
    assert all(p.startswith("lodge/decisions/") and p not in before for p in paths)


def test_confirmed_decision_keeps_decided_by_and_clears_its_flag() -> None:
    author = decision(id="d-cccccc", decided_by="author", date=at(0))
    agent = replace(AGENT, date=at(1), narrows=(author.id,))
    store = MemoryStore(area(), entry(id="s-aaaaaa"), author, agent)
    lodge = wired(store)
    assert lodge.waiting_all()[0].items
    lodge.confirm([agent.id], "Read.")
    assert load(Tree(None, store.files)).decisions[agent.id].decided_by == agent.decided_by
    assert lodge.waiting_all()[0].items == ()


def test_scope_product_when_any_listed_is_product() -> None:
    store = MemoryStore(
        area(),
        entry(id="s-aaaaaa"),
        entry(id="s-bbbbbb"),
        AGENT,
        replace(OTHER, scope=Scope.PROCESS),
    )
    wired(store).confirm([AGENT.id, OTHER.id], "Read.", "storage")
    assert made(store).scope is Scope.PRODUCT


def test_scope_process_when_all_are_process() -> None:
    store = MemoryStore(replace(AGENT, scope=Scope.PROCESS, changes=()))
    wired(store).confirm([AGENT.id], "Read.")
    assert made(store).scope is Scope.PROCESS


def test_area_confirms_exactly_the_listed() -> None:
    store = MemoryStore(area(), entry(id="s-aaaaaa"), entry(id="s-bbbbbb"), AGENT, OTHER)
    wired(store).confirm([OTHER.id, AGENT.id], "Read.", "storage")
    assert made(store).confirms == (AGENT.id, OTHER.id)


def test_stale_area_list_writes_nothing() -> None:
    store = MemoryStore(area(), entry(id="s-aaaaaa"), entry(id="s-bbbbbb"), AGENT, OTHER)
    wired(store).confirm([OTHER.id], "Read.")
    store.publishes.clear()
    with pytest.raises(
        StaleList, match="the list changed since the page was loaded; nothing was written"
    ):
        wired(store).confirm([AGENT.id, OTHER.id], "Read.", "storage")
    assert store.publishes == []


def test_second_identical_confirmation_is_stale() -> None:
    store = store_for(staged=True)
    lodge = wired(store)
    lodge.confirm([AGENT.id], "Read.")
    with pytest.raises(StaleList):
        lodge.confirm([AGENT.id], "Read.")
    assert len(store.publishes) == 1


@pytest.mark.parametrize("words", ["", " \r\n\t"])
def test_words_required(words: str) -> None:
    store = store_for()
    with pytest.raises(LodgeError, match="your words are required; nothing was written"):
        wired(store).confirm([AGENT.id], words)
    assert store.publishes == []


def test_words_with_specials_kept_verbatim() -> None:
    store = store_for()
    words = (
        'Read: "yes" \\ # [x]\r\n\tCaveat: café.\rInside.\n## Reasoning\nMore.\n---\nStill here.'
    )
    wired(store).confirm([AGENT.id], " \n" + words + " \n")
    expected = words.replace("\r\n", "\n")
    assert made(store).reasoning == expected
    quote = made(store).quote
    assert quote and quote.text == expected


def test_words_with_unstorable_character_refused() -> None:
    store = store_for()
    with pytest.raises(LodgeError, match="your words hold a character lodge cannot store"):
        wired(store).confirm([AGENT.id], "\x00")
    assert store.publishes == []


def test_commit_after_staged() -> None:
    store = store_for(staged=True)
    result = wired(store).confirm([AGENT.id], "Read.", commit=True)
    path = next(iter(store.publishes[0][0]))
    assert store.commits == [((path,), "Author confirmation from the viewer: d-111111")]
    assert result.committed == store.commit_result


def test_behind_area_lists_entries_in_other_areas() -> None:
    agent = replace(
        AGENT,
        changes=(
            *AGENT.changes,
            Change("s-bbbbbb", Action.EDIT),
            Change("s-bbbbbb", Action.LINK),
            Change("s-cccccc", Action.EDIT),
        ),
    )
    store = MemoryStore(area(), entry(id="s-aaaaaa"), entry(id="s-bbbbbb", area="other"), agent)
    rows = wired(store).behind_area("storage")
    assert rows[0].decision.id == AGENT.id
    assert rows[0].entries == (("s-aaaaaa", "storage"), ("s-bbbbbb", "other"))
    with pytest.raises(NotFound):
        wired(store).behind_area("unknown")


def test_show_marks_confirmable() -> None:
    store = store_for()
    lodge = wired(store)
    assert lodge.show(AGENT.id).confirmable
    assert not lodge.show("s-aaaaaa").confirmable
    lodge.confirm([AGENT.id], "Read.")
    assert not lodge.show(AGENT.id).confirmable
    assert not lodge.show("d-111111").confirmable


@pytest.mark.parametrize("staged,commit", [(False, True), (True, False)])
def test_confirmation_does_not_commit_unless_staged_and_requested(
    staged: bool, commit: bool
) -> None:
    store = store_for(staged=staged)
    result = wired(store).confirm([AGENT.id], "Read.", commit=commit)
    assert result.outcome is (AddOutcome.STAGED if staged else AddOutcome.PUBLISHED)
    assert result.committed is None
    assert store.commits == []


def test_confirmation_failed_check_writes_and_commits_nothing() -> None:
    store = MemoryStore(replace(AGENT, date="2026-10-29T09:31:00+01:00"), staged=True)
    result = wired(store).confirm([AGENT.id], "Read.", commit=True)
    assert result.outcome is AddOutcome.CHECK_FAILED
    assert not result.check.ok
    assert store.publishes == []
    assert store.commits == []


def test_repeated_cr_before_lf_is_refused() -> None:
    store = store_for()
    with pytest.raises(LodgeError, match="your words hold a character lodge cannot store"):
        wired(store).confirm([AGENT.id], "a\r\r\nb")
    assert store.publishes == []


def test_second_area_confirmation_is_stale() -> None:
    store = store_for(staged=True)
    lodge = wired(store)
    lodge.confirm([AGENT.id], "Read.", "storage")
    with pytest.raises(StaleList):
        lodge.confirm([AGENT.id], "Read.", "storage")
    assert len(store.publishes) == 1


def test_duplicate_confirmation_ids_are_stale() -> None:
    store = store_for()
    with pytest.raises(StaleList):
        wired(store).confirm([AGENT.id, AGENT.id], "Read.", "storage")
    assert store.publishes == []
