"""Specification reading orders and area confirmation pages."""

from typing import Literal
from urllib.parse import urlencode

from lodge.app import Behind, Read
from lodge.core import Level1, Placed, SpecArea
from lodge.viewer.forms import confirm_form
from lodge.viewer.html import e, link, linked, page, paragraphs


def spec_page(
    areas: tuple[SpecArea, ...],
    read: Read,
    token: str,
    order: Literal["dependency", "written"],
    area: str | None,
    behind: tuple[Behind, ...],
    notice: str | None = None,
) -> str:
    query = {} if area is None else {"area": area}
    dependency = "/spec" + ("?" + urlencode(query) if query else "")
    written = "/spec?" + urlencode(query | {"order": "written"})
    body = (
        f'<p><a href="{e(dependency)}">By dependency</a> &middot; '
        f'<a href="{e(written)}">As written</a></p>'
    )
    if behind and area is not None:
        body += "<h2>Decisions behind this area, not yet confirmed</h2><ul>"
        for held in behind:
            entries = ", ".join(f"{link(i)} ({e(a)})" for i, a in held.entries)
            body += f"<li>{link(held.decision.id, held.decision.title)}: {entries}</li>"
        body += "</ul>" + confirm_form(tuple(h.decision.id for h in behind), token, area)
    for held_area in areas:
        href = "/spec?" + urlencode({"area": held_area.name})
        body += (
            f'<h1><a href="{e(href)}">{e(held_area.title)}</a></h1>{paragraphs(held_area.intro)}'
        )
        if order == "written":
            body += "".join(_entry(v, read) for v in held_area.entries)
        else:
            body += "".join(_placed(p, read) for p in held_area.placed)
    if not areas:
        body += "<p>Nothing is recorded yet.</p>"
    return page("Specification", body, read, notice)


def _entry(v: Level1, read: Read) -> str:
    marks = "".join(f" &middot; {linked(flag, read.statuses)}" for flag in v.flags)
    return f"<h2>{e(v.title)} ({link(v.id)}{marks})</h2>{paragraphs(v.statement)}"


def _placed(p: Placed, read: Read) -> str:
    body = _entry(p.entry, read)
    extra = (*p.also, *((p.under,) if p.depth > 5 and p.under is not None else ()))
    if extra:
        body += "<p>also rests on " + ", ".join(link(i) for i in extra) + "</p>"
    body += "".join(f"<p>rests on {link(i)} ({e(a)})</p>" for i, a in p.across)
    return f'<div class="depth-{min(p.depth, 5)}">{body}</div>'
