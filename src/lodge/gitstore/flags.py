"""Process-local index flags and indexed attributes sources."""

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from lodge.gitstore import git
from lodge.gitstore.trees import decode

IndexStat = tuple[int, int, int, int] | None


def stat_key(path: Path) -> IndexStat:
    try:
        held = path.stat()
        return held.st_ino, held.st_size, held.st_mtime_ns, held.st_ctime_ns
    except OSError:
        return None


@dataclass(frozen=True)
class Flagged:
    paths: frozenset[str]
    attributes: frozenset[str]


class Flags:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.index: Path | None = None

    def key(self) -> IndexStat:
        if self.index is None:
            index = Path(git.run(["rev-parse", "--git-path", "index"], self.root))
            self.index = index if index.is_absolute() else self.root / index
        return stat_key(self.index)


def scan(raw: bytes) -> Flagged:
    """Decode index flags and attributes names, with a clean-index shortcut."""
    if raw and not raw.endswith(b"\0"):
        raw += b"\0"
    count = raw.count(b"\0") + int(bool(raw) and not raw.endswith(b"\0"))
    clean = raw.count(b"\0H ") + int(raw.startswith(b"H "))
    paths, attributes = set(), set()
    if count != clean:
        for item in raw.split(b"\0"):
            if len(item) < 3:
                continue
            tag, path = chr(item[0]), decode(item[2:])
            if path.startswith("lodge/") and (tag == "S" or tag.islower()):
                paths.add(path)
    offset = 0
    while (end := raw.find(b".gitattributes\0", offset)) >= 0:
        start = raw.rfind(b"\0", 0, end) + 1
        path = decode(raw[start + 2 : end + len(b".gitattributes")])
        if path == ".gitattributes" or path.endswith("/.gitattributes"):
            attributes.add(path)
        offset = end + len(b".gitattributes") + 1
    return Flagged(frozenset(paths), frozenset(attributes))


def config_values(raw: bytes) -> Mapping[str, str | None]:
    """Decode git config's NUL-separated key/newline/value entries."""
    values: dict[str, str | None] = {}
    for item in raw.split(b"\0"):
        if item:
            key, separator, value = item.partition(b"\n")
            values[decode(key)] = decode(value) if separator else None
    return values
