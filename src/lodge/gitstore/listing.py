"""Resolved listings and selected texts for checkout and branch reads."""

from collections.abc import Callable, Collection, Mapping
from pathlib import Path
from typing import Protocol

from lodge.app import LodgeError
from lodge.core import Listing
from lodge.gitstore import git
from lodge.gitstore.accepted import accept, rewritten
from lodge.gitstore.errors import NOT_INITIALISED, NotInitialised
from lodge.gitstore.identity import CheckoutIdentity, committed
from lodge.gitstore.lock import LockHeld, locked
from lodge.gitstore.published import _not_found
from lodge.gitstore.settings import StoreSettings
from lodge.gitstore.trees import decode


class CheckoutListing:
    def __init__(self, root: Path, settings: StoreSettings, exists: Callable[[Path], bool]) -> None:
        self.root = root
        self.settings = settings
        self.exists = exists
        self.identity = CheckoutIdentity(root)
        self.missing: str | None = None
        self._states: tuple[Listing, Listing] | None = None
        self._disk_texts: dict[str, str] = {}

    def identities(self) -> tuple[str, str]:
        if not self.exists(self.root):
            raise NotInitialised(NOT_INITIALISED)
        head = git.resolve(self.root, "HEAD")
        current, texts = self.identity.current(head)
        published, self.missing = _published(self.root, self.settings, head)
        self._states = current, committed(self.root, published)
        self._disk_texts.update(texts)
        return current.ident, self._states[1].ident

    def listings(self) -> tuple[Listing, Listing]:
        if self._states is None:
            self.identities()
        assert self._states is not None
        return self._states

    def texts(self, listing: Listing, paths: Collection[str]) -> dict[str, str]:
        return _texts(self.root, listing, paths, self._disk_texts)


class BranchSource(Protocol):
    _root: Path
    _common: Path
    _wait: float
    _ref: str
    _held: LockHeld | None
    _rev: str | None

    def _needs_fetch(self) -> bool: ...
    def _fetch(self) -> None: ...
    def _missing(self) -> LodgeError: ...


class BranchListing:
    def __init__(self, source: BranchSource) -> None:
        self.source = source
        self._states: tuple[Listing, Listing] | None = None

    def identities(self) -> tuple[str, str]:
        s = self.source
        held: LockHeld | None = None
        if s._needs_fetch():
            try:
                with locked(s._common, s._wait):
                    if s._needs_fetch():
                        s._fetch()
            except LockHeld as error:
                held = error
        tip = git.resolve(s._root, s._ref)
        if tip is None:
            raise held or s._missing()
        s._held, s._rev = held, tip
        kept = rewritten(s._root, tip)
        accept(s._root, tip)
        current = committed(s._root, tip)
        self._states = current, current if kept is None else committed(s._root, kept)
        return current.ident, self._states[1].ident

    def listings(self) -> tuple[Listing, Listing]:
        if self._states is None:
            self.identities()
        assert self._states is not None
        return self._states

    def texts(self, listing: Listing, paths: Collection[str]) -> dict[str, str]:
        return _texts(self.source._root, listing, paths, {})


def _published(root: Path, s: StoreSettings, head: str | None) -> tuple[str | None, str | None]:
    """Resolve exactly as published_state, without reading any record texts."""
    if head is None:
        return None, None
    tried = f"{s.remote}/{s.base}"
    base = git.resolve(root, f"refs/remotes/{tried}") or git.resolve(root, f"refs/heads/{s.base}")
    merged = None if base is None else git.attempt(["merge-base", head, base], root)
    if merged is None or merged.returncode != 0 or not merged.stdout.strip():
        return None, _not_found(tried, s.base)
    return decode(merged.stdout).strip(), None


def _texts(
    root: Path, listing: Listing, paths: Collection[str], disk: Mapping[str, str]
) -> dict[str, str]:
    wanted = {path: listing.blobs[path] for path in paths}
    hashes = sorted(set(wanted.values()) - disk.keys())
    contents = {key: disk[key] for key in wanted.values() if key in disk}
    if hashes:
        raw = git.run_bytes(["cat-file", "--batch"], root, input="\n".join(hashes) + "\n")
        position = 0
        for key in hashes:
            end = raw.index(b"\n", position)
            header = raw[position:end].split(b" ")
            if len(header) != 3:
                raise LodgeError(f"git cannot read the file {key}")
            start, size = end + 1, int(header[2])
            contents[key] = decode(raw[start : start + size]) if header[1] == b"blob" else ""
            position = start + size + 1
    return {path: contents[key] for path, key in wanted.items()}
