"""Descriptor-relative disk traversal and reads, without following links."""

import errno
import os
import stat
from dataclasses import dataclass, field
from pathlib import Path

from lodge.core import ATTACHMENTS, Tree, blob_id
from lodge.gitstore.trees import decode

_FOLDER = os.O_RDONLY | os.O_NOFOLLOW | os.O_DIRECTORY | os.O_CLOEXEC
_FILE = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC


def open_root(root: Path) -> int:
    """Open the checkout root for descriptor-relative traversal."""
    return os.open(root, _FOLDER & ~os.O_NOFOLLOW)


@dataclass
class DiskWalk:
    names: dict[str, str]
    folders: set[str]
    unlistable: set[str]
    _root_fd: int
    _stack: list[tuple[str, int]] = field(default_factory=list)

    def close(self) -> None:
        for _, fd in self._stack:
            os.close(fd)
        self._stack.clear()
        if self._root_fd >= 0:
            os.close(self._root_fd)
            self._root_fd = -1

    def parent(self, path: str) -> int | None:
        """Reuse up to 64 descriptors along the current path, reopening only on a miss."""
        parent = path.rpartition("/")[0]
        if self._root_fd < 0:
            return None
        if not parent:
            return self._root_fd
        if parent not in self.folders:
            return None
        # Retain the deepest open ancestor; siblings pop only the departed suffix.
        while self._stack and not (
            parent == self._stack[-1][0] or parent.startswith(self._stack[-1][0] + "/")
        ):
            os.close(self._stack.pop()[1])
        current, fd = self._stack[-1] if self._stack else ("", self._root_fd)
        suffix = parent[len(current) :].lstrip("/")
        try:
            for part in suffix.split("/") if suffix else ():
                current = f"{current}/{part}" if current else part
                if current not in self.folders:
                    return None
                fd = os.open(part, _FOLDER, dir_fd=fd)
                self._stack.append((current, fd))
                if len(self._stack) > 64:
                    os.close(self._stack.pop(0)[1])
            return fd
        except OSError:
            return None


def folder_stat(walked: DiskWalk, path: str) -> os.stat_result | None:
    """Take a descriptor-relative lstat, with no traversal through links."""
    parent = walked.parent(path)
    if parent is None:
        return None
    try:
        return os.stat(path.rpartition("/")[2], dir_fd=parent, follow_symlinks=False)
    except OSError:
        return None


def folder_entries(walked: DiskWalk, path: str) -> dict[str, str] | None:
    """List one real folder through its parent's descriptor."""
    parent = walked.parent(path)
    if parent is None:
        return None
    fd = -1
    try:
        fd = os.open(path.rpartition("/")[2], _FOLDER, dir_fd=parent)
        with os.scandir(fd) as entries:
            return {
                e.name: "folder"
                if e.is_dir(follow_symlinks=False)
                else "link"
                if e.is_symlink()
                else "file"
                for e in entries
            }
    except OSError:
        return None
    finally:
        if fd >= 0:
            os.close(fd)


def walk(root: Path) -> DiskWalk:
    """List real folders with an explicit stack and at most 66 descriptors."""
    walked = DiskWalk({}, set(), set(), open_root(root))
    pending = ["lodge"]
    try:
        while pending:
            path = pending.pop()
            parent = walked.parent(path)
            if parent is None:
                walked.unlistable.add(path)
                continue
            name = path.rpartition("/")[2]
            try:
                fd = os.open(name, _FOLDER, dir_fd=parent)
            except OSError as error:
                if error.errno in (errno.ENOTDIR, errno.ELOOP):
                    walked.names[path] = "link" if _link(parent, name) else "file"
                else:
                    walked.unlistable.add(path)
                continue
            try:
                with os.scandir(fd) as entries:
                    names = [
                        (e.name, e.is_dir(follow_symlinks=False), e.is_symlink()) for e in entries
                    ]
                walked.folders.add(path)
                for child, folder, link in names:
                    child_path = f"{path}/{child}"
                    if folder:
                        pending.append(child_path)
                    else:
                        walked.names[child_path] = "link" if link else "file"
            except OSError:
                walked.unlistable.add(path)
            finally:
                os.close(fd)
        walked.names.pop("lodge", None)
        return walked
    except BaseException:
        walked.close()
        raise


def _link(parent: int, name: str) -> bool:
    try:
        return stat.S_ISLNK(os.stat(name, dir_fd=parent, follow_symlinks=False).st_mode)
    except OSError:
        return False


def read_at(walked: DiskWalk, path: str, *, attachment: bool = False) -> bytes | None:
    """Read only through reached real folders, using the opened file's own type."""
    parent = walked.parent(path)
    if parent is None:
        return None
    name = path.rpartition("/")[2]
    try:
        fd = os.open(name, _FILE, dir_fd=parent)
    except OSError as error:
        if error.errno == errno.ELOOP:
            try:
                return b"" if attachment else os.fsencode(os.readlink(name, dir_fd=parent))
            except OSError:
                return b""
        if error.errno in (errno.ENOENT, errno.ENOTDIR):
            return None
        try:
            if stat.S_ISDIR(os.stat(name, dir_fd=parent, follow_symlinks=False).st_mode):
                return None
        except OSError:
            pass
        # Sockets and unreadable files have disk_tree's empty-text representation.
        return b""
    try:
        mode = os.fstat(fd).st_mode
        if stat.S_ISDIR(mode):
            return None
        if attachment or not stat.S_ISREG(mode):
            return b""
        with os.fdopen(fd, "rb", closefd=False) as stream:
            return stream.read()
    except OSError:
        return b""
    finally:
        os.close(fd)


def tree(root: Path) -> Tree:
    """The exact tree used by the gate and add, with attachments counted by presence."""
    walked = walk(root)
    files, blobs, attachments = {}, {}, set()
    try:
        for path in walked.names:
            attachment = path.startswith(ATTACHMENTS)
            raw = read_at(walked, path, attachment=attachment)
            if raw is None:
                continue
            if attachment:
                attachments.add(path)
            else:
                files[path], blobs[path] = decode(raw), blob_id(raw)
        return Tree(None, files, frozenset(attachments), blobs)
    finally:
        walked.close()
