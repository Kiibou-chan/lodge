"""Folder deltas preserve exact reads across edits and cache failures."""

import errno
import os
import shutil
import sqlite3
import time
from collections.abc import Iterator
from pathlib import Path
from unittest.mock import patch

import pytest

from gitstore.identity_rules import r11b
from gitstore.repos import CHECKOUT, Ticker, git, write
from gitstore.test_identity import ATTACHMENT, RECORD, agrees, prepared
from gitstore.test_index_failures import Interrupted as SQLInterrupted
from lodge.app import Store
from lodge.gitstore import disk, folders, open_index, open_store
from lodge.gitstore import git as runner
from lodge.gitstore.identity import CheckoutIdentity, Committed
from lodge.gitstore.index_db import IndexDB


@pytest.fixture(
    params=["a", pytest.param("b", marks=pytest.mark.skip(reason="awaits the author's STALE-1"))]
)
def mode(request: pytest.FixtureRequest) -> str:
    return str(request.param)


@pytest.fixture
def cached(tmp_path: Path, mode: str) -> Iterator[tuple[Path, IndexDB]]:
    repo, _ = prepared(tmp_path)
    index = open_index(repo / ".git")
    assert isinstance(index, IndexDB)
    with patch.object(folders, "time_ns", lambda: time.time_ns() + 3_000_000_000, create=True):
        if mode == "b":
            with r11b():
                yield repo, index
        else:
            yield repo, index
    index.close()


def opened(repo: Path, index: IndexDB) -> Store:
    return open_store(repo, CHECKOUT, Ticker(), index=index)


def seed(cached: tuple[Path, IndexDB]) -> tuple[Path, IndexDB]:
    repo, index = cached
    agrees(opened(repo, index))
    assert index.db.execute("SELECT count(*) FROM folders").fetchone()[0] > 0
    return repo, index


def test_unchanged_folders_are_not_listed(cached: tuple[Path, IndexDB]) -> None:
    repo, index = seed(cached)
    with patch.object(os, "scandir", side_effect=AssertionError("listed unchanged folder")):
        opened(repo, index).identities()
    agrees(opened(repo, index))


def test_seen_identity_takes_no_base_names(cached: tuple[Path, IndexDB], mode: str) -> None:
    repo, index = seed(cached)
    with patch.object(Committed, "listing", wraps=None, side_effect=AssertionError("base names")):
        if mode == "a":
            with pytest.raises(AssertionError, match="base names"):
                opened(repo, index).identities()
        else:
            with patch.object(runner, "run_bytes", wraps=runner.run_bytes) as calls:
                opened(repo, index).identities()
            assert not any(c.args[0][0] == "ls-tree" for c in calls.call_args_list)
    agrees(opened(repo, index))


def test_new_file_in_a_listed_folder(cached: tuple[Path, IndexDB]) -> None:
    repo, index = seed(cached)
    write(repo, "lodge/decisions/new.md", "New berth.\n")
    assert "lodge/decisions/new.md" in agrees(opened(repo, index)).blobs


def test_new_subfolder_with_a_file(cached: tuple[Path, IndexDB]) -> None:
    repo, index = seed(cached)
    write(repo, "lodge/decisions/new/record.md", "Nested berth.\n")
    assert "lodge/decisions/new/record.md" in agrees(opened(repo, index)).blobs


def test_deleted_untracked_file(cached: tuple[Path, IndexDB]) -> None:
    repo, index = cached
    path = "lodge/decisions/untracked.md"
    write(repo, path, "Temporary berth.\n")
    seed(cached)
    (repo / path).unlink()
    assert path not in agrees(opened(repo, index)).blobs


def test_rename_within_a_folder(cached: tuple[Path, IndexDB]) -> None:
    repo, index = seed(cached)
    (repo / RECORD).rename(repo / "lodge/decisions/renamed.md")
    listing = agrees(opened(repo, index))
    assert RECORD not in listing.blobs and "lodge/decisions/renamed.md" in listing.blobs


def test_deleted_attachment_is_absent(cached: tuple[Path, IndexDB], mode: str) -> None:
    repo, index = cached
    (repo / ATTACHMENT).unlink()
    seed(cached)
    if mode == "b":
        with patch.object(Committed, "listing", side_effect=AssertionError("base names")):
            opened(repo, index).identities()
    assert ATTACHMENT not in agrees(opened(repo, index)).attachments


@pytest.mark.parametrize("kind", ["copy", "other", "attachments"])
def test_folder_replaced_by_link_drops_its_rows(
    cached: tuple[Path, IndexDB], tmp_path: Path, kind: str
) -> None:
    repo, index = seed(cached)
    folder = "lodge/attachments" if kind == "attachments" else "lodge/decisions"
    target = tmp_path / "outside"
    shutil.copytree(repo / folder, target)
    if kind == "other":
        (target / "old.md").write_text("Outside bytes.\n")
    shutil.rmtree(repo / folder)
    (repo / folder).symlink_to(target, target_is_directory=True)
    listing = agrees(opened(repo, index))
    assert not any(p.startswith(folder + "/") for p in (*listing.blobs, *listing.attachments))
    assert (
        index.db.execute(
            "SELECT path FROM folders WHERE path=? OR path LIKE ?", (folder, folder + "/%")
        ).fetchall()
        == []
    )
    agrees(opened(repo, index))


def test_change_in_the_same_second_as_the_listing(cached: tuple[Path, IndexDB]) -> None:
    repo, index = seed(cached)
    index.db.execute("UPDATE folders SET listed_at_ns=ctime_ns+1")
    with patch.object(os, "scandir", wraps=os.scandir) as calls:
        opened(repo, index).identities()
    assert calls.call_count > 0
    write(repo, "lodge/decisions/racy.md", "Racy berth.\n")
    assert "lodge/decisions/racy.md" in agrees(opened(repo, index)).blobs


def test_mtime_set_back_still_detected(cached: tuple[Path, IndexDB]) -> None:
    repo, index = seed(cached)
    folder = repo / "lodge/decisions"
    before = folder.stat()
    write(repo, "lodge/decisions/backdated.md", "Backdated berth.\n")
    os.utime(folder, ns=(before.st_atime_ns, before.st_mtime_ns))
    assert "lodge/decisions/backdated.md" in agrees(opened(repo, index)).blobs


def test_base_change_relists(cached: tuple[Path, IndexDB]) -> None:
    repo, index = seed(cached)
    count = index.db.execute("SELECT count(*) FROM folders").fetchone()[0]
    write(repo, "lodge/decisions/committed.md", "Committed berth.\n")
    git(repo, "add", "--", "lodge")
    git(repo, "commit", "-m", "Change synthetic base")
    with patch.object(os, "scandir", wraps=os.scandir) as calls:
        opened(repo, index).identities()
    assert calls.call_count == count
    agrees(opened(repo, index))


def test_read_only_index_falls_back_to_the_walk(cached: tuple[Path, IndexDB]) -> None:
    repo, index = seed(cached)
    path = index.db.execute("PRAGMA database_list").fetchone()[2]
    db = sqlite3.connect(Path(path).as_uri() + "?mode=ro", uri=True, isolation_level=None)
    readonly = IndexDB(db, None)
    try:
        with patch.object(os, "scandir", side_effect=AssertionError("read-only hit listed")):
            opened(repo, readonly).identities()
        db.execute("PRAGMA query_only=ON")
        write(repo, "lodge/decisions/readonly.md", "Read-only berth.\n")
        assert "lodge/decisions/readonly.md" in agrees(opened(repo, readonly)).blobs
        db.close()
        with patch.object(disk, "walk", wraps=disk.walk) as walk:
            agrees(opened(repo, readonly))
        assert walk.called
    finally:
        readonly.close()


@pytest.mark.parametrize(
    "damage", ["missing", "undecodable", "bad_kind", "traversal", "deep_json", "missing_meta"]
)
def test_damaged_folder_row_is_a_miss(cached: tuple[Path, IndexDB], damage: str) -> None:
    repo, index = cached
    write(repo, "lodge/decisions/sub/untracked.md", "Untracked descendant.\n")
    seed(cached)
    if damage == "missing":
        index.db.execute("DELETE FROM folders WHERE path='lodge/decisions/sub'")
    elif damage == "missing_meta":
        index.db.execute("DELETE FROM meta")
    else:
        value = {
            "undecodable": "?",
            "bad_kind": '{"x":"unknown"}',
            "traversal": '{"../x":"file"}',
            "deep_json": "[" * 20000 + "]" * 20000,
        }[damage]
        index.db.execute("UPDATE folders SET added=? WHERE path='lodge/decisions/sub'", (value,))
    assert "lodge/decisions/sub/untracked.md" in agrees(opened(repo, index)).blobs


def test_interrupted_folder_write_lists_again(cached: tuple[Path, IndexDB]) -> None:
    repo, index = seed(cached)
    write(repo, "lodge/decisions/interrupted.md", "Interrupted berth.\n")
    from_snapshot = index.db.execute("SELECT * FROM folders").fetchall()
    count = index.db.execute("SELECT folder_count FROM meta").fetchone()[0]
    statements: list[str] = []
    index.db.set_trace_callback(statements.append)
    agrees(opened(repo, index))
    index.db.set_trace_callback(None)
    start = statements.index("BEGIN IMMEDIATE")
    end = statements.index("COMMIT", start)
    total = end - start + 1
    path = index.db.execute("PRAGMA database_list").fetchone()[2]
    for stop in range(1, total + 1):
        index.db.execute("DELETE FROM folders")
        index.db.executemany("INSERT INTO folders VALUES (?,?,?,?,?,?,?,?)", from_snapshot)
        index.db.execute("UPDATE meta SET folder_count=?", (count,))
        db = sqlite3.connect(path, isolation_level=None, factory=Interrupted)
        failed = IndexDB(db, None)
        db.after = stop
        agrees(opened(repo, failed))
        assert not db.in_transaction and db.count >= stop
        assert index.db.execute("SELECT * FROM folders").fetchall() == from_snapshot
        failed.close()
        agrees(opened(repo, index))


class Interrupted(SQLInterrupted):
    writing = False

    def execute(self, sql: str, parameters: object = (), /) -> sqlite3.Cursor:
        if sql == "BEGIN IMMEDIATE":
            self.writing = True
        if self.writing:
            return super().execute(sql, parameters)
        return sqlite3.Connection.execute(self, sql, parameters)  # type: ignore[arg-type]


@pytest.mark.parametrize("content", ["absent", "empty", "populated"])
@pytest.mark.parametrize("usable", [True, False])
def test_cached_gitlink_with_missing_object(
    cached: tuple[Path, IndexDB], content: str, usable: bool
) -> None:
    repo, index = cached
    path = "lodge/decisions/submodule"
    git(repo, "update-index", "--add", "--cacheinfo", f"160000,{'1' * 40},{path}")
    git(repo, "commit", "-m", "Synthetic unavailable gitlink")
    git(repo, "config", "diff.ignoreSubmodules", "all")
    if content != "absent":
        (repo / path).mkdir()
    if content == "populated":
        write(repo, f"{path}/child.md", "Submodule child.\n")
    seed(cached)
    if not usable:
        index.db.close()
    assert path not in agrees(opened(repo, index)).blobs


def test_unencodable_folder_path_is_a_cache_miss(cached: tuple[Path, IndexDB]) -> None:
    repo, index = seed(cached)
    path = "lodge/decisions/\udcff/new.md"
    try:
        write(repo, path, "Byte-named folder.\n")
    except OSError as error:
        if error.errno != errno.EILSEQ:
            raise
        pytest.skip("filesystem rejects non-UTF-8 names")
    assert path in agrees(opened(repo, index)).blobs
    assert not index.db.in_transaction


@pytest.mark.skip(reason="awaits the author's STALE-1")
def test_index_race_after_overlay_keeps_exact_fallback(cached: tuple[Path, IndexDB]) -> None:
    repo, index = seed(cached)
    original = CheckoutIdentity._overlay
    count = 0

    def changed(self: CheckoutIdentity, *args: object, **kwargs: object) -> object:
        nonlocal count
        value = original(self, *args, **kwargs)  # type: ignore[arg-type]
        count += 1
        write(repo, RECORD, f"Later bytes {count}.\n")
        os.utime(repo / ".git/index", ns=(count, count))
        return value

    with r11b(), patch.object(CheckoutIdentity, "_overlay", changed):
        agrees(opened(repo, index))
    assert count == 3
