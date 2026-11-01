"""Checkout identity from a committed base and an overlay hashed from disk."""

import os
import stat
from hashlib import sha1
from pathlib import Path

from lodge.core import ATTACHMENTS, Listing, blob_id
from lodge.gitstore import git
from lodge.gitstore.attributes import Conversions
from lodge.gitstore.flags import Flags
from lodge.gitstore.trees import decode, encode

EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
_DIFF = ["-c", "core.fsmonitor=false", "-c", "core.checkStat=default", "-c", "core.trustctime=true"]


class CheckoutIdentity:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.flags = Flags(root)
        self.conversions = Conversions(root, self.flags)
        self._base: Listing | None = None

    def current(self, rev: str | None) -> tuple[Listing, dict[str, str]]:
        if self._base is None or self._base.rev != rev:
            self._base = committed(self.root, rev)
        base = self._base
        base_paths = {*base.blobs, *base.attachments}
        disk_paths = names(self.root)
        flagged = self.flags.read()
        overlay_paths = disk_paths - base_paths
        overlay_paths.update(flagged.paths)
        overlay_paths.update(self.conversions.paths(base_paths | disk_paths, flagged))
        if rev is not None:
            for command in (["diff-index", "--cached"], ["diff-files"]):
                changed = git.run_bytes(
                    [
                        *_DIFF,
                        *command,
                        "--no-renames",
                        "-z",
                        "--name-only",
                        *([rev] if command[0] == "diff-index" else []),
                        "--",
                        "lodge",
                    ],
                    self.root,
                )
                overlay_paths.update(decode(p) for p in changed.split(b"\0") if p)
        overlay: dict[str, str | None] = {}
        texts: dict[str, str] = {}
        for path in sorted(overlay_paths):
            raw = read_disk(self.root / path, attachment=path.startswith(ATTACHMENTS))
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
        return Listing(rev, ident, blobs, frozenset(attachments)), texts


def committed(root: Path, rev: str | None) -> Listing:
    if rev is None:
        return Listing(None, EMPTY_TREE, {}, frozenset())
    done = git.attempt(["rev-parse", "--verify", f"{rev}:lodge"], root)
    if done.returncode != 0:
        return Listing(rev, EMPTY_TREE, {}, frozenset())
    ident = decode(done.stdout).strip()
    raw = git.run_bytes(["ls-tree", "-r", "-z", "--full-tree", rev, "--", "lodge"], root)
    blobs, attachments = {}, set()
    for item in raw.split(b"\0"):
        meta, _, raw_path = item.partition(b"\t")
        fields = meta.split(b" ")
        if len(fields) != 3:
            continue
        path = decode(raw_path)
        if path == "lodge":
            ident = EMPTY_TREE  # A file or gitlink at the root supplies no lodge/ tree.
            continue
        if path.startswith(ATTACHMENTS):
            attachments.add(path)
        else:
            blobs[path] = fields[2].decode()
    return Listing(rev, ident, blobs, frozenset(attachments))


def names(root: Path) -> set[str]:
    """Names only, with real folders traversed and links kept as files."""
    found: set[str] = set()
    folders = [(str(root / "lodge"), "lodge")]
    while folders:
        folder, prefix = folders.pop()
        try:
            with os.scandir(folder) as entries:
                for entry in entries:
                    if entry.is_dir(follow_symlinks=False):
                        folders.append((entry.path, f"{prefix}/{entry.name}"))
                    else:
                        found.add(f"{prefix}/{entry.name}")
        except OSError:
            continue
    return found


def read_disk(path: Path, *, attachment: bool = False) -> bytes | None:
    """The exact disk-tree representation; a real folder or absent path is deleted."""
    try:
        mode = os.lstat(path).st_mode
    except OSError:
        return None
    if stat.S_ISDIR(mode):
        return None
    if attachment:
        return b""  # Attachments count by presence; never open their contents.
    try:
        if stat.S_ISLNK(mode):
            return os.fsencode(os.readlink(path))
        return path.read_bytes() if stat.S_ISREG(mode) else b""
    except OSError:
        return b""
