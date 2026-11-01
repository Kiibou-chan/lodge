"""Seeded differential testing against the unchanged Python text loader."""

import json
import random
from collections.abc import Callable

import yaml

from lodge.core import yamlfast, yamlio

LIBYAML = bool(getattr(yaml, "__with_libyaml__", False))
SEED = 20261101


def python_yaml(text: str) -> object:
    """The pre-Task-3 loader, including its exact error message and line conversion."""
    try:
        return yaml.load(text, Loader=yamlio._TextLoader)
    except yaml.MarkedYAMLError as error:
        mark = error.problem_mark
        raise yamlio.YamlError(
            error.problem or "not valid YAML", None if mark is None else mark.line + 1
        ) from error
    except RecursionError:
        raise yamlio.YamlError("the header is nested too deeply") from None
    except yaml.reader.ReaderError as error:
        line = text.count("\n", 0, error.position) + 1
        raise yamlio.YamlError(f"unreadable character {error.character!r}", line) from error


def outcome(loader: Callable[[str], object], text: str) -> tuple[object, ...]:
    try:
        return ("value", loader(text))
    except yamlio.YamlError as error:
        return ("error", str(error), error.line)


def test_admitted_headers_parse_the_same() -> None:
    rng = random.Random(SEED)
    scalars = [
        "yes",
        "no",
        "null",
        "1234",
        "14:14",
        "2026-10-31T10:00:00+01:00",
        "A-1.why",
        '"\\ud83d\\ude00"',
        '"\\uD800"',
        '"\\u0001"',
        '"\\uD7FF\\uE000"',
        '"\\/\\b\\f\\n\\r\\t\\\\\\""',
        *(
            json.dumps(value, ensure_ascii=False)
            for value in (
                "",
                "Café 船 😀",
                'a "quote" and \\ slash',
                "comma, colon: {a} [b] # | & * ! % ?",
                "\x80",
                "\x85",
                "\u2028",
                "\u2029",
                "\ufeff",
                "\ufffe",
                "\uffff",
            )
        ),
    ]
    for _ in range(250):
        scalars.append(
            rng.choice("aA019")
            + "".join(rng.choices("aAZ019._:+-", k=rng.randrange(24))).rstrip(":")
        )
        scalars.append(
            json.dumps(
                "".join(
                    rng.choices('aZ09 .,:{}[]#|>&*!%?"\\/\b\f\n\r\tCafé船😀', k=rng.randrange(32))
                ),
                ensure_ascii=bool(rng.randrange(2)),
            )
        )
    admitted_count = c_successes = 0
    for n in range(20_000):
        lines: list[str] = []
        for _ in range(rng.randint(1, 3)):
            key = "".join(rng.choices("abcde_", k=rng.randint(1, 6)))
            value = rng.choice(scalars)
            other = rng.choice(scalars)
            shape = rng.randrange(5)
            lines.append(
                [
                    f"{key}: {value}",
                    f"{key}:\n  - {{a: {value}, b: {other}}}",
                    f"{key}: {{a: {value}, b: {other}}}",
                    f"{key}: [{value}, {other}]",
                    f"{key}: []",
                ][shape]
            )
        header = "\n".join(lines)
        if rng.randrange(2):
            position = rng.randrange(len(header))
            mutation = rng.choice(
                ["\t", "#", "|", "&", "\ufeff", "\u2028", "delete_quote", "indent"]
            )
            if mutation == "delete_quote":
                header = header.replace('"', "", 1)
            else:
                if mutation == "indent":
                    position = header.rfind("\n", 0, position) + 1
                    mutation = " "
                header = header[:position] + mutation + header[position:]
        context = f"seed={SEED}, case={n}, header={header!r}"
        if yamlfast.admitted(header):
            admitted_count += 1
            if LIBYAML:
                try:
                    fast = yamlfast.load_yaml(header)
                except Exception:
                    pass  # A C failure is allowed, but the public loader must fall back below.
                else:
                    c_successes += 1
                    assert ("value", fast) == outcome(python_yaml, header), context
        assert outcome(yamlio.load_yaml, header) == outcome(python_yaml, header), context
    print(f"seed={SEED}: libyaml parsed {c_successes}/{admitted_count} admitted headers")
    assert admitted_count > 1000
    if LIBYAML:
        assert c_successes > 1000
