"""The writer-shape guard and the optional libyaml text loader."""

import re
from collections.abc import Hashable
from typing import Any

import yaml
from yaml.constructor import ConstructorError, SafeConstructor

_FORBIDDEN = re.compile(r"[\x00-\x09\x0b-\x1f\x7f\u0085\u2028\u2029\ufeff\ud800-\udfff]")
_KEY = r"[a-z_]+"
_PLAIN = r"[A-Za-z0-9][A-Za-z0-9._:+-]*(?<!:)"
_STRING = r'"(?:[^"\\\x00-\x1f]|\\(?:["\\bfnrt]|u(?![dD][89a-fA-F])[0-9a-fA-F]{4}))*"'
_VALUE = rf"(?:{_PLAIN}|{_STRING})"
_FLOW_VALUE = rf"(?:[A-Za-z0-9][A-Za-z0-9._+-]*|{_STRING})"
_PAIR = rf"{_KEY}: {_FLOW_VALUE}"
_MAP = rf"\{{{_PAIR}(?:, {_PAIR})*\}}"
_SEQUENCE = rf"\[(?:{_FLOW_VALUE}(?:, {_FLOW_VALUE})*)?\]"
_FIELD = re.compile(rf"{_KEY}: (?:{_VALUE}|{_MAP}|{_SEQUENCE})")
_BLOCK_KEY = re.compile(rf"{_KEY}:")
_ITEM = re.compile(rf"  - {_MAP}")
_SURROGATE_PAIR = re.compile(r"[\ud800-\udbff][\udc00-\udfff]")
_KEPT_TAGS = {"tag:yaml.org,2002:str", "tag:yaml.org,2002:seq", "tag:yaml.org,2002:map", None}


def admitted(header: str) -> bool:
    """Whether every header line has one of the writer's restricted shapes."""
    if _FORBIDDEN.search(header):
        return False
    block = needs_item = False
    for line in header.removesuffix("\n").split("\n"):
        if block and _ITEM.fullmatch(line):
            needs_item = False
            continue
        if needs_item:
            return False
        block = _BLOCK_KEY.fullmatch(line) is not None
        needs_item = block
        if not block and not _FIELD.fullmatch(line):
            return False
    return not needs_item


def _join_pair(pair: re.Match[str]) -> str:
    return pair.group().encode("utf-16-le", "surrogatepass").decode("utf-16-le")


class TextConstructor(SafeConstructor):
    """The value-deciding constructors shared by the Python and C text loaders."""

    yaml_implicit_resolvers: dict[Any, Any] = {}  # noqa: RUF012
    yaml_constructors = {  # noqa: RUF012
        tag: build for tag, build in yaml.SafeLoader.yaml_constructors.items() if tag in _KEPT_TAGS
    }

    def construct_scalar(self, node: yaml.ScalarNode | yaml.MappingNode) -> Any:
        """Join each escaped UTF-16 surrogate pair into the character it encodes."""
        return _SURROGATE_PAIR.sub(_join_pair, super().construct_scalar(node))

    def construct_mapping(self, node: yaml.MappingNode, deep: bool = False) -> dict[Hashable, Any]:
        seen: set[str] = set()
        for key_node, _ in node.value:
            if isinstance(key_node, yaml.ScalarNode):
                if key_node.value in seen:
                    message = f"duplicate key {key_node.value!r}"
                    raise ConstructorError(None, None, message, key_node.start_mark)
                seen.add(key_node.value)
        return super().construct_mapping(node, deep)


if getattr(yaml, "__with_libyaml__", False):

    class _CTextLoader(TextConstructor, yaml.CSafeLoader):
        """The shared text constructors with libyaml's scanner and parser."""


def load_yaml(text: str) -> object:
    """The bare C loader; yamlio.load_yaml owns admission, dispatch, and fallback."""
    if not getattr(yaml, "__with_libyaml__", False):
        raise RuntimeError("libyaml is not available")
    return yaml.load(text, Loader=_CTextLoader)
