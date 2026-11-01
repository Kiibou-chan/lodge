"""Descriptor-relative disk traversal and reads, without following links."""

import errno
import os
import stat
from dataclasses import dataclass
from pathlib import Path

from lodge.core import ATTACHMENTS, Tree, blob_id
from lodge.gitstore.trees import decode

_FOLDER = os.O_RDONLY | os.O_NOFOLLOW | os.O_DIRECTORY | os.O_CLOEXEC
_FILE = os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK | os.O_CLOEXEC


@dataclass
class DiskWalk:
    names: dict[str, str]
    folders: set[str]
    unlistable: set[str]
    _root_fd: int
    _parent: str = ""
    _parent_fd: int = -1

    def close(self) -> None:
        if self._parent_fd >= 0:
            os.close(self._parent_fd)
            self._parent_fd = -1
        if self._root_fd >= 0:
            os.close(self._root_fd)
            self._root_fd = -1

    def parent(self, path: str) -> int | None:
        """Reopen ancestors with two transient descriptors, caching only the last parent."""
        parent = path.rpartition("/")[0]
        if self._root_fd < 0:
            return None
        if not parent:
            return self._root_fd
        if parent not in self.folders:
            return None
        if self._parent == parent and self._parent_fd >= 0:
            return self._parent_fd
        if self._parent_fd >= 0:
            os.close(self._parent_fd)
            self._parent_fd = -1
        current, fd = "", os.dup(self._root_fd)
        try:
            for part in parent.split("/"):
                current = f"{current}/{part}" if current else part
                if current not in self.folders:
                    return None
                child = os.open(part, _FOLDER, dir_fd=fd)
                os.close(fd)
                fd = child
            self._parent, self._parent_fd = parent, fd
            fd = -1
            return self._parent_fd
        except OSError:
            return None
        finally:
            if fd >= 0:
                os.close(fd)


def walk(root: Path) -> DiskWalk:
    """List real folders with an explicit stack and a constant descriptor bound."""
    walked = DiskWalk({}, set(), set(), os.open(root, _FOLDER & ~os.O_NOFOLLOW))
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
