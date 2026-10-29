"""Drafts: files an agent writes, without the identifier and date that lodge fills in."""

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Literal

from lodge.core.document import load_header, problem_for, split_document, trim_block
from lodge.core.fields import FormatError, check_keys, read_str
from lodge.core.headers import (
    AREA_KEYS,
    DECISION_KEYS,
    SPEC_KEYS,
    area_from,
    decision_from,
    spec_from,
)
from lodge.core.model import Area, Problem, Record

DraftKind = Literal["decision", "spec", "area"]
_KEYS: dict[DraftKind, tuple[str, ...]] = {
    "decision": (*DECISION_KEYS, "base"),
    "spec": (*SPEC_KEYS, "area", "base"),
    "area": (*AREA_KEYS, "name", "base"),
}


@dataclass(frozen=True)
class Draft:
    kind: DraftKind
    header: Mapping[str, object]
    body: str
    source: str
    header_text: str = ""


def parse_draft(source: str, text: str) -> Draft | Problem:
    """A draft's header and body; only the syntax and the key names are checked here."""

    header_text = ""
    try:
        header_text, body = split_document(text)
        header = load_header(header_text)
        kind = _kind_of(header.get("kind"))
        check_keys(header, _KEYS[kind])
        return Draft(kind, header, trim_block(body), source, header_text)
    except FormatError as error:
        return problem_for(source, error, header_text)


def record_from_draft(
    draft: Draft, id: str, date: str | None, area: str | None
) -> Record | Area | Problem:
    """The record a draft describes, given the `id` lodge gives it.

    A new record is given a `date`, and a draft may set one only with `imported_from`.
    An existing record is given `date=None` and keeps the date its draft carries.
    A new specification entry or area names itself in the draft; an existing one is given `area`.
    """
    header = {
        key: value for key, value in draft.header.items() if key not in ("area", "name", "base")
    }
    try:
        if draft.kind == "area":
            return area_from(header, draft.body, _name(draft, "name", area))
        header = _with_id(header, id)
        if draft.kind == "spec":
            return spec_from(header, draft.body, _name(draft, "area", area))
        return decision_from(_with_date(header, date), draft.body)
    except FormatError as error:
        return problem_for(draft.source, error, draft.header_text)


def _kind_of(value: object) -> DraftKind:
    if value == "decision":
        return "decision"
    if value == "spec":
        return "spec"
    if value == "area":
        return "area"
    raise FormatError("kind must be 'decision', 'spec', or 'area'", "kind")


def _with_id(header: dict[str, object], id: str) -> dict[str, object]:
    if header.get("id", id) != id:
        raise FormatError(
            f"id {header['id']!r} differs from the id {id!r} lodge gave this draft", "id"
        )
    return {**header, "id": id}


def _with_date(header: dict[str, object], date: str | None) -> dict[str, object]:
    if date is None or ("date" in header and "imported_from" in header):
        return header
    if "date" in header:
        raise FormatError(
            "lodge sets the date; a draft may set one only with imported_from", "date"
        )
    return {**header, "date": date}


def _name(draft: Draft, key: str, given: str | None) -> str:
    own = read_str(draft.header[key], key) if key in draft.header else None
    if given is not None and own is not None and own != given:
        raise FormatError(f"{key} {own!r} differs from {given!r}; entries do not move", key)
    name = given if given is not None else own
    if name is None:
        raise FormatError(f"a new {draft.kind} draft needs a '{key}' key", key)
    return name
