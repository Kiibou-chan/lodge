"""Checkout identity from a pinned committed base and a descriptor-read overlay."""

from hashlib import sha1
from pathlib import Path

from lodge.core import ATTACHMENTS, Listing, blob_id
from lodge.gitstore import disk, git
from lodge.gitstore.attributes import Conversions
from lodge.gitstore.committed import EMPTY_TREE, CommittedListing
from lodge.gitstore.committed import Committed as Committed
from lodge.gitstore.flags import Flags, scan
from lodge.gitstore.folders import Folders, FolderWalk
from lodge.gitstore.trees import decode, encode

_DIFF = ["-c", "core.fsmonitor=false", "-c", "core.checkStat=default", "-c", "core.trustctime=true"]


def candidates(
    identity: "CheckoutIdentity", rev: str | None, trunk: str | None
) -> tuple[Listing, dict[str, str]] | None:
    """Interim R11-A; R11-B switches only this body to identity.stat_current(rev, trunk)."""
    return None


class CheckoutIdentity:
    def __init__(self, root: Path, folders: Folders | None = None) -> None:
        self.root = root
        self.folders = folders
        self._pending: tuple[str | None, dict[str, str | None]] | None = None
        self.flags = Flags(root)
        self.conversions = Conversions(root, self.flags)
        self.committed = Committed(root)
        self.published: str | None = None

    def current(self, rev: str | None, trunk: str | None = None) -> tuple[Listing, dict[str, str]]:
        self._pending = None
        candidate = candidates(self, rev, trunk)
        if candidate is not None:
            return candidate
        merged = git.attempt(["merge-base", rev or EMPTY_TREE, trunk or EMPTY_TREE], self.root)
        self.published = decode(merged.stdout).strip() if merged.returncode == 0 else None
        self.committed.tree_id(self.published)
        base = self.committed.listing(rev)
        walked = self._walk(rev)
        try:
            return self._overlay(base, walked, {*base.blobs, *base.attachments, *walked.names})
        finally:
            walked.close()

    def stat_current(self, rev: str | None, trunk: str | None) -> tuple[Listing, dict[str, str]]:
        """R11-B's coherent git candidates, ready for the author's ruling."""
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
            flagged = scan(results[2].stdout)
            walked = self._walk(rev)
            try:

                def all_paths(walked: disk.DiskWalk = walked) -> set[str]:
                    base = self.committed.listing(rev)
                    return {*base.blobs, *base.attachments, *walked.names}

                changed = set(walked.names)
                if isinstance(walked, FolderWalk):
                    changed.update(walked.removed)
                else:
                    base = self.committed.listing(rev)
                    changed = {*base.blobs, *base.attachments} ^ set(walked.names)
                    changed.update(p for p, k in base.kinds.items() if k != "blob")
                if walked.unlistable:
                    changed.update(all_paths())
                changed.update(flagged.paths)
                changed.update(
                    self.conversions.paths(
                        all_paths,
                        flagged,
                        attributes={p for p in walked.names if p.endswith("/.gitattributes")},
                        config=(results[3], results[4]),
                    )
                )
                if results[2].returncode:
                    changed.update(all_paths())
                for done in results[:2]:
                    if done.returncode:
                        changed.update(all_paths())
                    changed.update(decode(p) for p in done.stdout.split(b"\0") if p)
                nonblobs = (
                    {p for p, k in walked.removed.items() if k == "other"}
                    if isinstance(walked, FolderWalk)
                    else set()
                )
                base = self.committed.selected(rev, changed, nonblobs)
                listing, texts = self._overlay(base, walked, changed, lazy=True)
            finally:
                walked.close()
            if before == self.flags.key():
                return listing, texts
            self.conversions.discard()
        merged = git.attempt(["merge-base", rev or EMPTY_TREE, trunk or EMPTY_TREE], self.root)
        self.published = decode(merged.stdout).strip() if merged.returncode == 0 else None
        self._pending = None
        exact = disk.tree(self.root)
        pieces = "\n".join(f"{p}\0{k}" for p, k in sorted(exact.blobs.items()))
        pieces += "\0" + "\0".join(sorted(exact.attachments))
        ident = sha1(encode(pieces)).hexdigest()
        return Listing(rev, ident, exact.blobs, exact.attachments), {
            exact.blobs[p]: t for p, t in exact.files.items()
        }

    def _overlay(
        self, base: CommittedListing, walked: disk.DiskWalk, paths: set[str], *, lazy: bool = False
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
        ident = base.ident
        if overlay:
            changes = "\n".join(f"{path}\0{key or ''}" for path, key in sorted(overlay.items()))
            ident = sha1(encode(f"{base.ident}\0{changes}")).hexdigest()
        listing = Listing(base.rev, ident, {}, frozenset())
        if lazy:
            self._pending = base.rev, overlay
        else:
            listing = self._apply(listing, base, overlay)
        return listing, texts

    def _walk(self, rev: str | None) -> disk.DiskWalk:
        if self.folders is None:
            return disk.walk(self.root)
        return self.folders.walk(
            self.root, self.committed.tree_id(rev), lambda: self.committed.listing(rev).kinds
        )

    def materialise(self, listing: Listing) -> Listing:
        if self._pending is None:
            return listing
        rev, overlay = self._pending
        return self._apply(listing, self.committed.listing(rev), overlay)

    @staticmethod
    def _apply(listing: Listing, base: Listing, overlay: dict[str, str | None]) -> Listing:
        blobs, attachments = dict(base.blobs), set(base.attachments)
        for path, change in overlay.items():
            if path.startswith(ATTACHMENTS):
                attachments.discard(path) if change is None else attachments.add(path)
            elif change is None:
                blobs.pop(path, None)
            else:
                blobs[path] = change
        return Listing(listing.rev, listing.ident, blobs, frozenset(attachments))
