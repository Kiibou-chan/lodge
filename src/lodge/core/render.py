"""The readable specification: the areas as structure, and that structure as Markdown."""

import re
from dataclasses import dataclass

from lodge.core.derive import Derived
from lodge.core.snapshot import Snapshot
from lodge.core.views import Level1, level1

_HEADING_LINE = re.compile(r"^( {0,3})(#|=+[ \t]*$|-+[ \t]*$)", re.MULTILINE)


@dataclass(frozen=True)
class SpecArea:
    """One area of the specification: its title, intro, and current entries in order."""

    name: str
    title: str
    intro: str
    entries: tuple[Level1, ...]


def spec_view(
    s: Snapshot, d: Derived, failing: frozenset[str], area: str | None = None
) -> tuple[SpecArea, ...]:
    """Each area by name, its current entries in the area's order, the rest by ID after them."""
    names = sorted({*s.areas, *(e.area for e in s.entries.values())})
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
        blocks.extend(_entry_block(v) for v in held.entries)
    return "".join(f"{block}\n\n" for block in blocks).removesuffix("\n")


def _area(s: Snapshot, d: Derived, failing: frozenset[str], name: str) -> SpecArea:
    held = s.areas.get(name)
    current = {
        i: e for i, e in s.entries.items() if e.area == name and d.status.get(i) == "current"
    }
    ordered = [i for i in (held.order if held else ()) if i in current]
    ordered += sorted(set(current) - set(ordered))
    entries = tuple(level1(s, d, i, failing) for i in dict.fromkeys(ordered))
    return SpecArea(name, held.title if held else name, held.intro if held else "", entries)


def _entry_block(v: Level1) -> str:
    marks = " · ".join((v.id, *v.flags))
    return f"## {v.title} ({marks})\n\n{_escaped(v.statement)}"


def _escaped(text: str) -> str:
    return _HEADING_LINE.sub(r"\1\\\2", text)
