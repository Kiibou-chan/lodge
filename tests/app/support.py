"""A small made-up project and the application wired to the fakes."""

from builders import area, at, decision, entry
from fakes import CountingIds, FixedClock, MemoryStore

from lodge.app import Lodge
from lodge.core import Action, Change, CoreSettings

AREA = area(name="storage", title="Storage", intro="How it keeps data.", order=("s-aaaaaa",))
ENTRY = entry(id="s-aaaaaa", area="storage", title="Transcripts are kept", statement="Held.")
FIRST = decision(
    id="d-aaaaaa",
    title="Keep whole transcripts",
    code="ITEM-1",
    decided_by="author",
    reasoning="Because they are evidence.",
    changes=(Change("s-aaaaaa", Action.CREATE),),
    date=at(0),
)


def project(staged: bool = False) -> MemoryStore:
    return MemoryStore(AREA, ENTRY, FIRST, staged=staged)


def wired(
    store: MemoryStore, clock: FixedClock | None = None, ids: CountingIds | None = None
) -> Lodge:
    return Lodge(store, clock or FixedClock(), ids or CountingIds(), CoreSettings())
