"""The errors a command reports as one sentence."""

from collections.abc import Mapping

from lodge.core import CoreSettings, SettingsError, parse_core_settings


class LodgeError(Exception):
    """A usage or environment error; the command line exits 2."""

    exit_code: int = 2


class NotFound(LodgeError):
    """No record or area has the name given; the command line exits 2."""


class Conflict(LodgeError):
    """Another change got in the way; the command line exits 1."""

    exit_code = 1


def core_settings(table: Mapping[str, object]) -> CoreSettings:
    """The core settings of a parsed `.lodge.toml`, an error in them reported as a `LodgeError`."""
    try:
        return parse_core_settings(table)
    except SettingsError as error:
        raise LodgeError(f".lodge.toml: {error}") from error
