"""The settings core reads from `.lodge.toml`: `[length]` and `[import]`."""

from collections.abc import Mapping
from dataclasses import dataclass, field, fields


class SettingsError(ValueError):
    pass


@dataclass(frozen=True)
class LengthGuidance:
    title_chars: int = 100
    decision_statement_words: int = 80
    spec_statement_words: int = 150
    reasoning_words: int = 1000


@dataclass(frozen=True)
class CoreSettings:
    length: LengthGuidance = field(default_factory=LengthGuidance)
    import_sources: tuple[str, ...] = ()


OTHER_PACKAGES = frozenset({"store", "hook"})


def parse_core_settings(table: Mapping[str, object]) -> CoreSettings:
    """Read `[length]` and `[import]` from a parsed TOML table; other keys are errors."""
    for name, value in table.items():
        if name in OTHER_PACKAGES or name in {"length", "import"}:
            continue
        if isinstance(value, Mapping):
            raise SettingsError(f"unknown section [{name}]")
        raise SettingsError(f"unknown key {name}")
    return CoreSettings(
        length=_length(_section(table, "length")),
        import_sources=_sources(_section(table, "import")),
    )


def _section(table: Mapping[str, object], name: str) -> Mapping[str, object]:
    section = table.get(name, {})
    if not isinstance(section, Mapping):
        raise SettingsError(f"{name} must be a table")
    return section


def _length(section: Mapping[str, object]) -> LengthGuidance:
    names = {item.name for item in fields(LengthGuidance)}
    values: dict[str, int] = {}
    for key, value in section.items():
        if key not in names:
            raise SettingsError(f"unknown key length.{key}")
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise SettingsError(f"length.{key} must be a positive whole number")
        values[key] = value
    return LengthGuidance(**values)


def _sources(section: Mapping[str, object]) -> tuple[str, ...]:
    for key in section:
        if key != "sources":
            raise SettingsError(f"unknown key import.{key}")
    sources = section.get("sources", [])
    if not isinstance(sources, list) or not all(isinstance(s, str) and s for s in sources):
        raise SettingsError("import.sources must be a list of file names")
    return tuple(sources)
