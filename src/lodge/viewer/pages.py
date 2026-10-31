"""The viewer's pages, each built from what the application returned."""

from lodge.app import Listed, Read, Shown, ThreadsWaiting
from lodge.core import Branch, CheckResult, Filters, Level1, Level3, Scope, Thread, attachment_path
from lodge.viewer.forms import confirm_form, record_forms, threads_body
from lodge.viewer.html import e, level1_body, link, page, paragraphs, where
from lodge.viewer.spec import spec_page as spec_page

KINDS = ("decision", "spec")
STATUSES = ("current", "replaced", "retired", "any")
_SCOPES = tuple(scope.value for scope in Scope)
_NONE = Read(None, ())


def search_page(listed: Listed, query: str, filters: Filters, notice: str | None = None) -> str:
    form = _search_form(query, filters)
    results = _results(listed.items, "No matches.", listed.read)
    shown, total = len(listed.items), len(listed.items) + listed.more
    cut = f"<p>{shown} of {total} shown; narrow the query.</p>" if listed.more else ""
    return page("Search", f"<h1>Search</h1>{form}{results}{cut}", listed.read, notice)


def record_page(shown: Shown, token: str, notice: str | None = None) -> str:
    v = shown.level1
    known = {v.id: v.status}
    if shown.level3 is not None:
        known |= {target: status for _, target, status in shown.level3.links}
    sections = ""
    if shown.level2 is not None:
        reasoning = (
            _results(shown.changing, "", shown.read)
            if shown.changing
            else paragraphs(shown.level2, known)
        )
        sections += _details("Reasoning", reasoning)
    if shown.level3 is not None:
        sections += _details("Provenance", _provenance(shown.level3, v))
    body = (
        f'<article class="record"><h1>{e(v.title)}</h1>{level1_body(v, known)}{sections}</article>'
    )
    if v.kind == "spec":
        body += "<h2>Rests on</h2>" + _branches(shown.rests_on)
        body += (
            "<h2>Rests on it</h2><ul>"
            + "".join(
                f"<li>{link(item.id, item.title)} {e(item.status)}</li>" for item in shown.supports
            )
            + "</ul>"
        )
    if shown.confirmable:
        body += confirm_form((v.id,), token)
    body += threads_body(shown.threads, token) + record_forms(v.id, token)
    return page(v.title, body, shown.read, notice)


def timeline_page(listed: Listed, notice: str | None = None) -> str:
    body = _results(listed.items, "No decisions yet.", listed.read)
    total = len(listed.items) + listed.more
    cut = f"<p>{len(listed.items)} of {total} shown.</p>" if listed.more else ""
    return page("Timeline", f"<h1>Timeline</h1>{body}{cut}", listed.read, notice)


def waiting_page(listed: Listed, waiting: ThreadsWaiting, notice: str | None = None) -> str:
    def threads(items: tuple[Thread, ...]) -> str:
        rows = "".join(
            f'<li><a href="/r/{e(t.about)}#{e(t.id)}">'
            f"{'Doubt' if t.raises == 'doubt' else 'Question'} {e(t.id)}: "
            f"{e(waiting.titles.get(t.about, t.about))}</a> "
            f"· {e(t.state.value)} · about {e(t.about)} · {len(t.messages)} "
            f"message{'s' if len(t.messages) != 1 else ''} · last by {e(t.messages[-1].by)}</li>"
            for t in items
        )
        return f"<ul>{rows}</ul>"

    body = "<h1>Waiting</h1><h2>Waiting for an agent</h2>" + threads(waiting.for_agent)
    body += "<h2>Waiting for the author</h2>"
    if listed.items or not waiting.for_author:
        body += _results(listed.items, "Nothing waits for the author.", listed.read)
    body += threads(waiting.for_author)
    return page("Waiting", body, listed.read, notice)


def _branches(branches: tuple[Branch, ...]) -> str:
    rows = "".join(
        f"<li>{link(b.id, b.title)} {e(b.status)}{_branches(b.children) if b.children else ''}</li>"
        for b in branches
    )
    return f"<ul>{rows}</ul>"


def problems_page(result: CheckResult, read: Read, notice: str | None = None) -> str:
    body = "<h1>Problems</h1>"
    if result.ok:
        body += "<p>ok</p>"
    else:
        items = "".join(
            f'<li><span class="check">check {p.check}</span> <code>{e(where(p))}</code> '
            f"{e(p.message)}</li>"
            for p in result.problems
        )
        body += f"<ul>{items}</ul>"
    if result.notes:
        notes = "".join(f"<li>{e(note)}</li>" for note in result.notes)
        body += f"<h2>Notes</h2><ul>{notes}</ul>"
    return page("Problems", body, read, notice)


def error_page(message: str, back: str | None = None) -> str:
    link = f'<a href="{e(back)}">Back to the form</a>' if back is not None else ""
    return page(
        "Cannot show this page", f"<h1>Cannot show this page</h1><p>{e(message)}</p>{link}", _NONE
    )


def _results(items: tuple[Level1, ...], empty: str, read: Read) -> str:
    if not items:
        return f"<p>{e(empty)}</p>"
    rows = "".join(
        f'<li class="result"><h2>{link(v.id, v.title)}</h2>{level1_body(v, read.statuses)}</li>'
        for v in items
    )
    return f'<ol class="results">{rows}</ol>'


def _details(summary: str, inner: str) -> str:
    return f"<details><summary>{e(summary)}</summary>{inner or '<p>None recorded.</p>'}</details>"


def _provenance(v3: Level3, v: Level1) -> str:
    rows: list[str] = []
    if v3.quote and v.quote is None:
        q = v3.quote
        rows.append(f"quote: &ldquo;{e(q.text)}&rdquo; ({e(q.where)}, {e(q.when)})")
    rows += [f"number: {e(n.value)} ({e(n.handle)})" for n in v3.numbers]
    if v3.work_item:
        rows.append(f"work item: {e(v3.work_item)}")
    rows += [
        f"attachment: <code>{e(attachment_path(v.id, name))}</code>" for name in v3.attachments
    ]
    if v3.imported_from:
        rows.append(f"imported from: {e(v3.imported_from.file)}, {e(v3.imported_from.heading)}")
    rows += [
        f'{e(relation)} {link(target)} <span class="status">{e(status)}</span>'
        for relation, target, status in v3.links
    ]
    return "<ul>" + "".join(f"<li>{row}</li>" for row in rows) + "</ul>" if rows else ""


def _search_form(query: str, filters: Filters) -> str:
    scope = None if filters.scope is None else str(filters.scope)
    fields = [
        f'<label>Words <input type="search" name="q" value="{e(query)}"></label>',
        _select("kind", "Kind", KINDS, filters.kind),
        _select("scope", "Scope", _SCOPES, scope),
        _select("status", "Status", STATUSES, filters.status, blank=False),
        f'<label>Area <input type="text" name="area" value="{e(filters.area or "")}"></label>',
        '<label>Decided by <input type="text" name="decided_by" '
        f'value="{e(filters.decided_by or "")}"></label>',
        "<button>Search</button>",
    ]
    return f'<form method="get" action="/">{"".join(fields)}</form>'


def _select(
    name: str, label: str, values: tuple[str, ...], chosen: str | None, blank: bool = True
) -> str:
    options = [("", "any")] if blank else []
    options += [(value, value) for value in values]
    shown = "".join(
        f'<option value="{e(value)}"{" selected" if value == (chosen or "") else ""}>'
        f"{e(text)}</option>"
        for value, text in options
    )
    return f'<label>{e(label)} <select name="{e(name)}">{shown}</select></label>'
