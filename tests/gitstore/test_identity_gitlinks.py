"""Gitlinks use the exact readers' empty text or the checkout's real files."""

from pathlib import Path
from unittest.mock import patch

import pytest

from gitstore.repos import BRANCH, CHECKOUT, Ticker, git, write
from gitstore.test_identity import agrees, prepared
from lodge.core import blob_id
from lodge.gitstore import git as runner
from lodge.gitstore import open_store

LINK = "lodge/decisions/submodule"
MISSING = "1" * 40


def submodule(tmp_path: Path, mode: str, content: str) -> None:
    repo, _ = prepared(tmp_path)
    git(repo, "update-index", "--add", "--cacheinfo", f"160000,{MISSING},{LINK}")
    git(repo, "commit", "-m", "Synthetic unavailable gitlink")
    git(repo, "config", "diff.ignoreSubmodules", "all")
    if content != "absent":
        (repo / LINK).mkdir()
    if content == "populated":
        write(repo, f"{LINK}/child.md", "Submodule disk file.\n")
    if mode == "branch":
        git(repo, "push", "origin", "HEAD:refs/heads/lodge")
    store = open_store(repo, BRANCH if mode == "branch" else CHECKOUT, Ticker())
    listing = agrees(store)
    if mode == "branch":
        assert listing.blobs[LINK] == blob_id(b"")
        assert store.texts(listing, [LINK]) == {LINK: ""}
    else:
        assert LINK not in listing.blobs
        assert (f"{LINK}/child.md" in listing.blobs) == (content == "populated")


@pytest.mark.parametrize("mode", ["checkout", "branch"])
def test_empty_submodule_folder(tmp_path: Path, mode: str) -> None:
    submodule(tmp_path, mode, "empty")


@pytest.mark.parametrize("mode", ["checkout", "branch"])
def test_populated_submodule(tmp_path: Path, mode: str) -> None:
    submodule(tmp_path, mode, "populated")


@pytest.mark.parametrize("mode", ["checkout", "branch"])
def test_absent_submodule_folder(tmp_path: Path, mode: str) -> None:
    submodule(tmp_path, mode, "absent")


def test_branch_gitlink_key_is_empty_text(tmp_path: Path) -> None:
    submodule(tmp_path, "branch", "absent")


def test_submodule_commit_absent_from_the_object_database(tmp_path: Path) -> None:
    with patch.object(runner, "run_bytes", wraps=runner.run_bytes) as calls:
        submodule(tmp_path, "branch", "empty")
    assert not any(
        c.args[0][0] == "cat-file" and MISSING in str(c.kwargs.get("input", ""))
        for c in calls.call_args_list
    )
