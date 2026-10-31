"""A made-up project for the viewer tests: one author decision, an agent edit awaiting her."""

from collections.abc import Callable

from builders import area, at, decision, entry
from fakes import MemoryStore
from support import FIRST, wired

from lodge.app import Lodge
from lodge.core import Action, Change, Quote

BAD = "lodge/decisions/d-bbbbbb-broken.md"
FRESH = "fetched 2026-10-29T08:00:00+00:00"

ENTRY = entry(id="s-aaaaaa", area="storage", title="Transcripts are kept", statement="Held.")
AGENT = decision(
    id="d-cccccc",
    title="Reword transcripts",
    statement="Say <kept> instead.",
    reasoning="First paragraph.\n\nSecond <b>paragraph</b>.",
    changes=(Change("s-aaaaaa", Action.EDIT),),
    date=at(10),
)
SCRIPT = decision(
    id="d-dddddd",
    title="Use <b>bold</b> sparingly",
    statement="<script>alert(1)</script>",
    decided_by="author",
    quote=Quote("<i>Yes</i>", "a <session>", "2026-10-28 10:00"),
    date=at(20),
)


def world(broken: bool = False) -> Lodge:
    store = MemoryStore(area(order=("s-aaaaaa",)), ENTRY, FIRST, AGENT, SCRIPT)
    if broken:
        store.files[BAD] = "no header here\n"
    return wired(store)


def staged_world() -> tuple[Callable[[], Lodge], MemoryStore]:
    store = MemoryStore(area(order=("s-aaaaaa",)), ENTRY, FIRST, AGENT, SCRIPT, staged=True)
    return lambda: wired(store), store
