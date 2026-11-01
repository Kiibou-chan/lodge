"""Resolved listings and selected texts for checkout and branch reads."""

from collections.abc import Callable, Collection, Mapping
from pathlib import Path
from typing import Protocol

from lodge.app import LodgeError
from lodge.core import Listing, blob_id
from lodge.gitstore import git
from lodge.gitstore.accepted import accept, rewritten
from lodge.gitstore.errors import NOT_INITIALISED, NotInitialised
from lodge.gitstore.identity import CheckoutIdentity, Committed
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
        self._published_rev: str | None = None

    def identities(self) -> tuple[str, str]:
        if not self.exists(self.root):
            raise NotInitialised(NOT_INITIALISED)
        head = git.resolve(self.root, "HEAD")
        trunk = _trunk(self.root, self.settings) if head is not None else None
        current, texts = self.identity.current(head, trunk)
        published = self.identity.published
        self.missing = (
            _not_found(f"{self.settings.remote}/{self.settings.base}", self.settings.base)
            if head is not None and published is None
            else None
        )
        self._published_rev = published
        self._states = current, current  # The published mapping is materialised only on demand.
        self._disk_texts.update(texts)
        return current.ident, self.identity.committed.tree_id(published)

    def listings(self) -> tuple[Listing, Listing]:
        if self._states is None:
            self.identities()
        assert self._states is not None
        return self._states[0], self.identity.committed.listing(self._published_rev)

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
        self.committed = Committed(source._root)
        self._revs: tuple[str, str | None] | None = None
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
        self._revs = tip, tip if kept is None else kept
        self._states = None
        return self.committed.tree_id(self._revs[0]), self.committed.tree_id(self._revs[1])

    def listings(self) -> tuple[Listing, Listing]:
        if self._revs is None:
            self.identities()
        assert self._revs is not None
        if self._states is None:
            self._states = (
                self.committed.listing(self._revs[0]),
                self.committed.listing(self._revs[1]),
            )
        return self._states

    def texts(self, listing: Listing, paths: Collection[str]) -> dict[str, str]:
        return _texts(self.source._root, listing, paths, {})


def _trunk(root: Path, s: StoreSettings) -> str | None:
    """Pin the trunk before the git group, preserving remote-first resolution."""
    return git.resolve(root, f"refs/remotes/{s.remote}/{s.base}") or git.resolve(
        root, f"refs/heads/{s.base}"
    )


def _texts(
    root: Path, listing: Listing, paths: Collection[str], disk: Mapping[str, str]
) -> dict[str, str]:
    wanted = {path: listing.blobs[path] for path in paths}
    disk = {blob_id(b""): "", **disk}
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
