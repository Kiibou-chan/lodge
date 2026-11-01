"""Base-relative folder signatures for indexed checkout reads.

Hits assume directory mutations update inode, mtime, or ctime, a local wall clock
comparable with the file system's, and no directory attribute caching. The three
second margin exceeds two-second timestamp rounding and a coarse kernel clock
lagging by up to a tick, with its reference
taken before lstat. Network file systems such as NFS and SMB can violate these
assumptions through server clock skew or attribute caching; inode reuse across
mounts is also outside the key, which has no device number. FUSE, NFS, and SMB
need separate validation of these assumptions before relying on cache hits.
"""

import json
import os
import sqlite3
import stat
from collections.abc import Callable, Collection, Mapping
from dataclasses import dataclass, field, replace
from pathlib import Path
from time import time_ns

from lodge.gitstore import disk
from lodge.gitstore.index_transactions import transaction


@dataclass
class FolderWalk(disk.DiskWalk):
    removed: dict[str, str] = field(default_factory=dict)
    listed: bool = False


@dataclass(frozen=True)
class Row:
    path: str
    ino: int
    mtime_ns: int
    ctime_ns: int
    listed_at_ns: int
    base: str
    added: dict[str, str]
    removed: dict[str, str]

    def matches(self, held: os.stat_result, base: str) -> bool:
        return (
            (self.ino, self.mtime_ns, self.ctime_ns)
            == (held.st_ino, held.st_mtime_ns, held.st_ctime_ns)
            and self.base == base
            and self.ctime_ns <= self.listed_at_ns - 3_000_000_000
        )


def _name(value: object) -> bool:
    return (
        isinstance(value, str)
        and bool(value)
        and value not in {".", ".."}
        and "/" not in value
        and "\0" not in value
    )


def _delta(raw: object) -> dict[str, str]:
    if not isinstance(raw, str):
        raise ValueError("invalid folder delta")
    value = json.loads(raw)
    if not isinstance(value, dict) or not all(
        _name(k) and isinstance(v, str) and v in {"file", "link", "folder", "other"}
        for k, v in value.items()
    ):
        raise ValueError("invalid folder entry")
    return value


def _rows(db: sqlite3.Connection, root: str) -> dict[str, Row]:
    with transaction(db):
        raw = db.execute(
            "SELECT path,ino,mtime_ns,ctime_ns,listed_at_ns,base,added,removed "
            "FROM folders WHERE root=?",
            (root,),
        ).fetchall()
        held = db.execute("SELECT folder_count FROM folder_roots WHERE root=?", (root,)).fetchone()
        count = held[0] if held is not None else -1
    if len(raw) != count:
        return {}
    rows = {}
    try:
        for path, ino, mtime, ctime, listed, base, added, removed in raw:
            if (
                not isinstance(path, str)
                or path.split("/")[0] != "lodge"
                or not all(_name(p) for p in path.split("/"))
                or not all(isinstance(n, int) for n in (ino, mtime, ctime, listed))
                or not isinstance(base, str)
            ):
                return {}
            rows[path] = Row(path, ino, mtime, ctime, listed, base, _delta(added), _delta(removed))
    except (ValueError, TypeError):
        return {}
    # Rows can only be reached through their real parent folders.
    if any(p != "lodge" and p.rpartition("/")[0] not in rows for p in rows):
        return {}
    return rows


class Folders:
    def __init__(self, db: sqlite3.Connection) -> None:
        self.db = db

    def walk(
        self,
        root: Path,
        base: str,
        names: Callable[[Collection[str]], Mapping[str, Mapping[str, str]]],
        *,
        checkout: str,
    ) -> disk.DiskWalk:
        try:
            rows = _rows(self.db, checkout)
        except Exception:
            return disk.walk(root)
        walked = FolderWalk({}, set(), set(), disk.open_root(root))
        children: dict[str, list[str]] = {}
        for path in rows:
            children.setdefault(path.rpartition("/")[0], []).append(path)
        kept: dict[str, Row] = {}
        relisted: dict[str, dict[str, str]] = {}
        pending = ["lodge"]
        try:
            while pending:
                path = pending.pop()
                listed = time_ns()
                held = disk.folder_stat(walked, path)
                if held is None:
                    walked.unlistable.add(path)
                    continue
                if not stat.S_ISDIR(held.st_mode):
                    walked.names[path] = "link" if stat.S_ISLNK(held.st_mode) else "file"
                    continue
                row = rows.get(path)
                if row is not None and row.matches(held, base):
                    pending.extend(children.get(path, ()))
                else:
                    walked.listed = True
                    entries = disk.folder_entries(walked, path)
                    if entries is None:
                        # A folder may have become a link after its lstat.
                        held = disk.folder_stat(walked, path)
                        if held is not None and not stat.S_ISDIR(held.st_mode):
                            walked.names[path] = "link" if stat.S_ISLNK(held.st_mode) else "file"
                        else:
                            walked.unlistable.add(path)
                        continue
                    relisted[path] = entries
                    row = Row(
                        path,
                        held.st_ino,
                        held.st_mtime_ns,
                        held.st_ctime_ns,
                        listed,
                        base,
                        {},
                        {},
                    )
                    pending.extend(f"{path}/{n}" for n, k in entries.items() if k == "folder")
                walked.folders.add(path)
                kept[path] = row
            bases = names(relisted) if relisted else {}
            for path, row in kept.items():
                if path in relisted:
                    entries, before = relisted[path], bases[path]
                    row = replace(
                        row,
                        added={n: k for n, k in entries.items() if before.get(n) != k},
                        removed={n: k for n, k in before.items() if entries.get(n) != k},
                    )
                    kept[path] = row
                walked.names.update(
                    (f"{path}/{n}", k) for n, k in row.added.items() if k != "folder"
                )
                walked.removed.update((f"{path}/{n}", k) for n, k in row.removed.items())
            walked.names.pop("lodge", None)
            if not walked.unlistable and (walked.listed or kept.keys() != rows.keys()):
                self._keep(checkout, kept)
            return walked
        except BaseException:
            walked.close()
            raise

    def _keep(self, root: str, rows: Mapping[str, Row]) -> None:
        try:
            with transaction(self.db, write=True):
                # Compare inside the write lock: another reader may have relisted meanwhile.
                earlier = _rows(self.db, root)
                paths = {
                    p[0] for p in self.db.execute("SELECT path FROM folders WHERE root=?", (root,))
                }
                for path in paths - rows.keys():
                    self.db.execute("DELETE FROM folders WHERE root=? AND path=?", (root, path))
                for row in rows.values():
                    if row == earlier.get(row.path):
                        continue
                    values = (
                        row.path,
                        row.ino,
                        row.mtime_ns,
                        row.ctime_ns,
                        row.listed_at_ns,
                        row.base,
                    )
                    added, removed = (
                        json.dumps(delta, ensure_ascii=True, separators=(",", ":"))
                        for delta in (row.added, row.removed)
                    )
                    self.db.execute(
                        "INSERT OR REPLACE INTO folders VALUES (?,?,?,?,?,?,?,?,?)",
                        (root, *values, added, removed),
                    )
                self.db.execute(
                    "INSERT OR REPLACE INTO folder_roots VALUES (?,?)", (root, len(rows))
                )
        except Exception:
            pass
