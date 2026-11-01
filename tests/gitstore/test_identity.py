"""Fast checkout states agree with exact trees, including unusual paths."""

import os
import shutil
from pathlib import Path

import pytest

from gitstore.repos import CHECKOUT, Ticker, checkout_project, git, write
from lodge.app import Store
from lodge.core import Listing
from lodge.gitstore import init_store, open_store

RECORD = "lodge/decisions/old.md"
ATTACHMENT = "lodge/attachments/d-aaaaaa/log.txt"


def prepared(tmp_path: Path) -> tuple[Path, Store]:
    _, repo = checkout_project(tmp_path)
    write(repo, RECORD, "Original berth.\n")
    write(repo, ATTACHMENT, "Original evidence.\n")
    git(repo, "add", "--", "lodge")
    git(repo, "commit", "-m", "Seed made-up store")
    git(repo, "push", "origin", "main")
    return repo, open_store(repo, CHECKOUT, Ticker())


def agrees(store: Store) -> Listing:
    identities = store.identities()
    listings = store.listings()
    assert identities == tuple(listing.ident for listing in listings)
    for listing, tree in zip(listings, store.trees(), strict=True):
        assert dict(listing.blobs) == dict(tree.blobs)
        assert listing.attachments == tree.attachments
        assert store.texts(listing, tuple(listing.blobs)) == dict(tree.files)
    return listings[0]


def test_clean_checkout_ident_is_the_head_tree(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)
    listing = agrees(store)
    assert store.identities() == (listing.ident, listing.ident)
    assert listing.ident == git(repo, "rev-parse", "HEAD:lodge")


def test_touched_file_keeps_the_clean_ident(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)
    before = agrees(store).ident
    os.utime(repo / RECORD, None)
    assert agrees(store).ident == before


def test_staged_edit_reverted_on_disk_keeps_the_clean_ident(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)
    before = agrees(store).ident
    original = (repo / RECORD).read_bytes()
    write(repo, RECORD, "Staged edit.\n")
    git(repo, "add", "--", RECORD)
    (repo / RECORD).write_bytes(original)
    assert agrees(store).ident == before


def test_unstaged_edit_agrees(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)
    before = agrees(store).ident
    write(repo, RECORD, "Edited berth.\n")
    listing = agrees(store)
    assert listing.ident != before
    write(repo, RECORD, "Later edit.\n")
    assert store.texts(listing, [RECORD]) == {RECORD: "Edited berth.\n"}


def test_untracked_file_agrees(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)
    write(repo, "lodge/decisions/new.md", "Untracked.\n")
    assert "lodge/decisions/new.md" in agrees(store).blobs


def test_ignored_file_agrees(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)
    write(repo, ".gitignore", "lodge/decisions/ignored.md\n")
    write(repo, "lodge/decisions/ignored.md", "Ignored.\n")
    assert "lodge/decisions/ignored.md" in agrees(store).blobs


def test_deleted_file_agrees(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)
    (repo / RECORD).unlink()
    assert RECORD not in agrees(store).blobs


def test_staged_deletion_left_on_disk_agrees(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)
    before = agrees(store).ident
    git(repo, "rm", "--cached", "--", RECORD)
    assert agrees(store).ident == before


def test_rename_agrees(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)
    git(repo, "mv", RECORD, "lodge/decisions/renamed.md")
    assert RECORD not in agrees(store).blobs


def test_symbolic_link_agrees(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)
    (repo / RECORD).unlink()
    (repo / RECORD).symlink_to("target.md")
    (repo / "lodge/decisions/folder-link").symlink_to("../spec", target_is_directory=True)
    assert store.texts(agrees(store), [RECORD]) == {RECORD: "target.md"}


@pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="requires named pipes")
def test_fifo_agrees(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)
    (repo / RECORD).unlink()
    os.mkfifo(repo / RECORD)
    assert store.texts(agrees(store), [RECORD]) == {RECORD: ""}


def test_attachment_bytes_changed_keeps_the_ident(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)
    before = agrees(store).ident
    write(repo, ATTACHMENT, "Changed evidence.\n")
    assert agrees(store).ident == before


def test_unborn_head(tmp_path: Path) -> None:
    git(tmp_path, "init", "-b", "main")
    init_store(tmp_path, CHECKOUT)
    write(tmp_path, RECORD, "Unborn.\n")
    assert RECORD in agrees(open_store(tmp_path, CHECKOUT, Ticker())).blobs


def test_head_without_lodge(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)
    git(repo, "rm", "-r", "--cached", "--", "lodge")
    git(repo, "commit", "-m", "Remove committed store")
    assert RECORD in agrees(store).blobs


def test_commit_after_edit_agrees(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)
    write(repo, RECORD, "Edited then committed.\n")
    before = agrees(store)
    git(repo, "add", "--", RECORD)
    git(repo, "commit", "-m", "Commit edit")
    assert agrees(store).blobs == before.blobs


def test_attachment_only_commit_agrees(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)
    before = agrees(store)
    write(repo, ATTACHMENT, "Changed and committed evidence.\n")
    git(repo, "add", "--", ATTACHMENT)
    git(repo, "commit", "-m", "Commit attachment edit")
    after = agrees(store)
    assert (after.blobs, after.attachments) == (before.blobs, before.attachments)


def test_reverted_to_published_with_head_ahead_agrees(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)
    write(repo, RECORD, "New head.\n")
    git(repo, "add", "--", RECORD)
    git(repo, "commit", "-m", "Advance head")
    git(repo, "checkout", "origin/main", "--", RECORD)
    agrees(store)
    current, published = store.listings()
    assert (current.blobs, current.attachments) == (published.blobs, published.attachments)


@pytest.mark.parametrize("path", [RECORD, ATTACHMENT])
@pytest.mark.parametrize("populated", [False, True], ids=["empty", "populated"])
def test_file_replaced_by_folder_agrees(tmp_path: Path, path: str, populated: bool) -> None:
    repo, store = prepared(tmp_path)
    (repo / path).unlink()
    (repo / path).mkdir()
    if populated:
        write(repo, f"{path}/new.md", "Nested file.\n")
    listing = agrees(store)
    assert path not in listing.blobs and path not in listing.attachments


@pytest.mark.parametrize("path", ["lodge/decisions", "lodge/attachments/d-aaaaaa"])
def test_folder_replaced_by_file_agrees(tmp_path: Path, path: str) -> None:
    repo, store = prepared(tmp_path)
    shutil.rmtree(repo / path)
    write(repo, path, "A file instead of a folder.\n")
    listing = agrees(store)
    assert path in listing.blobs or path in listing.attachments


def test_head_with_a_file_instead_of_lodge_folder(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)
    git(repo, "rm", "-r", "--", "lodge")
    write(repo, "lodge", "A former root file.\n")
    git(repo, "add", "--", "lodge")
    git(repo, "commit", "-m", "Former store root was a file")
    (repo / "lodge").unlink()
    write(repo, RECORD, "Now a store folder.\n")
    assert RECORD in agrees(store).blobs
