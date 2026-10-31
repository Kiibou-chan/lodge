"""A file as a YAML header between `---` lines and a Markdown body."""

import re
from collections.abc import Callable, Mapping

from lodge.core.fields import FormatError
from lodge.core.model import Problem
from lodge.core.yamlio import YamlError, load_yaml

REASONING_HEADING = "## Reasoning"
_LONE_SURROGATE = re.compile(r"[\ud800-\udfff]")


def normalise_newlines(text: str) -> str:
    return text.replace("\r\n", "\n")


def split_document(text: str) -> tuple[str, str]:
    """The header text and the body of a file; the header lies between the first two `---` lines."""
    if _LONE_SURROGATE.search(text):
        raise FormatError("the text is not valid UTF-8")
    lines = normalise_newlines(text).split("\n")
    if lines[0] != "---":
        raise FormatError("the file must start with a --- line opening its header")
    for index in range(1, len(lines)):
        if lines[index] == "---":
            return "\n".join(lines[1:index]), "\n".join(lines[index + 1 :])
    raise FormatError("the header is not closed by a --- line")


def load_header(header_text: str) -> dict[str, object]:
    """The header as a mapping; error lines count from the file's first line."""
    try:
        loaded = load_yaml(header_text)
    except YamlError as error:
        line = None if error.line is None else error.line + 1
        raise FormatError(f"the header is not valid YAML: {error}", line=line) from error
    if not isinstance(loaded, Mapping):
        raise FormatError("the header must be a mapping of keys to values")
    return {str(key): value for key, value in loaded.items()}


def has_reasoning_heading(text: str) -> bool:
    return any(line.rstrip() == REASONING_HEADING for line in text.split("\n"))


def trim_block(text: str) -> str:
    """`text` without the blank lines before it and the whitespace after it; indentation stays."""
    lines = text.split("\n")
    while lines and not lines[0].strip():
        lines.pop(0)
    return "\n".join(lines).rstrip()


def split_reasoning(body: str) -> tuple[str, str]:
    """The statement above the first `## Reasoning` line and the reasoning below it."""
    lines = body.split("\n")
    for index, line in enumerate(lines):
        if line.rstrip() == REASONING_HEADING:
            return trim_block("\n".join(lines[:index])), trim_block("\n".join(lines[index + 1 :]))
    return trim_block(body), ""


def assemble(header: list[str], body: str) -> str:
    text = "---\n" + "\n".join(header) + "\n---\n"
    return f"{text}\n{body}\n" if body else text


def read_with[T](path: str, text: str, build: Callable[[dict[str, object], str], T]) -> T | Problem:
    """`build` applied to the header and body of `text`, or the format problem it hit."""
    header_text = ""
    try:
        header_text, body = split_document(text)
        return build(load_header(header_text), body)
    except FormatError as error:
        return problem_for(path, error, header_text)


def problem_for(path: str, error: FormatError, header_text: str) -> Problem:
    """Problem 1 for `error`, with the line of its key in `header_text` when that is known."""
    line = error.line if error.line is not None else key_line(header_text, error.key)
    return Problem(path, 1, str(error), line)


def key_line(header_text: str, key: str | None) -> int | None:
    """The file line where the top-level `key` starts, for a dotted key its first part."""
    if key is None:
        return None
    top = key.split(".")[0]
    for index, line in enumerate(header_text.split("\n")):
        if line.startswith(f"{top}:"):
            return index + 2
    return None
