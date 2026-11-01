"""Exact trees key the bytes read, including changes git's stat shortcuts hide."""

import os
from pathlib import Path

from gitstore.repos import CHECKOUT, Ticker, checkout_project, commit, git, write
from lodge.core import blob_id
from lodge.gitstore import open_store

RECORD = "lodge/decisions/d-aaaaaa-berths.md"
ATTACHMENT = "lodge/attachments/d-aaaaaa/log.bin"


def index_blobs(repo: Path) -> dict[str, str]:
    return {
        path: meta.split()[1]
        for item in git(repo, "ls-files", "-s", "--", "lodge").splitlines()
        for meta, path in [item.split("\t", 1)]
        if not path.startswith("lodge/attachments/")
    }


def test_disk_tree_blobs_hash_the_bytes_read(tmp_path: Path) -> None:
    _, repo = checkout_project(tmp_path)
    commit(repo, RECORD, "Berths\n", "Add a record")
    commit(repo, ATTACHMENT, "listed only\n", "Add an attachment")
    store = open_store(repo, CHECKOUT, Ticker())
    clean, _ = store.trees()
    assert clean.blobs == index_blobs(repo)
    write(repo, RECORD, "Edited berths\r\n")
    untracked = "lodge/decisions/d-bbbbbb-untracked.md"
    (repo / untracked).write_bytes(b"\xff\x00\x80\n")
    linked = "lodge/decisions/d-cccccc-link.md"
    (repo / linked).symlink_to("d-aaaaaa-berths.md")
    nonregular = "lodge/decisions/pipe"
    os.mkfifo(repo / nonregular)
    changed, _ = store.trees()
    expected = {
        path: blob_id(
            os.fsencode(os.readlink(repo / path))
            if path == linked
            else b""
            if path == nonregular
            else (repo / path).read_bytes()
        )
        for path in changed.files
    }
    assert changed.blobs == expected
    assert changed.blobs[RECORD] != clean.blobs[RECORD]
    assert changed.attachments == {ATTACHMENT} and ATTACHMENT not in changed.blobs
    for path, text in changed.files.items():
        assert changed.blobs[path] == blob_id(text.encode("utf-8", "surrogateescape"))


def test_disk_tree_ignores_assume_unchanged(tmp_path: Path) -> None:
    _, repo = checkout_project(tmp_path)
    commit(repo, RECORD, "Original\n", "Add a record")
    claimed = index_blobs(repo)[RECORD]
    git(repo, "update-index", "--assume-unchanged", RECORD)
    write(repo, RECORD, "Edited behind the flag\n")
    current, _ = open_store(repo, CHECKOUT, Ticker()).trees()
    assert current.blobs[RECORD] == blob_id((repo / RECORD).read_bytes())
    assert current.blobs[RECORD] != claimed


def test_read_tree_blobs_are_git_object_ids(tmp_path: Path) -> None:
    _, repo = checkout_project(tmp_path)
    commit(repo, RECORD, "Committed berths\n", "Add a record")
    commit(repo, ATTACHMENT, "listed only\n", "Add an attachment")
    linked = "lodge/decisions/d-bbbbbb-link.md"
    (repo / linked).symlink_to("d-aaaaaa-berths.md")
    git(repo, "add", "--", linked)
    git(repo, "commit", "-m", "Add a symbolic link")
    expected = index_blobs(repo)
    git(repo, "push", "origin", "main")
    write(repo, RECORD, "Working tree differs\n")
    _, committed = open_store(repo, CHECKOUT, Ticker()).trees()
    assert committed.blobs == expected
    assert set(committed.blobs) == set(committed.files)
    assert committed.attachments == {ATTACHMENT} and ATTACHMENT not in committed.blobs


def test_gitlink_keys_the_empty_text_read(tmp_path: Path) -> None:
    _, repo = checkout_project(tmp_path)
    path = "lodge/decisions/submodule"
    git(
        repo,
        "update-index",
        "--add",
        "--cacheinfo",
        f"160000,{git(repo, 'rev-parse', 'HEAD')},{path}",
    )
    git(repo, "commit", "-m", "Add a gitlink")
    git(repo, "push", "origin", "main")
    # A non-regular file on disk also reads as empty text.
    os.mkfifo(repo / path)
    disk, committed = open_store(repo, CHECKOUT, Ticker()).trees()
    assert committed.files[path] == disk.files[path] == ""
    assert committed.blobs[path] == disk.blobs[path] == blob_id(b"")
