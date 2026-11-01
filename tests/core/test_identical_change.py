"""The change check adds no problems when a snapshot is compared with itself."""

from dataclasses import replace

import pytest
from builders import area, at, decision, entry, files_of, snapshot_of, thread
from checks import LATER, NOTES, NOW, OLD, SETTINGS, SPEC, creates, published, state
from linear_fixtures import chain, fifty_areas
from samples import DECISION_PATH, EXAMPLE, EXAMPLE_TEXT

from lodge.core import (
    Action,
    Change,
    Imported,
    Snapshot,
    ThreadState,
    Tree,
    check_change,
    load,
)


def snapshots() -> list[Snapshot]:
    """Samples, the change-check builders' cases, and deliberately defective states."""
    bad = decision(id="d-bbbbbb", decided_by="author", quote=None, date=at(1))
    new = entry(id="s-bbbbbb", title="Another")
    live = decision(id="d-bbbbbb", date=at(5), changes=(Change(SPEC, Action.EDIT),))
    imported = decision(
        id="d-cccccc", date=at(1), changes=(Change(SPEC, Action.EDIT),), imported_from=NOTES
    )
    imported_entry = replace(new, imported_from=NOTES)
    first_import = creates(new.id, id="d-bbbbbb", date=at(5), imported_from=NOTES)
    second_import = decision(
        id="d-cccccc", date=at(1), changes=(Change(new.id, Action.EDIT),), imported_from=NOTES
    )
    placed = area(order=(SPEC, new.id))
    samples = [
        snapshot_of(),
        snapshot_of(EXAMPLE),
        load(Tree(None, {DECISION_PATH: EXAMPLE_TEXT})),
        published(),
        state(),
        state(placed, new, creates(new.id, id="d-bbbbbb", date=LATER)),
        state(bad),
        state(bad, decision(id="d-cccccc", replaces=("d-zzzzzz",), date=LATER)),
        state(decision(id="d-bbbbbb", replaces=("d-zzzzzz",), date=LATER)),
        state(drop=(OLD,)),
        state(live),
        state(live, imported),
        state(placed, imported_entry, first_import),
        state(placed, imported_entry, first_import, second_import),
        state(area(order=(SPEC,), title="Renamed")),
        state(area(order=(SPEC,), intro="Words.")),
        state(area(order=()), decision(changes=(Change(SPEC, Action.RETIRE),), date=LATER)),
        state(decision(date=NOW.isoformat())),
        state(decision(date="2026-10-29T11:00:00+00:00")),
        state(area(name="other")),
        state(area(order=(SPEC,), rank=1)),
        fifty_areas(),
        chain(20),
        state(decision(id=OLD, statement="A hand edit already in the published state.")),
        load(
            Tree(None, files_of(decision(id=OLD, title="First"), decision(id=OLD, title="Second")))
        ),
        state(entry(id=SPEC, rests_on=(new.id,)), replace(new, rests_on=(SPEC,)), placed),
        state(entry(id=SPEC, rests_on=(new.id,)), new, area(order=(SPEC, new.id))),
        state(decision(changes=(Change(SPEC, Action.LINK),), date=LATER)),
        state(decision(imported_from=Imported("unlisted.md", "Berths"))),
        state(replace(new, imported_from=Imported("unlisted.md", "Cranes"))),
        snapshot_of(thread(about=OLD), thread(about=SPEC, state=ThreadState.CLOSED)),
        load(Tree(None, {"lodge/decisions/d-bbbbbb-broken.md": "---\ninvalid\n"})),
    ]
    for verb in ("replaces", "narrows", "confirms"):
        for date in (at(0), "2026-10-28T09:00:00+00:00", LATER):
            samples.append(state(decision(decided_by="author", date=date, **{verb: (OLD,)})))
    samples.extend(
        [
            state(decision(date="2026-10-28T09:30:00+00:00", replaces=(OLD,))),
            state(
                decision(date=at(0), changes=(Change(SPEC, Action.EDIT),)),
                entry(id=SPEC, statement="Now this."),
            ),
            state(decision(date="2026-01-01T00:00:00+00:00", replaces=(OLD,), imported_from=NOTES)),
        ]
    )
    for source in (None, NOTES):
        future = decision(date="2027-10-28T11:00:00+01:00", imported_from=source)
        samples.append(state(future))
        samples.append(
            state(
                replace(future, changes=(Change(SPEC, Action.EDIT),)),
                entry(id=SPEC, statement="Now."),
            )
        )
    return samples


CASE_IDS = [
    "empty",
    "example",
    "parsed-example",
    "published",
    "state",
    "created-entry",
    "author-without-quote",
    "bad-author-and-missing-replacement",
    "missing-replacement",
    "missing-old",
    "live-edit",
    "import-over-live",
    "imported-entry",
    "repeated-import",
    "renamed-area",
    "area-intro",
    "retired-entry",
    "now",
    "later-today",
    "other-area",
    "ranked-area",
    "fifty-areas",
    "chain",
    "published-hand-edit",
    "duplicate-id",
    "dependency-cycle",
    "dependency",
    "link",
    "unlisted-decision-source",
    "unlisted-entry-source",
    "threads",
    "broken-header",
    *(
        f"{verb}-{when}"
        for verb in ("replaces", "narrows", "confirms")
        for when in ("earlier-day", "earlier-time", "later")
    ),
    "replacement-same-time",
    "earlier-edit",
    "earlier-imported-replacement",
    "future-decision",
    "future-edit",
    "future-imported-decision",
    "future-imported-edit",
]


@pytest.mark.parametrize("snapshot", snapshots(), ids=CASE_IDS)
def test_check_change_of_a_state_with_itself_is_empty(snapshot: Snapshot) -> None:
    assert check_change(snapshot, snapshot, SETTINGS, NOW).problems == ()
