"""A strict plain-value representation of cached records and read values."""

from collections.abc import Mapping
from dataclasses import fields, is_dataclass
from enum import Enum
from functools import cache
from typing import get_args, get_origin, get_type_hints

from lodge.core.model import (
    Action,
    Area,
    Change,
    Decision,
    Imported,
    Message,
    NumberHandle,
    Problem,
    Quote,
    Raises,
    Scope,
    SpecEntry,
    Thread,
    ThreadState,
)
from lodge.core.views import Level1, Level3

CORE_CLASSES: Mapping[str, type] = {
    cls.__name__: cls
    for cls in (
        Action,
        Area,
        Change,
        Decision,
        Imported,
        Message,
        NumberHandle,
        Problem,
        Quote,
        Raises,
        Scope,
        SpecEntry,
        Thread,
        ThreadState,
        Level1,
        Level3,
    )
}


def to_plain(value: object) -> object:
    """Encode only the documented shapes, tagging enums before their scalar base types."""
    if isinstance(value, Enum):
        return ("=" + type(value).__name__, to_plain(value.value))
    if is_dataclass(value) and not isinstance(value, type):
        return (type(value).__name__, *(to_plain(getattr(value, f.name)) for f in fields(value)))
    if type(value) in (str, int, bool) or value is None:
        return value
    if isinstance(value, tuple):
        return [to_plain(v) for v in value]
    if isinstance(value, Mapping) and all(type(k) is str for k in value):
        return {k: to_plain(v) for k, v in value.items()}
    if isinstance(value, frozenset):
        return frozenset(to_plain(v) for v in value)
    raise ValueError("unsupported cached value")


def from_plain(plain: object, classes: Mapping[str, type]) -> object:
    """Decode only our shapes and registered classes, checking every field's declared type."""
    if type(plain) in (str, int, bool) or plain is None:
        return plain
    if isinstance(plain, list):
        return tuple(from_plain(v, classes) for v in plain)
    if isinstance(plain, dict) and all(type(k) is str for k in plain):
        return {k: from_plain(v, classes) for k, v in plain.items()}
    if isinstance(plain, frozenset):
        return frozenset(from_plain(v, classes) for v in plain)
    if isinstance(plain, tuple) and plain and type(plain[0]) is str:
        tag, *values = plain
        enum = tag.startswith("=")
        cls = classes.get(tag[1:] if enum else tag)
        if cls is not None:
            if enum and issubclass(cls, Enum) and len(values) == 1:
                return cls(values[0])
            if not enum and is_dataclass(cls) and len(values) == len(fields(cls)):
                decoded = [from_plain(v, classes) for v in values]
                hints = _hints(cls)
                if all(_fits(v, hints[f.name]) for f, v in zip(fields(cls), decoded, strict=True)):
                    return cls(*decoded)
    raise ValueError("invalid cached value")


@cache
def _hints(cls: type) -> dict[str, object]:
    return get_type_hints(cls)


def _fits(value: object, annotation: object) -> bool:
    origin, args = get_origin(annotation), get_args(annotation)
    if origin is tuple:
        if not isinstance(value, tuple):
            return False
        if len(args) == 2 and args[1] is Ellipsis:
            return all(_fits(v, args[0]) for v in value)
        return len(value) == len(args) and all(
            _fits(v, t) for v, t in zip(value, args, strict=True)
        )
    if origin is Mapping:
        return isinstance(value, dict) and all(
            _fits(k, args[0]) and _fits(v, args[1]) for k, v in value.items()
        )
    if origin is frozenset:
        return isinstance(value, frozenset) and all(_fits(v, args[0]) for v in value)
    if args:
        return any(_fits(value, t) for t in args)
    return isinstance(annotation, type) and type(value) is annotation
