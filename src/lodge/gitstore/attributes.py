"""Conservative conversion detection, cached within a store object."""

import os
from collections.abc import Collection
from dataclasses import dataclass
from pathlib import Path

from lodge.gitstore import git
from lodge.gitstore.flags import Flagged, Flags, IndexStat, stat_key
from lodge.gitstore.trees import decode, encode

_ATTRIBUTES = ("text", "eol", "crlf", "filter", "ident", "working-tree-encoding")
_FALSE = {"", "false", "no", "off", "0"}


@dataclass(frozen=True)
class Source:
    path: str
    before: IndexStat
    raw: bytes | None
    after: IndexStat


@dataclass(frozen=True)
class ConversionKey:
    index: IndexStat
    config: tuple[str, str]
    variables: tuple[str | None, ...]
    sources: tuple[Source, ...]
    paths: frozenset[str]
    attributes: frozenset[str]


class Conversions:
    def __init__(self, root: Path, flags: Flags) -> None:
        self.root = root
        self.flags = flags
        self._cached: tuple[ConversionKey, frozenset[str]] | None = None
        self.info: Path | None = None

    def paths(self, paths: Collection[str], flagged: Flagged) -> frozenset[str]:
        before = self._key(paths, flagged)
        if self._cached is not None and self._cached[0] == before:
            return self._cached[1]
        if before.config[0].lower() not in _FALSE or None in before.variables:
            result = before.paths
        elif not flagged.attributes and not any(s.raw is not None for s in before.sources):
            result = frozenset()
        else:
            raw = (
                git.run_bytes(
                    ["check-attr", "--stdin", "-z", *_ATTRIBUTES],
                    self.root,
                    input=b"\0".join(encode(p) for p in sorted(before.paths)) + b"\0",
                )
                if before.paths
                else b""
            )
            fields = raw.split(b"\0")
            result = frozenset(
                decode(fields[i])
                for i in range(0, len(fields) - 2, 3)
                if fields[i + 2] not in (b"unspecified", b"unset")
            )
        self._cached = (before, result) if before == self._key(paths, flagged) else None
        return result

    def _key(self, paths: Collection[str], flagged: Flagged) -> ConversionKey:
        index = self.flags.key()
        if self.info is None:
            info = Path(git.run(["rev-parse", "--git-path", "info/attributes"], self.root))
            self.info = info if info.is_absolute() else self.root / info
        config = (self._config("core.autocrlf"), self._config("core.attributesFile", path=True))
        names = ["GIT_ATTR_GLOBAL"]
        if not os.environ.get("GIT_ATTR_NOSYSTEM"):
            names.append("GIT_ATTR_SYSTEM")
        variables = []
        for name in names:
            done = git.attempt(["var", name], self.root)
            variables.append(decode(done.stdout).strip() if done.returncode == 0 else None)
        sources = {self.root / ".gitattributes", self.info}
        sources.update(
            self.root / p
            for p in {*paths, *flagged.attributes}
            if p.rsplit("/", 1)[-1] == ".gitattributes"
        )
        for text in (*variables, config[1]):
            if text:
                path = Path(text).expanduser()
                sources.add(path if path.is_absolute() else self.root / path)
        held = []
        for path in sorted(sources):
            before = stat_key(path)
            try:
                raw = path.read_bytes()
            except OSError:
                raw = None
            held.append(Source(str(path), before, raw, stat_key(path)))
        return ConversionKey(
            index, config, tuple(variables), tuple(held), frozenset(paths), flagged.attributes
        )

    def _config(self, name: str, *, path: bool = False) -> str:
        args = ["config", *(["--path"] if path else []), "--get", name]
        done = git.attempt(args, self.root)
        return decode(done.stdout).strip() if done.returncode == 0 else ""
