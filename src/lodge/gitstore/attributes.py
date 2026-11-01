"""Conservative conversion detection, cached within a store object by its sources."""

import os
import subprocess
from collections.abc import Callable, Collection
from dataclasses import dataclass
from pathlib import Path

from lodge.gitstore import disk, git
from lodge.gitstore.flags import Flagged, Flags, IndexStat, config_values, stat_key
from lodge.gitstore.trees import decode, encode

_ATTRIBUTES = ("text", "eol", "crlf", "filter", "ident", "working-tree-encoding")
_FALSE = {"", "false", "no", "off", "0"}
PathSource = Collection[str] | Callable[[], Collection[str]]


@dataclass(frozen=True)
class Source:
    path: str
    before: IndexStat
    raw: bytes | None
    after: IndexStat


@dataclass(frozen=True)
class ConversionKey:
    index: IndexStat
    config: tuple[tuple[str, str | None], ...]
    variables: tuple[str | None, ...]
    sources: tuple[Source, ...]
    attributes: frozenset[str]
    failed: bool


def configuration(
    root: Path,
) -> tuple[subprocess.CompletedProcess[bytes], subprocess.CompletedProcess[bytes]]:
    return git.attempt(["config", "--list", "-z"], root), git.attempt(["var", "-l"], root)


class Conversions:
    def __init__(self, root: Path, flags: Flags) -> None:
        self.root = root
        self.flags = flags
        self._cached: tuple[ConversionKey, frozenset[str]] | None = None
        self.info: Path | None = None

    def discard(self) -> None:
        self._cached = None

    def paths(
        self,
        paths: PathSource,
        flagged: Flagged,
        *,
        attributes: Collection[str] | None = None,
        config: tuple[subprocess.CompletedProcess[bytes], subprocess.CompletedProcess[bytes]]
        | None = None,
    ) -> frozenset[str]:
        if attributes is None:
            walked = disk.walk(self.root)
            try:
                attributes = {p for p in walked.names if p.endswith("/.gitattributes")}
            finally:
                walked.close()
        before = self._key(flagged, attributes, config)
        if self._cached is not None and self._cached[0] == before:
            return self._cached[1]
        values = dict(before.config)
        autocrlf = values.get("core.autocrlf", "false")
        if (
            not before.failed
            and None not in before.variables
            and autocrlf is not None
            and autocrlf.lower() in _FALSE
            and not flagged.attributes
            and not any(s.raw is not None for s in before.sources)
        ):
            result = frozenset[str]()
        else:
            names = frozenset(paths() if callable(paths) else paths)
            if (
                before.failed
                or autocrlf is None
                or autocrlf.lower() not in _FALSE
                or None in before.variables
            ):
                result = names
            else:
                done = (
                    git.attempt(
                        ["check-attr", "--stdin", "-z", *_ATTRIBUTES],
                        self.root,
                        input=b"\0".join(encode(p) for p in sorted(names)) + b"\0",
                    )
                    if names
                    else None
                )
                fields = [] if done is None else done.stdout.split(b"\0")
                result = (
                    names
                    if done is not None and done.returncode
                    else frozenset(
                        decode(fields[i])
                        for i in range(0, len(fields) - 2, 3)
                        if fields[i + 2] not in (b"unspecified", b"unset")
                    )
                )
        self._cached = (
            (before, result) if before == self._key(flagged, attributes, config) else None
        )
        return result

    def _key(
        self,
        flagged: Flagged,
        attributes: Collection[str],
        config: tuple[subprocess.CompletedProcess[bytes], subprocess.CompletedProcess[bytes]]
        | None,
    ) -> ConversionKey:
        index = self.flags.key()
        if self.info is None:
            info = Path(git.run(["rev-parse", "--git-path", "info/attributes"], self.root))
            self.info = info if info.is_absolute() else self.root / info
        configured, variables = config or configuration(self.root)
        values = config_values(configured.stdout)
        known = dict(
            line.split("=", 1) for line in decode(variables.stdout).splitlines() if "=" in line
        )
        names = ["GIT_ATTR_GLOBAL"]
        if not os.environ.get("GIT_ATTR_NOSYSTEM"):
            names.append("GIT_ATTR_SYSTEM")
        resolved: list[str | None] = []
        for name in names:
            if name in known:
                resolved.append(known[name])
            else:
                done = git.attempt(["var", name], self.root)
                resolved.append(decode(done.stdout).strip() if done.returncode == 0 else None)
        sources = {self.root / ".gitattributes", self.info}
        sources.update(self.root / p for p in {*attributes, *flagged.attributes})
        for text in (*resolved, values.get("core.attributesfile")):
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
            index,
            tuple(sorted(values.items())),
            tuple(resolved),
            tuple(held),
            flagged.attributes,
            configured.returncode != 0 or variables.returncode != 0,
        )
