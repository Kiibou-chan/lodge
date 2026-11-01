"""Checkout isolation, bounded git work, timestamp races, and incremental rows."""

import os
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from gitstore.repos import CHECKOUT, git, worktree, write
from gitstore.test_folders import cached as cached
from gitstore.test_folders import opened, seed
from gitstore.test_identity import RECORD, agrees
from lodge.gitstore import disk, folders
from lodge.gitstore import git as runner
from lodge.gitstore.committed import Committed
from lodge.gitstore.index_db import IndexDB
from lodge.gitstore.index_space import clear
from lodge.gitstore.index_transactions import transaction
from lodge.gitstore.listing import CheckoutListing


def test_folder_rows_are_scoped_to_each_checkout(cached: tuple[Path, IndexDB]) -> None:
    repo, index = seed(cached)
    other = worktree(repo, "other")
    agrees(opened(other, index))
    with patch.object(os, "scandir", side_effect=AssertionError("relisted another checkout")):
        for root in (repo, other, repo, other):
            opened(root, index).identities()
    roots = {r[0] for r in index.db.execute("SELECT DISTINCT root FROM folders")}
    assert roots == {git(p, "rev-parse", "--absolute-git-dir") for p in (repo, other)}
    counts = dict(index.db.execute("SELECT root,folder_count FROM folder_roots"))
    assert counts == {
        root: index.db.execute("SELECT count(*) FROM folders WHERE root=?", (root,)).fetchone()[0]
        for root in roots
    }


@pytest.mark.parametrize("tracked", [False, True])
def test_three_hundred_changes_use_constant_git_processes(
    cached: tuple[Path, IndexDB], tracked: bool
) -> None:
    repo, index = cached
    for n in range(300):
        write(repo, f"lodge/decisions/new-{n}.md", "Before.\n")
    if tracked:
        git(repo, "add", "--", "lodge")
        git(repo, "commit", "-m", "Synthetic batch base")
        for n in range(300):
            write(repo, f"lodge/decisions/new-{n}.md", "After.\n")
    seed(cached)
    with patch.object(runner, "attempt", wraps=runner.attempt) as calls:
        opened(repo, index).identities()
    # The seven run_many children are fixed; attempt covers every other process.
    assert calls.call_count <= 10, calls.call_count
    batches = [c for c in calls.call_args_list if c.args[0][:2] == ["cat-file", "--batch-check"]]
    assert len(batches) == int(tracked)
    if tracked:
        assert b"\0" not in batches[0].args[3]
        assert batches[0].args[3].count(b"\n") == 300
    agrees(opened(repo, index))


@pytest.mark.parametrize("quantum", [1_000_000_000, 2_000_000_000])
def test_reference_time_precedes_lstat_and_scan(cached: tuple[Path, IndexDB], quantum: int) -> None:
    repo, index = cached
    now = [10_900_000_000]
    original_stat, original_entries = disk.folder_stat, disk.folder_entries
    path = "lodge/decisions/late.md"
    created = False

    def rounded(walked: disk.DiskWalk, name: str) -> os.stat_result | None:
        held = original_stat(walked, name)
        if held is not None:
            held = Mock(
                spec=os.stat_result,
                st_ino=held.st_ino,
                st_mode=held.st_mode,
                st_ctime_ns=10_000_000_000 // quantum * quantum,
                st_mtime_ns=10_000_000_000 // quantum * quantum,
            )
        return held

    def racing(walked: disk.DiskWalk, name: str) -> dict[str, str] | None:
        nonlocal created
        entries = original_entries(walked, name)
        if name == "lodge/decisions" and not created:
            created = True
            write(repo, path, "Created inside the scan.\n")
            now[0] = 13_100_000_000
        return entries

    with (
        patch.object(disk, "folder_stat", rounded),
        patch.object(disk, "folder_entries", racing),
        patch.object(folders, "time_ns", lambda: now[0]),
    ):
        first = opened(repo, index)
        first.identities()
        assert created and path not in first.listings()[0].blobs
        now[0] = 16_000_000_000
        assert path in agrees(opened(repo, index)).blobs
        assert path in agrees(opened(repo, index)).blobs


def test_clear_preserves_folder_hits(cached: tuple[Path, IndexDB]) -> None:
    repo, index = seed(cached)
    with transaction(index.db, write=True):
        clear(index.db)
    with patch.object(os, "scandir", side_effect=AssertionError("clear lost folder rows")):
        opened(repo, index).identities()


def test_one_changed_folder_writes_and_lists_only_it(cached: tuple[Path, IndexDB]) -> None:
    repo, index = seed(cached)
    write(repo, "lodge/decisions/extra.md", "Extra.\n")
    statements: list[str] = []
    index.db.set_trace_callback(statements.append)
    try:
        with (
            patch.object(Committed, "listing", side_effect=AssertionError("full base map")),
            patch.object(runner, "attempt", wraps=runner.attempt) as calls,
        ):
            opened(repo, index).identities()
    finally:
        index.db.set_trace_callback(None)
    inserts = [s for s in statements if s.startswith("INSERT") and "folders " in s]
    assert len(inserts) == 1
    assert not any(s.startswith("DELETE FROM folders") for s in statements)
    listings = [c.args[0] for c in calls.call_args_list if c.args[0][0] == "ls-tree"]
    assert len(listings) == 1 and "-r" not in listings[0]
    assert any(str(p).endswith(":lodge/decisions") for p in listings[0])
    assert statements.count("BEGIN IMMEDIATE") == statements.count("COMMIT") - 1 == 1
    agrees(opened(repo, index))


def test_vanished_rows_are_deleted_without_rewriting_others(cached: tuple[Path, IndexDB]) -> None:
    repo, index = cached
    write(repo, "lodge/decisions/temporary/extra.md", "Temporary.\n")
    seed(cached)
    (repo / "lodge/decisions/temporary/extra.md").unlink()
    (repo / "lodge/decisions/temporary").rmdir()
    statements: list[str] = []
    index.db.set_trace_callback(statements.append)
    agrees(opened(repo, index))
    index.db.set_trace_callback(None)
    deletes = [s for s in statements if s.startswith("DELETE FROM folders")]
    assert len(deletes) == 1 and "path='lodge/decisions/temporary'" in deletes[0]
    inserts = [s for s in statements if s.startswith("INSERT") and "folders " in s]
    assert len(inserts) == 1


def test_failed_refresh_cannot_materialise_an_empty_lazy_listing(
    cached: tuple[Path, IndexDB],
) -> None:
    repo, index = seed(cached)
    source = CheckoutListing(repo, CHECKOUT, lambda _: True, folders.Folders(index.db))
    source.identities()
    with (
        patch.object(runner, "run_many", side_effect=RuntimeError("refresh failed")),
        pytest.raises(RuntimeError, match="refresh failed"),
    ):
        source.identities()
    with pytest.raises(RuntimeError, match="lazy listing"):
        source.listings()
    assert RECORD in source.identity.committed.listing(git(repo, "rev-parse", "HEAD")).blobs


def test_invalid_extra_row_is_removed_when_snapshot_heals(cached: tuple[Path, IndexDB]) -> None:
    repo, index = seed(cached)
    root = git(repo, "rev-parse", "--absolute-git-dir")
    index.db.execute(
        "INSERT INTO folders VALUES (?,?,0,0,0,0,'base','{}','{}')", (root, "../invalid")
    )
    agrees(opened(repo, index))
    with patch.object(os, "scandir", side_effect=AssertionError("invalid row never healed")):
        opened(repo, index).identities()
