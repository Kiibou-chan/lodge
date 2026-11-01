"""Process-local index flags and indexed attributes sources."""

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
        self._cached: tuple[IndexStat, Flagged] | None = None

    def key(self) -> IndexStat:
        if self.index is None:
            index = Path(git.run(["rev-parse", "--git-path", "index"], self.root))
            self.index = index if index.is_absolute() else self.root / index
        return stat_key(self.index)

    def read(self) -> Flagged:
        before = self.key()
        if self._cached is not None and self._cached[0] == before:
            return self._cached[1]
        raw = git.run_bytes(
            ["ls-files", "-t", "-v", "-z", "--", "lodge", ".gitattributes"], self.root
        )
        paths, attributes = set(), set()
        for item in raw.split(b"\0"):
            if len(item) < 3:
                continue
            tag, path = chr(item[0]), decode(item[2:])
            if path.startswith("lodge/") and (tag == "S" or tag.islower()):
                paths.add(path)
            if path.rsplit("/", 1)[-1] == ".gitattributes":
                attributes.add(path)
        result = Flagged(frozenset(paths), frozenset(attributes))
        self._cached = (before, result) if before == self.key() else None
        return result
