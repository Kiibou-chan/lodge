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


@dataclass
class DiskWalk:
    root: Path
    names: dict[str, str]
    folders: set[str]
    unlistable: set[str]
    _root_fd: int
    _parent: str = ""
    _held: list[int] = field(default_factory=list)

    def close(self) -> None:
        for fd in reversed(self._held):
            os.close(fd)
        self._held.clear()
        if self._root_fd >= 0:
            os.close(self._root_fd)
            self._root_fd = -1

    def parent(self, path: str) -> int | None:
        """Keep only the most recently read ancestor chain, bounding descriptors by depth."""
        parent = path.rpartition("/")[0]
        if parent not in self.folders or self._root_fd < 0:
            return None
        if self._parent == parent and self._held:
            return self._held[-1]
        for fd in reversed(self._held):
            os.close(fd)
        self._held.clear()
        self._parent = ""
        current, fd = "", self._root_fd
        try:
            for part in parent.split("/"):
                current = f"{current}/{part}" if current else part
                if current not in self.folders:
                    return None
                fd = os.open(part, _FOLDER, dir_fd=fd)
                self._held.append(fd)
        except OSError:
            return None
        self._parent = parent
        return fd


def walk(root: Path) -> DiskWalk:
    """Names and kinds, the real folders reached, and folders that could not be listed."""
    walked = DiskWalk(root, {}, set(), set(), os.open(root, _FOLDER))

    def visit(parent: int, name: str, path: str) -> None:
        try:
            fd = os.open(name, _FOLDER, dir_fd=parent)
        except OSError as error:
            if error.errno in (errno.ENOTDIR, errno.ELOOP):
                walked.names[path] = "link" if _link(parent, name) else "file"
            else:
                walked.unlistable.add(path)
            return
        try:
            try:
                with os.scandir(fd) as entries:
                    names = [
                        (entry.name, entry.is_dir(follow_symlinks=False), entry.is_symlink())
                        for entry in entries
                    ]
            except OSError:
                walked.unlistable.add(path)
                return
            walked.folders.add(path)
            for child, folder, link in names:
                child_path = f"{path}/{child}"
                if folder:
                    visit(fd, child, child_path)
                else:
                    walked.names[child_path] = "link" if link else "file"
        finally:
            os.close(fd)

    try:
        visit(walked._root_fd, "lodge", "lodge")
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
