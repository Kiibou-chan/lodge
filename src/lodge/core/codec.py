"""JSON-native plain values, isolated by the source and dependency digest."""

from collections.abc import Callable, Mapping
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
        return ["=" + type(value).__name__, value.value]
    if is_dataclass(value) and not isinstance(value, type):
        return [type(value).__name__, *(to_plain(getattr(value, f.name)) for f in fields(value))]
    if type(value) in (str, int, bool) or value is None:
        return value
    if isinstance(value, tuple):
        return ["", *(to_plain(v) for v in value)]
    if isinstance(value, Mapping) and all(type(k) is str for k in value):
        return {k: to_plain(v) for k, v in value.items()}
    if isinstance(value, frozenset):
        return ["*", *(to_plain(v) for v in value)]
    raise ValueError("unsupported cached value")


def from_plain(plain: object, classes: Mapping[str, type]) -> object:
    """Decode registered shapes with class layouts and validators compiled once."""
    if type(plain) is list:
        return _compact(plain, classes)
    if type(plain) in (str, int, bool) or plain is None:
        return plain
    if isinstance(plain, dict) and all(type(k) is str for k in plain):
        return {k: from_plain(v, classes) for k, v in plain.items()}
    raise ValueError("invalid cached value")


@cache
def _hints(cls: type) -> dict[str, object]:
    return get_type_hints(cls)


@cache
def _check(annotation: object) -> Callable[[object], bool]:
    origin, args = get_origin(annotation), get_args(annotation)
    if origin is tuple:
        if len(args) == 2 and args[1] is Ellipsis:
            item = _check(args[0])
            return lambda v: isinstance(v, tuple) and all(item(x) for x in v)
        items = tuple(_check(a) for a in args)
        return lambda v: (
            isinstance(v, tuple)
            and len(v) == len(items)
            and all(check(x) for check, x in zip(items, v, strict=True))
        )
    if origin is Mapping:
        key, value = _check(args[0]), _check(args[1])
        return lambda v: isinstance(v, dict) and all(key(k) and value(x) for k, x in v.items())
    if origin is frozenset:
        item = _check(args[0])
        return lambda v: isinstance(v, frozenset) and all(item(x) for x in v)
    if args and all(isinstance(a, type) for a in args):
        return lambda v: type(v) in args
    if args:
        choices = tuple(_check(a) for a in args)
        return lambda v: any(check(v) for check in choices)
    return lambda v: type(v) is annotation


@cache
def _layout(
    cls: type,
) -> tuple[
    tuple[str, ...],
    tuple[tuple[int, tuple[type, ...]], ...],
    tuple[tuple[int, Callable[[object], bool], type | None], ...],
]:
    if not is_dataclass(cls):
        raise ValueError("invalid cached class")
    hints = _hints(cls)
    names = tuple(f.name for f in fields(cls))
    scalars: list[tuple[int, tuple[type, ...]]] = []
    nested: list[tuple[int, Callable[[object], bool], type | None]] = []
    for i, name in enumerate(names):
        annotation = hints[name]
        types = get_args(annotation) or (annotation,)
        if get_origin(annotation) not in (tuple, Mapping, frozenset) and all(
            t in (str, int, bool, type(None)) for t in types
        ):
            scalars.append((i, types))
        else:
            args = get_args(annotation)
            item = (
                args[0]
                if get_origin(annotation) is tuple
                and len(args) == 2
                and args[1] is Ellipsis
                and args[0] in (str, int, bool)
                else None
            )
            nested.append((i, _check(annotation), item))
    return names, tuple(scalars), tuple(nested)


def _compact(plain: list[object], classes: Mapping[str, type]) -> object:
    if not plain or type(plain[0]) is not str:
        raise ValueError("invalid cached tag")
    tag = plain[0]
    if tag == "":
        return tuple(from_plain(v, classes) for v in plain[1:]) if len(plain) > 1 else ()
    if tag == "*":
        return frozenset(from_plain(v, classes) for v in plain[1:])
    cls = classes.get(tag[1:] if tag.startswith("=") else tag)
    if cls is None:
        raise ValueError("unknown cached class")
    if tag.startswith("="):
        if issubclass(cls, Enum) and len(plain) == 2:
            return cls(plain[1])
        raise ValueError("invalid cached enum")
    names, scalars, nested = _layout(cls)
    if len(plain) != len(names) + 1:
        raise ValueError("invalid cached arity")
    values = plain[1:]
    for i, types in scalars:
        if type(values[i]) not in types:
            raise ValueError("invalid cached scalar")
    for i, check, item in nested:
        raw = values[i]
        if item is not None:
            if not isinstance(raw, list) or not raw or raw[0] != "":
                raise ValueError("invalid cached tuple")
            items = raw[1:]
            if items and not all(type(v) is item for v in items):
                raise ValueError("invalid cached tuple item")
            values[i] = tuple(items)
        else:
            if raw is not None:
                values[i] = from_plain(raw, classes)
            if not check(values[i]):
                raise ValueError("invalid cached field")
    record: object = object.__new__(cls)
    record.__dict__.update(zip(names, values, strict=True))
    return record
