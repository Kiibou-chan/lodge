"""Pinned committed identities and lazy mappings for checkout reads."""

from collections.abc import Collection, Mapping
from dataclasses import dataclass
from pathlib import Path

from lodge.core import ATTACHMENTS, Listing, blob_id
from lodge.gitstore import git
from lodge.gitstore.trees import decode, encode

EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"


@dataclass(frozen=True)
class CommittedListing(Listing):
    kinds: Mapping[str, str]


class Committed:
    """Per-store mappings for at most the two most recently used pinned commits."""

    def __init__(self, root: Path) -> None:
        self.root = root
        self._trees: dict[str | None, str] = {}
        self._listings: dict[str | None, CommittedListing] = {}

    def remember(self, rev: str | None, ident: str) -> None:
        self._trees.pop(rev, None)
        self._trees[rev] = ident
        while len(self._trees) > 2:
            oldest = next(iter(self._trees))
            self._trees.pop(oldest)
            self._listings.pop(oldest, None)

    def tree_id(self, rev: str | None) -> str:
        if rev not in self._trees:
            done = (
                None
                if rev is None
                else git.attempt(["rev-parse", "--verify", f"{rev}:lodge/"], self.root)
            )
            ident = EMPTY_TREE if done is None or done.returncode else decode(done.stdout).strip()
            self.remember(rev, ident)
        return self._trees[rev]

    def listing(self, rev: str | None) -> CommittedListing:
        ident = self.tree_id(rev)
        if rev not in self._listings:
            blobs, attachments, kinds = {}, set(), {}
            raw = (
                b""
                if rev is None or ident == EMPTY_TREE
                else git.run_bytes(
                    ["ls-tree", "-r", "-z", "--full-tree", rev, "--", "lodge"], self.root
                )
            )
            for item in raw.split(b"\0"):
                meta, _, raw_path = item.partition(b"\t")
                fields, path = meta.split(b" "), decode(raw_path)
                if len(fields) != 3 or not path.startswith("lodge/"):
                    continue
                kinds[path] = decode(fields[1])
                if path.startswith(ATTACHMENTS):
                    attachments.add(path)
                else:
                    blobs[path] = decode(fields[2]) if fields[1] == b"blob" else blob_id(b"")
            self._listings[rev] = CommittedListing(rev, ident, blobs, frozenset(attachments), kinds)
        return self._listings[rev]

    def folder(self, rev: str | None, path: str) -> Mapping[str, str]:
        """List only the immediate base entries of one relisted folder."""
        if rev is None or self.tree_id(rev) == EMPTY_TREE:
            return {}
        done = git.attempt(["ls-tree", "-z", f"{rev}:{path}"], self.root)
        if done.returncode:
            return {}
        entries = {}
        for item in done.stdout.split(b"\0"):
            meta, _, name = item.partition(b"\t")
            fields = meta.split(b" ")
            if len(fields) == 3:
                entries[decode(name)] = (
                    "folder"
                    if fields[1] == b"tree"
                    else "link"
                    if fields[0] == b"120000"
                    else "file"
                    if fields[1] == b"blob"
                    else "other"
                )
        return entries

    def selected(
        self, rev: str | None, paths: Collection[str], nonblobs: Collection[str] = ()
    ) -> CommittedListing:
        """Look up changed inputs without enumerating the base's names."""
        if rev in self._listings:
            return self._listings[rev]
        blobs, attachments, kinds = {}, set(), {}
        selected = sorted(paths) if rev is not None else []
        queries = [p for p in selected if p not in nonblobs]
        # Ordinary queries are rev:path lines; NUL input admits names with line breaks.
        nul = any("\n" in p for p in queries)
        separator = b"\0" if nul else b"\n"
        raw = (
            git.run_bytes(
                ["cat-file", "--batch-check", *(["-z"] if nul else [])],
                self.root,
                input=b"".join(encode(f"{rev}:{p}") + separator for p in queries),
            )
            if queries
            else b""
        )
        objects = {}
        offset = 0
        for path in queries:
            missing = encode(f"{rev}:{path} missing\n")
            if raw.startswith(missing, offset):
                offset += len(missing)
                continue
            end = raw.find(b"\n", offset)
            fields = raw[offset:end].split(b" ")
            offset = end + 1
            if len(fields) != 3:
                raise ValueError("invalid git batch-check output")
            objects[path] = decode(fields[0]), decode(fields[1])
        for path in selected:
            if path in nonblobs:
                key, kind = blob_id(b""), "commit"
            elif path in objects:
                key, kind = objects[path]
            else:
                continue
            if kind == "tree":
                continue
            kinds[path] = kind
            if path.startswith(ATTACHMENTS):
                attachments.add(path)
            else:
                blobs[path] = key if kind == "blob" else blob_id(b"")
        return CommittedListing(rev, self.tree_id(rev), blobs, frozenset(attachments), kinds)
