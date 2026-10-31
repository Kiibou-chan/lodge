"""Records built from a header mapping and a body; the one place the field rules live."""

from collections.abc import Mapping

from lodge.core.document import (
    REASONING_HEADING,
    has_reasoning_heading,
    split_reasoning,
    trim_block,
)
from lodge.core.fields import (
    FormatError,
    check_keys,
    read_area_name,
    read_code,
    read_date,
    read_enum,
    read_id,
    read_ids,
    read_map,
    read_maps,
    read_optional_str,
    read_rank,
    read_str,
    read_strs,
    require,
)
from lodge.core.model import (
    Action,
    Area,
    Change,
    Decision,
    Imported,
    NumberHandle,
    Quote,
    Scope,
    SpecEntry,
)

DECISION_KEYS = (
    *("id", "kind", "code", "title", "scope", "decided_by", "date", "changes", "replaces"),
    *("narrows", "confirms", "work_item", "quote", "numbers", "attachments", "imported_from"),
)
SPEC_KEYS = ("id", "kind", "code", "title", "imported_from", "rests_on")
AREA_KEYS = ("kind", "title", "order", "rank")


def decision_from(header: Mapping[str, object], body: str) -> Decision:
    check_keys(header, DECISION_KEYS)
    _expect_kind(header, "decision")
    decision_id = read_id(require(header, "id"), "id", "d")
    title = read_str(require(header, "title"), "title")
    scope = read_enum(Scope, require(header, "scope"), "scope")
    decided_by = read_str(require(header, "decided_by"), "decided_by")
    imported = _imported(header)
    date = read_date(require(header, "date"), imported is not None)
    statement, reasoning = split_reasoning(body)
    if not statement:
        raise FormatError("the statement is empty; write it above any '## Reasoning' heading")
    return Decision(
        id=decision_id,
        title=title,
        scope=scope,
        decided_by=decided_by,
        date=date,
        statement=statement,
        reasoning=reasoning,
        code=read_code(header),
        changes=tuple(
            Change(item["entry"], read_enum(Action, item["action"], "changes.action"))
            for item in _changes(header)
        ),
        replaces=_ids(header, "replaces"),
        narrows=_ids(header, "narrows"),
        confirms=_ids(header, "confirms"),
        work_item=read_optional_str(header, "work_item"),
        quote=_quote(header),
        numbers=tuple(
            NumberHandle(item["value"], item["handle"])
            for item in read_maps(header.get("numbers", []), "numbers", ("value", "handle"))
        ),
        attachments=read_strs(header.get("attachments", []), "attachments"),
        imported_from=imported,
    )


def spec_from(header: Mapping[str, object], body: str, area: str) -> SpecEntry:
    check_keys(header, SPEC_KEYS)
    _expect_kind(header, "spec")
    entry_id = read_id(require(header, "id"), "id", "s")
    title = read_str(require(header, "title"), "title")
    if has_reasoning_heading(body):
        raise FormatError(f"a specification entry has no '{REASONING_HEADING}' section")
    statement = trim_block(body)
    if not statement:
        raise FormatError("the statement is empty")
    return SpecEntry(
        id=entry_id,
        area=read_area_name(area, "area"),
        title=title,
        statement=statement,
        code=read_code(header),
        imported_from=_imported(header),
        rests_on=_ids(header, "rests_on", "s"),
    )


def area_from(header: Mapping[str, object], body: str, name: str) -> Area:
    check_keys(header, AREA_KEYS)
    _expect_kind(header, "area")
    return Area(
        name=read_area_name(name, "area"),
        title=read_str(require(header, "title"), "title"),
        intro=trim_block(body),
        order=_ids(header, "order", "s"),
        rank=read_rank(header["rank"]) if "rank" in header else None,
    )


def _expect_kind(header: Mapping[str, object], kind: str) -> None:
    if require(header, "kind") != kind:
        raise FormatError(f"kind must be '{kind}' here", "kind")


def _ids(header: Mapping[str, object], key: str, prefix: str = "d") -> tuple[str, ...]:
    return read_ids(header.get(key, []), key, prefix)


def _changes(header: Mapping[str, object]) -> list[dict[str, str]]:
    items = read_maps(header.get("changes", []), "changes", ("entry", "action"))
    for item in items:
        read_id(item["entry"], "changes.entry", "s")
    return items


def _quote(header: Mapping[str, object]) -> Quote | None:
    if "quote" not in header:
        return None
    fields = read_map(header["quote"], "quote", ("text", "where", "when"), "text")
    return Quote(fields["text"], fields["where"], fields["when"])


def _imported(header: Mapping[str, object]) -> Imported | None:
    if "imported_from" not in header:
        return None
    fields = read_map(header["imported_from"], "imported_from", ("file", "heading"))
    return Imported(fields["file"], fields["heading"])
