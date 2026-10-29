"""The settings of `.lodge.toml` that the store reads, and the file as a whole."""

import re
import tomllib
from collections.abc import Mapping
from dataclasses import dataclass, fields
from pathlib import Path
from typing import Literal

from lodge.app import LodgeError, core_settings
from lodge.core import CoreSettings

_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._/-]*")


@dataclass(frozen=True)
class StoreSettings:
    mode: Literal["checkout", "branch"] = "checkout"
    branch: str = "lodge"
    remote: str = "origin"
    base: str = "main"
    max_staleness_seconds: int = 60
    commit_trailer: str | None = None


@dataclass(frozen=True)
class ProjectSettings:
    core: CoreSettings
    store: StoreSettings
    raw: Mapping[str, object]


def load_settings(root: Path) -> ProjectSettings:
    """`.lodge.toml` at `root`, defaults when it is absent; every defect is a `LodgeError`."""
    table = _read(root / ".lodge.toml")
    return ProjectSettings(core_settings(table), _store(table.get("store", {})), table)


def _read(path: Path) -> Mapping[str, object]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return {}
    except (OSError, UnicodeDecodeError) as error:
        raise LodgeError(f".lodge.toml: cannot be read: {error}") from error
    try:
        return tomllib.loads(text)
    except tomllib.TOMLDecodeError as error:
        raise LodgeError(f".lodge.toml: {error}") from error


def _store(section: object) -> StoreSettings:
    if not isinstance(section, Mapping):
        raise LodgeError(".lodge.toml: store must be a table")
    known = {item.name for item in fields(StoreSettings)}
    for key in section:
        if key not in known:
            raise LodgeError(f".lodge.toml: unknown key store.{key}")
    return StoreSettings(
        mode=_mode(section.get("mode", "checkout")),
        branch=_name(section, "branch", "lodge"),
        remote=_name(section, "remote", "origin"),
        base=_name(section, "base", "main"),
        max_staleness_seconds=_seconds(section.get("max_staleness_seconds", 60)),
        commit_trailer=_trailer(section.get("commit_trailer")),
    )


def _mode(value: object) -> Literal["checkout", "branch"]:
    if value == "checkout":
        return "checkout"
    if value == "branch":
        return "branch"
    raise LodgeError('.lodge.toml: store.mode must be "checkout" or "branch"')


def _name(section: Mapping[str, object], key: str, default: str) -> str:
    value = section.get(key, default)
    if not isinstance(value, str) or not _NAME.fullmatch(value) or ".." in value:
        raise LodgeError(
            f".lodge.toml: store.{key} must be a name of letters, digits, and . _ / -, "
            "not starting with a symbol"
        )
    return value


def _seconds(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise LodgeError(
            ".lodge.toml: store.max_staleness_seconds must be a whole number of 0 or more"
        )
    return value


def _trailer(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise LodgeError(".lodge.toml: store.commit_trailer must be a non-empty string")
    return value
