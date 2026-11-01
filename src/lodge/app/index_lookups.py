"""Assemble CLI results from a single stored-state read transaction."""

from collections.abc import Mapping, Sequence
from dataclasses import replace

from lodge import core
from lodge.app.errors import LodgeError, NotFound
from lodge.app.index_types import Row, StoredState, level1_of
from lodge.app.ports import Index
from lodge.app.results import Read, Shown, ShownMany


class Miss(Exception):
    """The cache cannot prove this complete answer."""


class QueryFallback(Exception):
    """The query needs memory, while the stored state remains valid."""


class Lookups:
    def __init__(self, index: Index, state: StoredState, read: Read) -> None:
        self.index, self.state, self.read = index, state, read
        self.loaded: dict[str, tuple[Row, core.Decision | core.SpecEntry]] = {}

    def record(
        self, ident: str, ref: str | None = None
    ) -> tuple[Row, core.Decision | core.SpecEntry]:
        if ident not in self.loaded:
            rows = self.index.rows(self.state.key, [ident])
            if rows is None:
                raise Miss
            if ident not in rows:
                if ref is None:
                    raise Miss
                raise self.not_found(f"record named {ref}", ref)
            row = rows[ident]
            parses = self.index.parses([row.key])
            record = parses.get(row.key)
            if not isinstance(record, (core.Decision, core.SpecEntry)) or record.id != ident:
                raise Miss
            self.loaded[ident] = row, record
        return self.loaded[ident]

    def empty_candidates(self, rows: Mapping[str, Row]) -> list[core.Candidate]:
        # Empty-query ranking reads only filters, dates, and IDs from these views.
        return [
            core.Candidate(
                core.Level1(
                    ident,
                    "decision" if ident.startswith("d-") else "spec",
                    None,
                    "",
                    "",
                    row.status,
                    row.decided_by,
                    row.date,
                    row.scope,
                    row.area,
                    row.flags,
                    row.quote,
                ),
                row.areas,
                frozenset(),
                frozenset(),
            )
            for ident, row in rows.items()
        ]

    def view(self, ident: str) -> core.Level1:
        return level1_of(*self.record(ident))

    def resolve(self, ref: str) -> str:
        wanted = ref.strip().lower()
        if wanted.startswith(("d-", "s-")):
            try:
                self.record(wanted, ref)
            except NotFound:
                pass
            else:
                return wanted
        coded = self.state.codes.get(wanted, ())
        if len(coded) > 1:
            raise LodgeError(f"the code {ref} names more than one record: {', '.join(coded)}")
        if not coded:
            raise self.not_found(f"record named {ref}", ref)
        return coded[0]

    def not_found(self, what: str, needle: str) -> NotFound:
        paths = [p.path for p in self.read.unrecorded if p.check == 1]
        named = [p for p in paths if needle.strip().lower() in p.lower()] or paths
        suffix = f"; lodge could not read {', '.join(named)}, which may hold it" if named else ""
        return NotFound(f"no {what}{suffix}")

    def family(self, code: str) -> tuple[str, ...]:
        wanted = code.lower()
        pairs = [
            (c, i)
            for c, ids in self.state.codes.items()
            if c == wanted or c.startswith(wanted + ".")
            for i in ids
        ]
        return tuple(i for _, i in sorted(pairs, key=lambda p: (p[0] != wanted, *p)))

    def shown(self, ident: str, reasoning: bool, provenance: bool) -> Shown:
        row, record = self.record(ident)
        changing = (
            tuple(self.view(i) for i in row.changed_by)
            if reasoning and isinstance(record, core.SpecEntry)
            else ()
        )
        why = None
        if reasoning:
            why = (
                record.reasoning
                if isinstance(record, core.Decision)
                else "\n\n".join(
                    core.format_level1(replace(v, statement="", quote=None)).removesuffix("\n\n")
                    for v in changing
                )
            )
        source = None
        if provenance:
            source = (
                core.Level3(
                    record.quote,
                    record.numbers,
                    record.work_item,
                    record.attachments,
                    record.imported_from,
                    row.links,
                )
                if isinstance(record, core.Decision)
                else core.Level3(None, (), None, (), record.imported_from, row.links)
            )
        siblings: tuple[str, ...] = ()
        citing: tuple[str, ...] = ()
        count = 0
        if record.code:
            siblings = tuple(i for i in self.family(record.code) if i != ident)
            code = record.code.lower()
            found = self.index.citing(self.state.key, code, 10)
            count = self.state.citers.get(code, -1)
            if found is None or count < 0 or len(found) != min(10, count):
                raise Miss
            citing = found
        return Shown(
            self.view(ident),
            why,
            source,
            self.read,
            changing,
            siblings=tuple(self.view(i) for i in siblings[:10]),
            citers=tuple(self.view(i) for i in citing),
            left_out=(max(0, len(siblings) - 10), max(0, count - 10)),
        )

    def show_many(self, refs: Sequence[str], reasoning: bool, provenance: bool) -> ShownMany:
        seen: dict[str, Shown] = {}
        items: list[tuple[str, Shown | LodgeError]] = []
        for ref in refs:
            try:
                ident = self.resolve(ref)
                shown = (
                    replace(seen[ident], repeat=True)
                    if ident in seen
                    else self.shown(ident, reasoning, provenance)
                )
                seen[ident] = shown
                items.append((ref, shown))
            except LodgeError as error:
                items.append((ref, error))
        return ShownMany(tuple(items), self.read)
