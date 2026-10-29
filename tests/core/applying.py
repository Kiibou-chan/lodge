"""Drafts and states for the tests of `apply_drafts`; the project is made up."""

from builders import tree_of
from samples import document

from lodge.core import (
    Applied,
    Area,
    Decision,
    Draft,
    Problem,
    Snapshot,
    SpecEntry,
    Tree,
    apply_drafts,
    load,
    parse_draft,
)

NOW = "2026-10-29T09:30:00+01:00"


def drafted(*texts: str) -> list[Draft]:
    drafts = [parse_draft(f"draft{i}.md", text) for i, text in enumerate(texts)]
    assert all(isinstance(d, Draft) for d in drafts), drafts
    return [d for d in drafts if isinstance(d, Draft)]


def decision_text(*extra: str, body: str = "It is kept.") -> str:
    return document(
        [
            "kind: decision",
            'title: "Keep transcripts"',
            "scope: process",
            "decided_by: coordinator",
            *extra,
        ],
        body,
    )


def spec_text(*header: str, body: str = "They are kept.") -> str:
    return document(["kind: spec", 'title: "Transcripts"', *header], body)


def area_text(*header: str, body: str = "Intro.") -> str:
    return document(["kind: area", 'title: "Storage"', *header], body)


def state(*items: Decision | SpecEntry | Area) -> tuple[Snapshot, Tree]:
    tree = tree_of(*items)
    return load(tree), tree


def apply(
    s: Snapshot, tree: Tree, *texts: str, ids: tuple[str, ...] = (), importing: bool = False
) -> Applied | list[Problem]:
    return apply_drafts(s, tree, drafted(*texts), ids, NOW, importing)


def applied(result: Applied | list[Problem]) -> Applied:
    assert isinstance(result, Applied), result
    return result


def problems(result: Applied | list[Problem]) -> list[Problem]:
    assert isinstance(result, list), result
    return result
