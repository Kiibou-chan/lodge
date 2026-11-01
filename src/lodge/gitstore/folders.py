"""Base-relative folder signatures for indexed checkout reads."""

import json
import os
import sqlite3
import stat
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field
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
            and self.ctime_ns <= self.listed_at_ns - 2_000_000_000
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


def _rows(db: sqlite3.Connection) -> dict[str, Row]:
    with transaction(db):
        raw = db.execute("SELECT * FROM folders").fetchall()
        count = db.execute("SELECT folder_count FROM meta").fetchone()[0]
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


def _base_folders(names: Mapping[str, str]) -> dict[str, dict[str, str]]:
    folders: dict[str, dict[str, str]] = {}
    for path, kind in names.items():
        parent, _, name = path.rpartition("/")
        folders.setdefault(parent, {})[name] = "file" if kind == "blob" else "other"
        while parent != "lodge" and parent:
            parent, _, name = parent.rpartition("/")
            folders.setdefault(parent, {})[name] = "folder"
    return folders


class Folders:
    def __init__(self, db: sqlite3.Connection) -> None:
        self.db = db

    def walk(self, root: Path, base: str, names: Callable[[], Mapping[str, str]]) -> disk.DiskWalk:
        try:
            rows = _rows(self.db)
        except Exception:
            return disk.walk(root)
        walked = FolderWalk({}, set(), set(), os.open(root, disk._FOLDER & ~os.O_NOFOLLOW))
        children: dict[str, list[str]] = {}
        for path in rows:
            children.setdefault(path.rpartition("/")[0], []).append(path)
        base_folders: dict[str, dict[str, str]] | None = None
        kept: dict[str, Row] = {}
        pending = ["lodge"]
        try:
            while pending:
                path = pending.pop()
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
                    listed = time_ns()
                    if entries is None:
                        # A folder may have become a link after its lstat.
                        held = disk.folder_stat(walked, path)
                        if held is not None and not stat.S_ISDIR(held.st_mode):
                            walked.names[path] = "link" if stat.S_ISLNK(held.st_mode) else "file"
                        else:
                            walked.unlistable.add(path)
                        continue
                    if base_folders is None:
                        base_folders = _base_folders(names())
                    before = base_folders.get(path, {})
                    added = {n: k for n, k in entries.items() if before.get(n) != k}
                    removed = {n: k for n, k in before.items() if entries.get(n) != k}
                    row = Row(
                        path,
                        held.st_ino,
                        held.st_mtime_ns,
                        held.st_ctime_ns,
                        listed,
                        base,
                        added,
                        removed,
                    )
                    pending.extend(f"{path}/{n}" for n, k in entries.items() if k == "folder")
                walked.folders.add(path)
                kept[path] = row
                walked.names.update(
                    (f"{path}/{n}", k) for n, k in row.added.items() if k != "folder"
                )
                walked.removed.update((f"{path}/{n}", k) for n, k in row.removed.items())
            walked.names.pop("lodge", None)
            if not walked.unlistable and (walked.listed or kept.keys() != rows.keys()):
                self._keep(kept)
            return walked
        except BaseException:
            walked.close()
            raise

    def _keep(self, rows: Mapping[str, Row]) -> None:
        try:
            with transaction(self.db, write=True):
                self.db.execute("DELETE FROM folders")
                for row in rows.values():
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
                        "INSERT INTO folders VALUES (?,?,?,?,?,?,?,?)", (*values, added, removed)
                    )
                self.db.execute("UPDATE meta SET folder_count=?", (len(rows),))
        except Exception:
            pass
