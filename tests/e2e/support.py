"""Draft texts for a made-up project, and records added through the command line."""

from dataclasses import dataclass

from e2e.conftest import Project

QUOTE = 'quote: {text: "Keep them.", where: "chat", when: "2026-10-29 10:00"}'


def document(header: list[str], body: str) -> str:
    return "---\n" + "\n".join(header) + "\n---\n\n" + body + "\n"


def decision_text(
    title: str = "Keep transcripts",
    *extra: str,
    decided_by: str = "coordinator",
    body: str = "Transcripts are kept.",
) -> str:
    header = ["kind: decision", f'title: "{title}"', "scope: product", f"decided_by: {decided_by}"]
    return document([*header, *extra], body)


def entry_text(entry_id: str, title: str = "Transcripts are kept", body: str = "Held.") -> str:
    return document(["kind: spec", f"id: {entry_id}", "area: storage", f'title: "{title}"'], body)


def area_text(*order: str) -> str:
    header = ["kind: area", "name: storage", 'title: "Storage"', f"order: [{', '.join(order)}]"]
    return document(header, "How data is kept.")


@dataclass(frozen=True)
class Seeded:
    decision: str
    entry: str


def first_decision(out: str) -> str:
    """The first decision ID on the last line of what `lodge add` printed."""
    return next(word for word in out.splitlines()[-1].split() if word.startswith("d-"))


def initialise(p: Project) -> None:
    assert p.run("init").code == 0


def seed(p: Project, *extra: str, decided_by: str = "coordinator", code: str = "ITEM-1") -> Seeded:
    """Initialise the store and add one decision that creates one entry in one area."""
    initialise(p)
    entry = p.run("id", "s").out.strip()
    header = [f"code: {code}", "changes:", f"  - {{entry: {entry}, action: create}}", *extra]
    files = [
        p.draft("decision.md", decision_text("Keep transcripts", *header, decided_by=decided_by)),
        p.draft("entry.md", entry_text(entry)),
        p.draft("area.md", area_text(entry)),
    ]
    added = p.run("add", *files)
    assert added.code == 0, added
    return Seeded(first_decision(added.out), entry)
