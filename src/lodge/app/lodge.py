"""The operations every command and the viewer call."""

from collections.abc import Sequence
from typing import Literal

from lodge.app import confirm, reads, threads, writes
from lodge.app.ports import Clock, IdSource, Store
from lodge.app.results import (
    Added,
    Behind,
    Listed,
    Read,
    Shown,
    ThreadList,
    ThreadShown,
    ThreadsWaiting,
    Written,
)
from lodge.app.state import Wiring
from lodge.core import CheckResult, CoreSettings, Filters, Raises, SpecArea


class Lodge:
    def __init__(self, store: Store, clock: Clock, ids: IdSource, settings: CoreSettings) -> None:
        self._w = Wiring(store, clock, ids, settings)

    def search(self, query: str, filters: Filters, limit: int = 20) -> Listed:
        return reads.search_records(self._w, query, filters, limit)

    def show(self, ref: str, reasoning: bool = False, provenance: bool = False) -> Shown:
        return reads.show(self._w, ref, reasoning, provenance)

    def waiting_all(self) -> tuple[Listed, ThreadsWaiting]:
        """Decisions and threads waiting, checked in the same snapshot."""
        return reads.waiting_all(self._w)

    def timeline(self, limit: int = 50) -> Listed:
        return reads.timeline(self._w, limit)

    def spec(self, area: str | None = None) -> tuple[str, Read, tuple[SpecArea, ...]]:
        """The Markdown, how fresh it is, and the same areas as structure."""
        return reads.spec(self._w, area)

    def problems(self) -> tuple[CheckResult, Read]:
        return self.check(gate=False)

    def check(self, gate: bool) -> tuple[CheckResult, Read]:
        return reads.check(self._w, gate)

    def draft(self, ref: str) -> str:
        """The file of `ref`, an ID, a code, or `area:<name>`, ready to edit and add."""
        return reads.draft(self._w, ref)

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

    def ask(
        self,
        ref: str,
        raises: Raises,
        by: str,
        text: str,
        where: str | None = None,
        when: str | None = None,
        commit: bool = False,
    ) -> Written:
        return threads.write(self._w, ref, raises, by, text, where, when, commit=commit)

    def reply(
        self,
        thread: str,
        by: str,
        text: str,
        where: str | None = None,
        when: str | None = None,
        commit: bool = False,
    ) -> Written:
        return threads.write(self._w, thread, None, by, text, where, when, commit=commit)

    def close(
        self,
        thread: str,
        by: str,
        text: str | None = None,
        where: str | None = None,
        when: str | None = None,
        commit: bool = False,
    ) -> Written:
        return threads.write(
            self._w, thread, None, by, text or "", where, when, commit=commit, close=True
        )

    def threads(self) -> ThreadList:
        return threads.list_open(self._w)

    def thread(self, ref: str) -> ThreadShown:
        return threads.show(self._w, ref)

    def threads_waiting(self) -> ThreadsWaiting:
        return threads.waiting(self._w)

    def confirm(
        self,
        ids: Sequence[str],
        words: str,
        area: str | None = None,
        commit: bool = False,
    ) -> Written:
        return confirm.confirm(self._w, ids, words, area, commit)

    def behind_area(self, name: str) -> tuple[Behind, ...]:
        return confirm.behind_area(self._w, name)
