"""Escaping, links, and the frame every page shares."""

import re
from collections.abc import Mapping
from html import escape
from urllib.parse import quote

from lodge.app import Read
from lodge.core import Level1, Problem, head_parts

NAV = (
    ("/", "Search"),
    ("/spec", "Specification"),
    ("/timeline", "Timeline"),
    ("/waiting", "Waiting"),
    ("/problems", "Problems"),
)
_ID = re.compile(r"\b[ds]-[0-9a-hjkmnp-tv-z]{6}\b")


def e(text: str) -> str:
    return escape(text, quote=True)


def link(ref: str, text: str | None = None) -> str:
    return f'<a href="/r/{e(quote(ref, safe=""))}">{e(ref if text is None else text)}</a>'


def linked(text: str, statuses: Mapping[str, str] | None = None) -> str:
    """`text` escaped; each record ID in `statuses` a link with its status beside it."""
    known = statuses or {}

    def swap(found: re.Match[str]) -> str:
        ref = found[0]
        if ref not in known:
            return ref
        return f'{link(ref)} <span class="status">{e(known[ref])}</span>'

    return _ID.sub(swap, e(text))


def paragraphs(text: str, statuses: Mapping[str, str] | None = None) -> str:
    blocks = [block.strip() for block in text.strip().split("\n\n") if block.strip()]
    return "".join(f"<p>{linked(block, statuses)}</p>" for block in blocks)


def where(problem: Problem) -> str:
    return f"{problem.path}:{problem.line}" if problem.line else problem.path


def meta(v: Level1) -> str:
    """The identifier, status, who decided, the day, and the scope or area."""
    ident, code, status, who, day, place = head_parts(v)
    id_html = f'<span class="id">{e(ident)}</span>'
    if code:
        id_html += f' <span class="code">{e(code)}</span>'
    status_html = f'<span class="status status-{e(status)}">{e(status)}</span>'
    parts = [id_html, status_html, *(e(p) for p in (who, day, place) if p)]
    return f'<p class="meta">{" &middot; ".join(parts)}</p>'


def flags(v: Level1, statuses: Mapping[str, str] | None = None) -> str:
    items = "".join(f'<span class="flag">{linked(flag, statuses)}</span>' for flag in v.flags)
    return f'<p class="flags">{items}</p>' if items else ""


def quoted(v: Level1) -> str:
    if v.quote is None:
        return ""
    q = v.quote
    return (
        f'<blockquote class="quote"><p>&ldquo;{e(q.text)}&rdquo;</p>'
        f"<footer>{e(q.where)}, {e(q.when)}</footer></blockquote>"
    )


def level1_body(v: Level1, statuses: Mapping[str, str] | None = None) -> str:
    """What every read shows: the flags, then the statement and the author's quote."""
    statement = f'<div class="statement">{paragraphs(v.statement)}</div>'
    return f"{meta(v)}{flags(v, statuses)}{statement}{quoted(v)}"


def page(title: str, body: str, read: Read) -> str:
    nav = "".join(f'<a href="{href}">{label}</a>' for href, label in NAV)
    fresh = f'<p class="freshness">{e(read.freshness)}</p>' if read.freshness else ""
    return (
        '<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<title>{e(title)} &ndash; lodge</title><link rel="stylesheet" href="/style.css">'
        f"</head><body><header><nav>{nav}</nav></header>{fresh}{_banner(read)}"
        f"<main>{body}</main></body></html>\n"
    )


def _banner(read: Read) -> str:
    """Each file lodge cannot read, named above the page's content."""
    if not read.unrecorded:
        return ""
    count = len(read.unrecorded)
    noun = "file lodge cannot read" if count == 1 else "files lodge cannot read"
    items = "".join(f"<li><code>{e(where(p))}</code>: {e(p.message)}</li>" for p in read.unrecorded)
    return (
        f'<aside class="banner" role="alert"><p><a href="/problems">{count} {noun}</a></p>'
        f"<ul>{items}</ul></aside>"
    )
