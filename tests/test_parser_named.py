"""Named-command parsing preserves the complete parser's public text."""

from __future__ import annotations

import argparse
from collections.abc import Callable
from unittest.mock import patch

import pytest

from lodge.cli import parser as grammar

COMMANDS = (
    "init",
    "id",
    "search",
    "show",
    "draft",
    "add",
    "check",
    "spec",
    "waiting",
    "guide",
    "view",
    "hook",
    "threads",
    "thread",
    "ask",
    "reply",
    "close",
)


def answer(
    capsys: pytest.CaptureFixture[str], argv: list[str], full: bool
) -> tuple[object, str, str]:
    factory = grammar._parser
    with patch.object(
        grammar, "_parser", side_effect=lambda *args: factory() if full else factory(*args)
    ):
        result = grammar.parse(argv)
    captured = capsys.readouterr()
    return result, captured.out, captured.err


def test_help_texts_unchanged(capsys: pytest.CaptureFixture[str]) -> None:
    for argv in (["--help"], ["-h"], ["--version"], *([name, "--help"] for name in COMMANDS)):
        assert answer(capsys, argv, False) == answer(capsys, argv, True)


def test_errors_unchanged(capsys: pytest.CaptureFixture[str]) -> None:
    for argv in (
        [],
        ["unknown"],
        *([name] for name in COMMANDS),
        *([name, "--bad-option"] for name in COMMANDS),
    ):
        assert answer(capsys, argv, False) == answer(capsys, argv, True)


def test_named_parser_builds_one_subcommand() -> None:
    original: Callable[..., argparse.ArgumentParser] = argparse._SubParsersAction.add_parser
    made: list[str] = []

    def counted(
        self: argparse._SubParsersAction[argparse.ArgumentParser], name: str, **kwargs: object
    ) -> argparse.ArgumentParser:
        made.append(name)
        return original(self, name, **kwargs)

    with patch.object(argparse._SubParsersAction, "add_parser", counted):
        assert grammar.parse(["guide", "--read"]) == grammar.Guide(True)
    assert made == ["guide"]
