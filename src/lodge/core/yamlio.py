"""Reading and quoting YAML so that every scalar is text and every text survives a round trip."""

import json
import re
from collections.abc import Hashable
from typing import Any

import yaml
from yaml.constructor import ConstructorError

_KEPT_TAGS = {"tag:yaml.org,2002:str", "tag:yaml.org,2002:seq", "tag:yaml.org,2002:map", None}
_UNREADABLE = re.compile(r"[\x00-\x1f\x7f-\x9f\u2028\u2029\ud800-\udfff\ufffe\uffff]")


_PAIR = re.compile(r"[\ud800-\udbff][\udc00-\udfff]")
LINE_BREAKS_AND_TABS = "\t\n\r"


class YamlError(ValueError):
    """A header that is not readable; `line` counts from 1 in the text given, when known."""

    def __init__(self, message: str, line: int | None = None) -> None:
        super().__init__(message)
        self.line = line


class _TextLoader(yaml.SafeLoader):
    """A safe loader with no implicit resolvers: `yes`, `14:14`, `~`, and `1234` stay text."""

    yaml_implicit_resolvers: dict[Any, Any] = {}  # noqa: RUF012
    yaml_constructors = {  # noqa: RUF012
        tag: build for tag, build in yaml.SafeLoader.yaml_constructors.items() if tag in _KEPT_TAGS
    }

    def construct_scalar(self, node: yaml.ScalarNode | yaml.MappingNode) -> Any:
        """Text with each escaped UTF-16 surrogate pair joined into the character it encodes."""
        return _PAIR.sub(_join_pair, super().construct_scalar(node))

    def construct_mapping(self, node: yaml.MappingNode, deep: bool = False) -> dict[Hashable, Any]:
        seen: set[str] = set()
        for key_node, _ in node.value:
            if isinstance(key_node, yaml.ScalarNode):
                if key_node.value in seen:
                    message = f"duplicate key {key_node.value!r}"
                    raise ConstructorError(None, None, message, key_node.start_mark)
                seen.add(key_node.value)
        return super().construct_mapping(node, deep)


def _join_pair(pair: re.Match[str]) -> str:
    return pair.group().encode("utf-16-le", "surrogatepass").decode("utf-16-le")


def load_yaml(text: str) -> object:
    """The one YAML document in `text`, with every scalar a `str`."""
    try:
        return yaml.load(text, Loader=_TextLoader)
    except yaml.MarkedYAMLError as error:
        mark = error.problem_mark
        problem = error.problem or "not valid YAML"
        raise YamlError(problem, None if mark is None else mark.line + 1) from error
    except RecursionError:
        raise YamlError("the header is nested too deeply") from None
    except yaml.reader.ReaderError as error:
        line = text.count("\n", 0, error.position) + 1
        raise YamlError(f"unreadable character {error.character!r}", line) from error


def unreadable_char(text: str, allowed: str = "") -> str | None:
    """The first character, not among `allowed`, that YAML cannot read back from a quoted string."""
    for found in _UNREADABLE.finditer(text):
        if found.group() not in allowed:
            return found.group()
    return None


def quoted(text: str, allowed: str = "") -> str:
    """`text` as a JSON string, which YAML reads back unchanged."""
    bad = unreadable_char(text, allowed)
    if bad is not None:
        raise ValueError(f"U+{ord(bad):04X} cannot be written in a header")
    return json.dumps(text, ensure_ascii=False)
