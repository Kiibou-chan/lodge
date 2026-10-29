"""The operations every command and the viewer call."""

from collections.abc import Sequence
from typing import Literal

from lodge.app import reads, writes
from lodge.app.ports import Clock, IdSource, Store
from lodge.app.results import Added, Listed, Read, Shown
from lodge.app.state import Wiring
from lodge.core import CheckResult, CoreSettings, Filters, SpecArea


class Lodge:
    def __init__(self, store: Store, clock: Clock, ids: IdSource, settings: CoreSettings) -> None:
        self._w = Wiring(store, clock, ids, settings)

    def search(self, query: str, filters: Filters, limit: int = 20) -> Listed:
        return reads.search_records(self._w.store, query, filters, limit)

    def show(self, ref: str, reasoning: bool = False, provenance: bool = False) -> Shown:
        return reads.show(self._w.store, ref, reasoning, provenance)

    def waiting(self) -> Listed:
        return reads.waiting(self._w.store)

    def timeline(self, limit: int = 50) -> Listed:
        return reads.timeline(self._w.store, limit)

    def spec(self, area: str | None = None) -> tuple[str, Read, tuple[SpecArea, ...]]:
        """The Markdown, how fresh it is, and the same areas as structure."""
        return reads.spec(self._w.store, area)

    def problems(self) -> tuple[CheckResult, Read]:
        return self.check(gate=False)

    def check(self, gate: bool) -> tuple[CheckResult, Read]:
        return reads.check(self._w.store, self._w.clock, self._w.settings, gate)

    def draft(self, ref: str) -> str:
        """The file of `ref`, an ID, a code, or `area:<name>`, ready to edit and add."""
        return reads.draft(self._w.store, ref)

    def mint(self, prefix: Literal["d", "s"]) -> str:
        return writes.mint(self._w, prefix)

    def add(
        self,
        drafts: Sequence[tuple[str, str]],
        importing: bool = False,
        dry_run: bool = False,
        attachments: Sequence[tuple[str, str]] = (),
    ) -> Added:
        """Add `drafts`; `attachments`, (name, text) files, go beside the one decision created."""
        return writes.add(self._w, drafts, importing, dry_run, attachments)
