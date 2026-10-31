"""The checks that one state of the store answers alone: 1, 2, 3, 7, and 8."""

from collections.abc import Iterator
from dataclasses import dataclass

from lodge.core.check_areas import check_areas
from lodge.core.check_cycles import check_cycles
from lodge.core.derive import is_author
from lodge.core.model import Decision, Problem, Record
from lodge.core.snapshot import Snapshot, attachment_path


@dataclass(frozen=True)
class CheckResult:
    """What a check found: problems fail it, notes are printed."""

    problems: tuple[Problem, ...]
    notes: tuple[str, ...]

    @property
    def ok(self) -> bool:
        return not self.problems


def check_state(s: Snapshot) -> CheckResult:
    found = [
        *s.problems,
        *_file_names(s),
        *_unresolved(s),
        *_codes(s),
        *_attachments(s),
        *_quotes(s),
        *_confirmations(s),
        *check_areas(s),
        *check_cycles(s),
    ]
    return CheckResult(tuple(sorted(found, key=sort_key)), ())


def sort_key(p: Problem) -> tuple[str, int, str]:
    return (p.path, p.check, p.message)


def problem_at(s: Snapshot, record_id: str, check: int, message: str) -> Problem:
    """A problem about the record `record_id`, at its path."""
    return Problem(s.paths.get(record_id, ""), check, f"{record_id}: {message}")


def decisions(s: Snapshot) -> Iterator[Decision]:
    """Every decision, by ID."""
    yield from (s.decisions[i] for i in sorted(s.decisions))


def new_decisions(published: Snapshot, after: Snapshot) -> list[Decision]:
    """The decisions of `after` that `published` does not hold, by ID."""
    return [d for d in decisions(after) if d.id not in published.decisions]


def records(s: Snapshot) -> Iterator[Record]:
    """Every record, decisions first, each kind by ID."""
    yield from decisions(s)
    yield from (s.entries[i] for i in sorted(s.entries))


def _file_names(s: Snapshot) -> Iterator[Problem]:
    for record in (*records(s), *s.threads.values()):
        name = s.paths[record.id].rsplit("/", 1)[-1]
        if name != f"{record.id}.md" and not name.startswith(f"{record.id}-"):
            yield problem_at(s, record.id, 1, f"the file name {name} does not start with the ID")


def _unresolved(s: Snapshot) -> Iterator[Problem]:
    for t in s.threads.values():
        if t.about not in s.decisions and t.about not in s.entries:
            yield problem_at(s, t.id, 2, f"about {t.about}, which does not exist")
    for e in sorted(s.entries.values(), key=lambda e: e.id):
        for target in dict.fromkeys(e.rests_on):
            if target == e.id:
                yield problem_at(s, e.id, 2, "rests_on itself")
            elif target not in s.entries:
                yield problem_at(s, e.id, 2, f"rests_on {target}, which does not exist")
    for d in decisions(s):
        targets = [
            ("changes", dict.fromkeys(c.entry for c in d.changes), s.entries),
            ("replaces", dict.fromkeys(d.replaces), s.decisions),
            ("narrows", dict.fromkeys(d.narrows), s.decisions),
            ("confirms", dict.fromkeys(d.confirms), s.decisions),
        ]
        for key, ids, known in targets:
            for target in ids:
                if target == d.id:
                    yield problem_at(s, d.id, 2, f"{key} itself")
                elif target not in known:
                    yield problem_at(s, d.id, 2, f"{key} {target}, which does not exist")


def _codes(s: Snapshot) -> Iterator[Problem]:
    by_code: dict[str, list[Record]] = {}
    for record in records(s):
        if record.code is not None:
            by_code.setdefault(record.code.casefold(), []).append(record)
    for group in by_code.values():
        if len(group) > 1:
            for record in group:
                message = (
                    f"code {record.code} is shared with another record, "
                    "compared without regard to case"
                )
                yield problem_at(s, record.id, 2, message)


def _attachments(s: Snapshot) -> Iterator[Problem]:
    for d in decisions(s):
        for name in dict.fromkeys(d.attachments):
            if attachment_path(d.id, name) not in s.attachments:
                message = (
                    f"lists attachment {name}, which does not exist; pass the file with --attach"
                )
                yield problem_at(s, d.id, 2, message)


def _quotes(s: Snapshot) -> Iterator[Problem]:
    for d in decisions(s):
        if not is_author(d) and "author" in d.decided_by.strip().casefold():
            message = (
                f"decided_by is {d.decided_by}; "
                "write author exactly, with a quote, or use your own role"
            )
            yield problem_at(s, d.id, 3, message)
        if not is_author(d) or d.imported_from is not None:
            continue
        if d.quote is None:
            message = (
                "decided_by is author, but there is no quote; "
                "add quote: {text, where, when} with the author's words, "
                "or record it under your own role"
            )
            yield problem_at(s, d.id, 3, message)
            continue
        for key, value in (("where", d.quote.where), ("when", d.quote.when)):
            if not value.strip():
                yield problem_at(s, d.id, 3, f"quote.{key} is empty")


def _confirmations(s: Snapshot) -> Iterator[Problem]:
    for d in decisions(s):
        if d.confirms and not is_author(d):
            yield problem_at(
                s, d.id, 3, f"confirms is for author decisions, but decided_by is {d.decided_by}"
            )
