"""Reading and writing record and area files, their paths, and the hash of a file's text."""

import hashlib
import re
from dataclasses import fields

from lodge.core.document import (
    REASONING_HEADING,
    assemble,
    has_reasoning_heading,
    normalise_newlines,
    read_with,
)
from lodge.core.fields import FormatError, read_area_name
from lodge.core.headers import area_from, decision_from, spec_from
from lodge.core.model import Area, Decision, Imported, Problem, Record, SpecEntry
from lodge.core.yamlio import LINE_BREAKS_AND_TABS, quoted

_PLAIN = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
_WORD = re.compile(r"[a-z0-9]+")
_SLUG_WORDS = 6
_SLUG_CHARS = 60


def parse_record(path: str, text: str) -> Record | Problem:
    def build(header: dict[str, object], body: str) -> Record:
        kind = header.get("kind")
        if kind == "decision":
            return decision_from(header, body)
        if kind == "spec":
            return spec_from(header, body, _folder_of(path))
        raise FormatError("kind must be 'decision' or 'spec'", "kind")

    return read_with(path, text, build)


def parse_area(path: str, text: str) -> Area | Problem:
    return read_with(path, text, lambda header, body: area_from(header, body, _folder_of(path)))


def write_record(record: Record) -> str:
    """The canonical file for `record`; a record that would not read back is a `ValueError`."""
    if has_reasoning_heading(record.statement):
        raise ValueError(f"the statement holds a line reading '{REASONING_HEADING}'")
    if isinstance(record, Decision):
        text = assemble(_decision_header(record), _decision_body(record))
    else:
        text = assemble(_spec_header(record), record.statement)
    back = parse_record(new_record_path(record), text)
    if isinstance(back, Problem):
        raise ValueError(f"the record would not read back: {back.message}")
    if back != record:
        raise ValueError(f"the record would not read back unchanged: {_differing(record, back)}")
    return text


def write_area(area: Area) -> str:
    header = ["kind: area", f"title: {_quoted('title', area.title)}"]
    if area.order:
        header.append(f"order: [{', '.join(area.order)}]")
    text = assemble(header, area.intro)
    back = parse_area(area_path(area.name), text)
    if isinstance(back, Problem):
        raise ValueError(f"the area would not read back: {back.message}")
    if back != area:
        raise ValueError(f"the area would not read back unchanged: {_differing(area, back)}")
    return text


def new_record_path(record: Record) -> str:
    words = slug(record.title)
    stem = f"{record.id}-{words}" if words else record.id
    if isinstance(record, Decision):
        return f"lodge/decisions/{stem}.md"
    return f"lodge/spec/{record.area}/{stem}.md"


def area_path(name: str) -> str:
    return f"lodge/spec/{name}/_area.md"


def slug(title: str) -> str:
    """At most six words of the title, joined by hyphens, cut to 60 characters at a word end."""
    joined = "-".join(_WORD.findall(title.lower())[:_SLUG_WORDS])
    if len(joined) <= _SLUG_CHARS:
        return joined
    cut = joined.rfind("-", 0, _SLUG_CHARS + 1)
    return joined[:cut] if cut > 0 else joined[:_SLUG_CHARS]


def content_hash(text: str) -> str:
    """The first 12 hex characters of the SHA-256 of the text, line ends as `\\n`."""
    data = normalise_newlines(text).encode("utf-8", errors="surrogateescape")
    return hashlib.sha256(data).hexdigest()[:12]


def _folder_of(path: str) -> str:
    parts = path.split("/")
    if len(parts) < 2:
        raise FormatError(
            "an area's files lie in a folder named after the area, as in lodge/spec/<area>/"
        )
    return read_area_name(parts[-2], "area")


def _differing(record: Record | Area, back: Record | Area) -> str:
    """The name of the first field of `record` that reads back as something else."""
    for item in fields(record):
        if getattr(record, item.name) != getattr(back, item.name):
            return f"{item.name} reads back as {getattr(back, item.name)!r}"
    return "the kind differs"


def _quoted(key: str, value: str, allowed: str = "") -> str:
    try:
        return quoted(value, allowed)
    except ValueError as error:
        raise ValueError(f"{key}: {error}") from None


def _imported_line(imported: Imported) -> str:
    file = _quoted("imported_from.file", imported.file)
    heading = _quoted("imported_from.heading", imported.heading)
    return f"imported_from: {{file: {file}, heading: {heading}}}"


def _decision_header(d: Decision) -> list[str]:
    plain = d.decided_by if _PLAIN.fullmatch(d.decided_by) else _quoted("decided_by", d.decided_by)
    header = [f"id: {d.id}", "kind: decision"]
    header += [f"code: {d.code}"] if d.code is not None else []
    header += [f"title: {_quoted('title', d.title)}", f"scope: {d.scope.value}"]
    header += [f"decided_by: {plain}", f"date: {d.date}"]
    if d.changes:
        header.append("changes:")
        header += [f"  - {{entry: {c.entry}, action: {c.action.value}}}" for c in d.changes]
    for key, ids in (("replaces", d.replaces), ("narrows", d.narrows), ("confirms", d.confirms)):
        header += [f"{key}: [{', '.join(ids)}]"] if ids else []
    if d.work_item is not None:
        header.append(f"work_item: {_quoted('work_item', d.work_item)}")
    if d.quote is not None:
        text = _quoted("quote.text", d.quote.text, LINE_BREAKS_AND_TABS)
        where = _quoted("quote.where", d.quote.where)
        when = _quoted("quote.when", d.quote.when)
        header.append(f"quote: {{text: {text}, where: {where}, when: {when}}}")
    if d.numbers:
        header.append("numbers:")
        for n in d.numbers:
            value, handle = _quoted("numbers.value", n.value), _quoted("numbers.handle", n.handle)
            header.append(f"  - {{value: {value}, handle: {handle}}}")
    if d.attachments:
        header.append(
            f"attachments: [{', '.join(_quoted('attachments', a) for a in d.attachments)}]"
        )
    header += [_imported_line(d.imported_from)] if d.imported_from is not None else []
    return header


def _decision_body(d: Decision) -> str:
    return f"{d.statement}\n\n{REASONING_HEADING}\n\n{d.reasoning}" if d.reasoning else d.statement


def _spec_header(entry: SpecEntry) -> list[str]:
    header = [f"id: {entry.id}", "kind: spec"]
    header += [f"code: {entry.code}"] if entry.code is not None else []
    header.append(f"title: {_quoted('title', entry.title)}")
    header += [_imported_line(entry.imported_from)] if entry.imported_from is not None else []
    return header
