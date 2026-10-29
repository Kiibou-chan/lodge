"""What each command prints, as lines of text."""

import re
from collections.abc import Collection, Sequence

from lodge.app import Added, AddOutcome, Listed, Read, Shown
from lodge.core import CheckResult, Level1, Problem, format_level1, format_level3

NO_MATCHES = "no matches"
NOTHING_WAITS = "nothing waits for the author"
NOTHING_RECORDED = "Nothing is recorded yet."
DECISION_DRAFT_NOTE = (
    "note: decisions are immutable; to change one, write a new decision with replaces or narrows"
)


def is_decision_file(text: str) -> bool:
    """Whether a record file's header says `kind: decision`."""
    header = text.split("\n---\n", 1)[0].splitlines()
    return "kind: decision" in (line.strip() for line in header)


def read_lines(read: Read) -> list[str]:
    """The freshness line, then a line for each file lodge cannot read."""
    first = [] if read.freshness is None else [read.freshness]
    return [*first, *(f"problem: {_where(p)}: {p.message}" for p in read.unrecorded)]


def listed_text(listed: Listed, empty: str) -> str:
    lines = [*read_lines(listed.read), _blocks(listed.items, empty)]
    if listed.more:
        total = len(listed.items) + listed.more
        lines.append(
            f"{len(listed.items)} of {total} shown; narrow the query or give --limit {total}"
        )
    return "\n".join(lines)


def shown_text(shown: Shown) -> str:
    sections = [format_level1(shown.level1)]
    if shown.level2 is not None:
        sections.append(_section("Reasoning", shown.level2))
    if shown.level3 is not None:
        sections.append(_section("Provenance", format_level3(shown.level3)))
    return "\n".join([*read_lines(shown.read), "\n\n".join(sections)])


def check_lines(result: CheckResult, already_shown: Collection[Problem] = ()) -> list[str]:
    """Problems, or `ok`, then the notes."""
    problems = [p for p in result.problems if p not in already_shown]
    head = [f"check {p.check}: {p.message}" for p in problems]
    if result.ok:
        head = ["ok"]
    return [*head, *(f"note: {note}" for note in result.notes)]


def added_lines(added: Added, dry_run: bool) -> list[str]:
    provisional = set(added.minted) if dry_run else set()
    lines = [
        f"feedback: {f.record_id}{' (provisional)' if f.record_id in provisional else ''}: "
        f"{f.message}"
        for f in added.feedback
    ]
    lines += [f"note: {note}" for note in added.check.notes]
    lines += [f"check {p.check}: {_marked(p.message, provisional)}" for p in added.check.problems]
    ids = " ".join(added.ids)
    if added.outcome in (AddOutcome.PUBLISHED, AddOutcome.STAGED):
        lines.append(f"{added.outcome.value} {ids}".rstrip())
    elif added.outcome is AddOutcome.UNCHANGED:
        lines.append(added.outcome.value)
    elif added.outcome is AddOutcome.CHECK_FAILED:
        lines += [] if added.freshness is None else [added.freshness]
        lines.append("not published: the check failed")
    if dry_run:
        lines.append("dry run: nothing published")
    return lines


def _marked(text: str, provisional: set[str]) -> str:
    """`text` with each provisional ID followed by `(provisional)`."""
    for record_id in provisional:
        text = re.sub(
            rf"\b{re.escape(record_id)}\b(?! \(provisional\))", f"{record_id} (provisional)", text
        )
    return text


def _blocks(items: Sequence[Level1], empty: str) -> str:
    return "\n\n".join(format_level1(item) for item in items) if items else empty


def _section(heading: str, text: str) -> str:
    return f"## {heading}\n\n{text or 'none recorded'}"


def _where(problem: Problem) -> str:
    return f"{problem.path}:{problem.line}" if problem.line else problem.path
