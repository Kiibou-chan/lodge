"""Read draft and message files with command-line errors."""

from pathlib import Path

from lodge.app import LodgeError


def read_file(name: str, not_utf8: str, exact: bool) -> str:
    try:
        if exact:
            return Path(name).read_bytes().decode("utf-8")
        return Path(name).read_text(encoding="utf-8")
    except UnicodeDecodeError:
        raise LodgeError(f"{name}: {not_utf8}") from None
    except OSError as error:
        raise LodgeError(f"{name}: cannot be read: {error.strerror or error}") from error
