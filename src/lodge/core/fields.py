"""Typed readers for header values; each names the key it rejects."""

import re
from collections.abc import Collection, Mapping
from datetime import date, datetime
from enum import StrEnum

from lodge.core.ids import is_id
from lodge.core.yamlio import LINE_BREAKS_AND_TABS, unreadable_char

_CODE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
_AREA = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
_STAMP = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}[+-][0-9]{2}:[0-9]{2}")
_DAY = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
ID_KIND = {"d": "decision", "s": "specification entry", "q": "thread"}


class FormatError(Exception):
    """A file or draft that breaks the format; `key` names the header key at fault."""

    def __init__(self, message: str, key: str | None = None, line: int | None = None) -> None:
        super().__init__(message)
        self.key = key
        self.line = line


def check_keys(header: Mapping[str, object], allowed: Collection[str]) -> None:
    unknown = [key for key in header if key not in allowed]
    if unknown:
        names = ", ".join(repr(key) for key in unknown)
        raise FormatError(
            f"unknown key {names}; the keys here are {', '.join(allowed)}", unknown[0]
        )


def require(header: Mapping[str, object], key: str) -> object:
    if key not in header:
        raise FormatError(f"missing required field '{key}'", key)
    return header[key]


def read_str(value: object, key: str, allowed: str = "") -> str:
    if not isinstance(value, str) or not value.strip():
        raise FormatError(f"{key} must be a non-empty string", key)
    bad = unreadable_char(value, allowed)
    if bad is not None:
        raise FormatError(f"{key} holds U+{ord(bad):04X}, which a header cannot carry", key)
    return value


def read_optional_str(header: Mapping[str, object], key: str) -> str | None:
    return read_str(header[key], key) if key in header else None


def read_code(header: Mapping[str, object]) -> str | None:
    code = read_optional_str(header, "code")
    if code is not None and _CODE.fullmatch(code) is None:
        raise FormatError(f"code must match [A-Za-z0-9][A-Za-z0-9._-]*, not {code!r}", "code")
    return code


def read_list(value: object, key: str) -> list[object]:
    if not isinstance(value, list):
        raise FormatError(f"{key} must be a list", key)
    return value


def read_map(
    value: object, key: str, names: tuple[str, ...], multiline: str | None = None
) -> dict[str, str]:
    """A mapping with exactly the keys `names`, each a non-empty string.

    The value of the key `multiline` may hold line breaks and tabs.
    """
    if not isinstance(value, Mapping):
        raise FormatError(f"{key} must be a mapping with {', '.join(names)}", key)
    for name in value:
        if name not in names:
            raise FormatError(
                f"{key} has an unknown key {name!r}; it takes {', '.join(names)}", key
            )
    for name in names:
        if name not in value:
            raise FormatError(f"{key} is missing '{name}'", key)
    return {
        name: read_str(
            value[name], f"{key}.{name}", LINE_BREAKS_AND_TABS if name == multiline else ""
        )
        for name in names
    }


def read_maps(value: object, key: str, names: tuple[str, ...]) -> list[dict[str, str]]:
    return [read_map(item, key, names) for item in read_list(value, key)]


def read_id(value: object, key: str, prefix: str) -> str:
    text = read_str(value, key)
    if not is_id(text) or not text.startswith(f"{prefix}-"):
        raise FormatError(f"{key} holds {text!r}, which is not a {ID_KIND[prefix]} id", key)
    return text


def read_ids(value: object, key: str, prefix: str) -> tuple[str, ...]:
    return tuple(read_id(item, key, prefix) for item in read_list(value, key))


def read_strs(value: object, key: str) -> tuple[str, ...]:
    return tuple(read_str(item, key) for item in read_list(value, key))


def read_enum[E: StrEnum](kind: type[E], value: object, key: str) -> E:
    text = read_str(value, key)
    try:
        return kind(text)
    except ValueError:
        options = ", ".join(repr(str(member)) for member in kind.__members__.values())
        raise FormatError(f"{key} must be one of {options}, not {text!r}", key) from None


def read_date(value: object, imported: bool) -> str:
    """An ISO 8601 stamp with seconds and an offset; a bare day only for an imported record."""
    text = read_str(value, "date")
    try:
        if _STAMP.fullmatch(text):
            datetime.fromisoformat(text)
            return text
        if _DAY.fullmatch(text) and imported:
            date.fromisoformat(text)
            return f"{text}T00:00:00+00:00"
    except ValueError:
        raise FormatError(f"date {text!r} is not a real date and time", "date") from None
    hint = "" if imported else "; a date alone is accepted only with imported_from"
    raise FormatError(
        f"date must be ISO 8601 with seconds and an offset, as in 2026-10-28T23:48:10+01:00{hint}",
        "date",
    )


def read_area_name(value: object, key: str) -> str:
    text = read_str(value, key)
    if _AREA.fullmatch(text) is None:
        raise FormatError(f"area name {text!r} must be lower-case words joined by hyphens", key)
    return text


def read_rank(value: object) -> int:
    """A non-negative whole number written without leading zeroes."""
    if not isinstance(value, str) or re.fullmatch(r"0|[1-9][0-9]*", value) is None:
        raise FormatError("rank must be a non-negative whole number without leading zeroes", "rank")
    return int(value)


def read_stamp(value: object, key: str) -> str:
    """An ISO 8601 date and time with seconds and an offset."""
    text = read_str(value, key)
    if _STAMP.fullmatch(text):
        try:
            datetime.fromisoformat(text)
            return text
        except ValueError:
            pass
    raise FormatError(f"{key} must be ISO 8601 with seconds and an offset", key)
