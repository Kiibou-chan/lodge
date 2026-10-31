"""The readable specification: the areas as structure, and that structure as Markdown."""

import re
from dataclasses import dataclass

from lodge.core.derive import Derived
from lodge.core.order import area_names, derived_order, written_order
from lodge.core.snapshot import Snapshot
from lodge.core.views import Level1, level1

_HEADING_LINE = re.compile(r"^( {0,3})(#|=+[ \t]*$|-+[ \t]*$)", re.MULTILINE)


@dataclass(frozen=True)
class Placed:
    """A displayed entry with dependency placement and additional links."""

    entry: Level1
    depth: int
    under: str | None
    also: tuple[str, ...]
    across: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class SpecArea:
    """One area with its title, intro, written entries, and derived placements."""

    name: str
    title: str
    intro: str
    entries: tuple[Level1, ...]
    placed: tuple[Placed, ...]


def spec_view(
    s: Snapshot, d: Derived, failing: frozenset[str], area: str | None = None
) -> tuple[SpecArea, ...]:
    """Areas by rank and name, with written entries and their dependency placements."""
    names = area_names(s)
    return tuple(_area(s, d, failing, name) for name in names if area is None or area == name)


def render_spec(s: Snapshot, d: Derived, failing: frozenset[str], area: str | None = None) -> str:
    """The areas as Markdown; an entry that level 1 flags carries its flags in the heading.

    A line of an intro or statement that starts with `#`, up to three spaces in, or is made of
    `=` or `-` gets a backslash, so no record text reads as a heading.
    """
    blocks: list[str] = []
    for held in spec_view(s, d, failing, area):
        blocks.append(f"# {held.title}")
        if held.intro:
            blocks.append(_escaped(held.intro))
        for p in held.placed:
            links = "".join(f"\nrests on {target} ({other})" for target, other in p.across)
            blocks.append(_entry_block(p.entry) + links)
    return "".join(f"{block}\n\n" for block in blocks).removesuffix("\n")


def _area(s: Snapshot, d: Derived, failing: frozenset[str], name: str) -> SpecArea:
    held = s.areas.get(name)
    shown = {i: level1(s, d, i, failing) for i in written_order(s, d, name)}
    entries = tuple(shown.values())
    placed = []
    for p in derived_order(s, d, name):
        targets = tuple(dict.fromkeys(s.entries[p.id].rests_on))
        also = tuple(
            t
            for t in targets
            if t != p.under
            and t in s.entries
            and s.entries[t].area == name
            and d.status.get(t) == "current"
        )
        across = tuple(
            (t, s.entries[t].area) for t in targets if t in s.entries and s.entries[t].area != name
        )
        placed.append(Placed(shown[p.id], p.depth, p.under, also, across))
    return SpecArea(
        name, held.title if held else name, held.intro if held else "", entries, tuple(placed)
    )


def _entry_block(v: Level1) -> str:
    marks = " · ".join((v.id, *v.flags))
    return f"## {v.title} ({marks})\n\n{_escaped(v.statement)}"


def _escaped(text: str) -> str:
    return _HEADING_LINE.sub(r"\1\\\2", text)
