"""Checkout identity from a pinned committed base and a descriptor-read overlay."""

from collections.abc import Mapping
from dataclasses import dataclass
from functools import partial
from hashlib import sha1
from pathlib import Path

from lodge.core import ATTACHMENTS, Listing, blob_id
from lodge.gitstore import disk, git
from lodge.gitstore.attributes import Conversions
from lodge.gitstore.flags import Flags, scan
from lodge.gitstore.trees import decode, encode

EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
_DIFF = ["-c", "core.fsmonitor=false", "-c", "core.checkStat=default", "-c", "core.trustctime=true"]


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


def read_paths(base: set[str], present: set[str], changed: set[str]) -> set[str]:
    """Interim R11-A: read every file, even after all conversion sources are removed."""
    return base | present | changed


class CheckoutIdentity:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.flags = Flags(root)
        self.conversions = Conversions(root, self.flags)
        self.committed = Committed(root)
        self.published: str | None = None

    def current(self, rev: str | None, trunk: str | None = None) -> tuple[Listing, dict[str, str]]:
        for _ in range(3):
            before = self.flags.key()
            calls = [
                [
                    *_DIFF,
                    "diff-index",
                    "--cached",
                    "--no-renames",
                    "-z",
                    "--name-only",
                    rev or EMPTY_TREE,
                    "--",
                    "lodge",
                ],
                [*_DIFF, "diff-files", "--no-renames", "-z", "--name-only", "--", "lodge"],
                ["ls-files", "-t", "-v", "-z", "--", "lodge", ".gitattributes"],
                ["config", "--list", "-z"],
                ["var", "-l"],
                ["rev-parse", *([f"{rev}:lodge/"] if rev is not None else [])],
                ["merge-base", rev or EMPTY_TREE, trunk or EMPTY_TREE],
            ]
            results = git.run_many(calls, self.root)
            if before != self.flags.key():
                self.conversions.discard()
                continue
            merged = results[6]
            self.published = decode(merged.stdout).strip() if merged.returncode == 0 else None
            resolved = results[5]
            if rev is not None and resolved.returncode == 0:
                self.committed.remember(rev, decode(resolved.stdout).strip())
            self.committed.tree_id(self.published)
            base = self.committed.listing(rev)
            flagged = scan(results[2].stdout)
            walked = disk.walk(self.root)
            try:
                base_paths = {*base.blobs, *base.attachments}
                present = set(walked.names)
                changed = base_paths ^ present
                changed.update(flagged.paths)
                changed.update(p for p, kind in base.kinds.items() if kind != "blob")
                changed.update(
                    self.conversions.paths(
                        partial(set.union, base_paths, present),
                        flagged,
                        attributes={p for p in walked.names if p.endswith("/.gitattributes")},
                        config=(results[3], results[4]),
                    )
                )
                for done in results[:2]:
                    if done.returncode:
                        changed.update(base_paths)
                    changed.update(decode(p) for p in done.stdout.split(b"\0") if p)
                listing, texts = self._overlay(
                    base, walked, read_paths(base_paths, present, changed)
                )
            finally:
                walked.close()
            if before == self.flags.key():
                return listing, texts
            self.conversions.discard()
        merged = git.attempt(["merge-base", rev or EMPTY_TREE, trunk or EMPTY_TREE], self.root)
        self.published = decode(merged.stdout).strip() if merged.returncode == 0 else None
        exact = disk.tree(self.root)
        pieces = "\n".join(f"{p}\0{k}" for p, k in sorted(exact.blobs.items()))
        pieces += "\0" + "\0".join(sorted(exact.attachments))
        ident = sha1(encode(pieces)).hexdigest()
        return Listing(rev, ident, exact.blobs, exact.attachments), {
            exact.blobs[p]: t for p, t in exact.files.items()
        }

    def _overlay(
        self, base: CommittedListing, walked: disk.DiskWalk, paths: set[str]
    ) -> tuple[Listing, dict[str, str]]:
        overlay: dict[str, str | None] = {}
        texts: dict[str, str] = {}
        for path in sorted(paths):
            raw = disk.read_at(walked, path, attachment=path.startswith(ATTACHMENTS))
            if path.startswith(ATTACHMENTS):
                if (raw is not None) != (path in base.attachments):
                    overlay[path] = "present" if raw is not None else None
            else:
                key = None if raw is None else blob_id(raw)
                if key != base.blobs.get(path):
                    overlay[path] = key
                    if key is not None and raw is not None:
                        texts[key] = decode(raw)
        blobs, attachments = dict(base.blobs), set(base.attachments)
        for path, change in overlay.items():
            if path.startswith(ATTACHMENTS):
                attachments.discard(path) if change is None else attachments.add(path)
            elif change is None:
                blobs.pop(path, None)
            else:
                blobs[path] = change
        ident = base.ident
        if overlay:
            changes = "\n".join(f"{path}\0{key or ''}" for path, key in sorted(overlay.items()))
            ident = sha1(encode(f"{base.ident}\0{changes}")).hexdigest()
        return Listing(base.rev, ident, blobs, frozenset(attachments)), texts
