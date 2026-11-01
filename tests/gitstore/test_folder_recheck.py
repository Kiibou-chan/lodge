"""Process bounds and coarse-clock regressions from the folder recheck."""

import shutil
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from gitstore.repos import git, worktree, write
from gitstore.test_folders import cached as cached
from gitstore.test_folders import opened, seed
from gitstore.test_identity import agrees
from lodge.gitstore.index_db import IndexDB
from lodge.gitstore.index_space import clear
from lodge.gitstore.index_transactions import transaction


@pytest.mark.parametrize("cold", [False, True])
def test_three_hundred_relisted_folders_bound_spawns(
    cached: tuple[Path, IndexDB], cold: bool
) -> None:
    repo, index = cached
    for n in range(300):
        write(repo, f"lodge/decisions/folder-{n}/record.md", "Synthetic berth.\n")
    git(repo, "add", "--", "lodge")
    git(repo, "commit", "-m", "Synthetic folders")
    seed(cached)
    write(repo, "lodge/decisions/new.md", "New base.\n")
    git(repo, "add", "--", "lodge")
    git(repo, "commit", "-m", "Change synthetic base")
    if cold:
        index.db.execute("DELETE FROM folders")
        index.db.execute("DELETE FROM folder_roots")
    with patch.object(subprocess, "Popen", wraps=subprocess.Popen) as calls:
        opened(repo, index).identities()
    processes = [c.args[0] for c in calls.call_args_list if c.args[0][0] == "git"]
    assert len(processes) <= 15, len(processes)
    listings = [args for args in processes if "ls-tree" in args]
    assert len(listings) == 1 and "-r" in listings[0]
    agrees(opened(repo, index))


def test_clear_prunes_only_removed_checkout_roots(cached: tuple[Path, IndexDB]) -> None:
    repo, index = seed(cached)
    other = worktree(repo, "other")
    agrees(opened(other, index))
    root = git(repo, "rev-parse", "--absolute-git-dir")
    removed = git(other, "rev-parse", "--absolute-git-dir")
    before = index.db.execute("SELECT * FROM folders WHERE root=?", (root,)).fetchall()
    count = index.db.execute("SELECT * FROM folder_roots WHERE root=?", (root,)).fetchall()
    shutil.rmtree(other)
    git(repo, "worktree", "prune")
    assert not Path(removed).exists()
    with transaction(index.db, write=True):
        clear(index.db)
    assert index.db.execute("SELECT * FROM folders WHERE root=?", (removed,)).fetchall() == []
    assert index.db.execute("SELECT * FROM folder_roots WHERE root=?", (removed,)).fetchall() == []
    assert index.db.execute("SELECT * FROM folders WHERE root=?", (root,)).fetchall() == before
    assert index.db.execute("SELECT * FROM folder_roots WHERE root=?", (root,)).fetchall() == count
