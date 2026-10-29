"""Records and texts shared by the core tests; the project is made up."""

from lodge.core import Action, Change, Decision, Quote, Scope

DECISION_PATH = "lodge/decisions/d-3m8qk2-whole-transcripts-are-kept-before-a.md"
SPEC_PATH = "lodge/spec/storage/s-4kq1zm-transcripts-are-kept.md"
TITLE = "Whole transcripts are kept before a session is archived"

EXAMPLE = Decision(
    id="d-3m8qk2",
    title=TITLE,
    scope=Scope.PROCESS,
    decided_by="author",
    date="2026-10-28T23:48:10+01:00",
    statement="One to three sentences stating the decision.",
    reasoning="Why, in a few hundred words at most.",
    code="ITEM-1",
    changes=(Change("s-4kq1zm", Action.EDIT),),
    replaces=("d-8rw0te",),
    quote=Quote("Record it.", "first session", "2026-10-28 23:48"),
)

EXAMPLE_TEXT = f"""---
id: d-3m8qk2
kind: decision
code: ITEM-1
title: "{TITLE}"
scope: process
decided_by: author
date: 2026-10-28T23:48:10+01:00
changes:
  - {{entry: s-4kq1zm, action: edit}}
replaces: [d-8rw0te]
quote: {{text: "Record it.", where: "first session", when: "2026-10-28 23:48"}}
---

One to three sentences stating the decision.

## Reasoning

Why, in a few hundred words at most.
"""

BASE_HEADER = [
    "id: d-3m8qk2",
    "kind: decision",
    'title: "A title"',
    "scope: product",
    "decided_by: coordinator",
    "date: 2026-10-28T23:48:10+01:00",
]


def document(header: list[str], body: str = "A statement.") -> str:
    return "---\n" + "\n".join(header) + "\n---\n\n" + body + "\n"


def replaced(key: str, line: str | None) -> list[str]:
    """`BASE_HEADER` with the line for `key` swapped for `line`, or dropped when `line` is None."""
    kept = [row for row in BASE_HEADER if not row.startswith(f"{key}:")]
    return kept if line is None else [*kept, line]
