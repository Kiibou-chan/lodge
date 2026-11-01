"""Ancestor links, inaccessible folders, and special-file swaps stay bounded."""

from __future__ import annotations

import multiprocessing
import os
import shutil
from collections.abc import Iterator
from pathlib import Path
from types import TracebackType
from unittest.mock import patch

import pytest

from gitstore.repos import git, write
from gitstore.test_identity import ATTACHMENT, RECORD, agrees, prepared
from lodge.gitstore import disk
from lodge.gitstore.checkout import disk_tree


def replace_folder(repo: Path, folder: str, target: Path) -> None:
    shutil.rmtree(repo / folder)
    (repo / folder).symlink_to(target, target_is_directory=True)


def test_folder_replaced_by_symlink_to_copy(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)
    target = tmp_path / "copy"
    shutil.copytree(repo / "lodge/decisions", target)
    replace_folder(repo, "lodge/decisions", target)
    assert RECORD not in agrees(store).blobs


def test_folder_replaced_by_symlink_to_other_content(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)
    target = tmp_path / "other"
    target.mkdir()
    (target / "old.md").write_text("Outside content.\n")
    replace_folder(repo, "lodge/decisions", target)
    assert RECORD not in agrees(store).blobs


def test_attachments_folder_symlink(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)
    target = tmp_path / "attachments-copy"
    shutil.copytree(repo / "lodge/attachments", target)
    replace_folder(repo, "lodge/attachments", target)
    assert ATTACHMENT not in agrees(store).attachments


def test_folder_link_to_outside_is_never_read(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)
    target = tmp_path / "outside"
    target.mkdir()
    (target / "old.md").write_text("Forbidden outside bytes.\n")
    replace_folder(repo, "lodge/decisions", target)
    listing = agrees(store)
    assert RECORD not in listing.blobs
    assert "Forbidden outside bytes" not in str(store.texts(listing, tuple(listing.blobs)))


def test_link_inside_an_attachment_path(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)
    target = tmp_path / "attachment-target"
    shutil.copytree(repo / "lodge/attachments/d-aaaaaa", target)
    replace_folder(repo, "lodge/attachments/d-aaaaaa", target)
    assert ATTACHMENT not in agrees(store).attachments


def test_folder_swapped_for_link_during_the_walk(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)
    target = tmp_path / "swapped"
    target.mkdir()
    (target / "old.md").write_text("Do not traverse.\n")
    original = os.scandir

    class Listed:
        def __init__(self, path: int | str | os.PathLike[str]) -> None:
            self.path = path
            self.entries = original(path)

        def __enter__(self) -> Iterator[os.DirEntry[str]]:
            return iter(self.entries)

        def __exit__(
            self,
            _kind: type[BaseException] | None,
            _error: BaseException | None,
            _traceback: TracebackType | None,
        ) -> None:
            self.entries.close()
            # The walk has classified every entry, but has not opened any child.
            if (
                isinstance(self.path, int)
                and os.readlink(f"/proc/self/fd/{self.path}") == str(repo / "lodge")
                and not (repo / "lodge/decisions").is_symlink()
            ):
                replace_folder(repo, "lodge/decisions", target)

    def swapped(path: int | str | os.PathLike[str]) -> Listed:
        return Listed(path)

    with patch.object(os, "scandir", swapped):
        listing = agrees(store)
    assert RECORD not in listing.blobs
    assert "lodge/decisions" in listing.blobs
    # Repeat against the exact reader with a fresh real folder.
    (repo / "lodge/decisions").unlink()
    write(repo, RECORD, "Before swap.\n")
    with patch.object(os, "scandir", swapped):
        exact = disk_tree(repo)
    assert RECORD not in exact.files and exact.files["lodge/decisions"] == str(target)


@pytest.mark.skipif(os.geteuid() == 0, reason="root can list unreadable folders")
@pytest.mark.parametrize("path", ["lodge/decisions", "lodge/decisions/submodule"])
def test_unlistable_folder_agrees(tmp_path: Path, path: str) -> None:
    repo, store = prepared(tmp_path)
    if path.endswith("submodule"):
        git(repo, "update-index", "--add", "--cacheinfo", f"160000,{'1' * 40},{path}")
        git(repo, "commit", "-m", "Synthetic unreadable submodule")
        git(repo, "config", "diff.ignoreSubmodules", "all")
        (repo / path).mkdir()
    folder = repo / path
    folder.chmod(0)
    try:
        listing = agrees(store)
        assert path not in listing.blobs
        if path == "lodge/decisions":
            assert RECORD not in listing.blobs
    finally:
        folder.chmod(0o755)


def test_fifo_agrees(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)
    (repo / RECORD).unlink()
    os.mkfifo(repo / RECORD)
    assert store.texts(agrees(store), [RECORD]) == {RECORD: ""}


def test_regular_file_swapped_for_fifo_before_open(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)

    def child() -> None:
        original = os.open

        def swapped(
            path: str | bytes | os.PathLike[str] | os.PathLike[bytes],
            flags: int,
            mode: int = 0o777,
            *,
            dir_fd: int | None = None,
        ) -> int:
            if path == "old.md" and dir_fd is not None and not flags & os.O_DIRECTORY:
                os.unlink("old.md", dir_fd=dir_fd)
                os.mkfifo("old.md", dir_fd=dir_fd)
            return original(path, flags, mode, dir_fd=dir_fd)

        with patch.object(os, "open", swapped):
            listing = agrees(store)
            assert store.texts(listing, [RECORD]) == {RECORD: ""}
            # trees() is the exact reader for both the gate and add.
            assert store.trees()[0].files[RECORD] == ""
            assert disk_tree(repo).files[RECORD] == ""
            walked = disk.walk(repo)
            try:
                assert disk.read_at(walked, RECORD) == b""
            finally:
                walked.close()

    process = multiprocessing.get_context("fork").Process(target=child)
    process.start()
    process.join(10)
    if process.is_alive():
        process.kill()
        process.join()
        pytest.fail("regular-to-FIFO swap blocked a reader")
    assert process.exitcode == 0
