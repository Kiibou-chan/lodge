"""Lazy mappings, coherent index groups, conversion sources, and R11 histories."""

import os
import subprocess
import time
from collections.abc import Sequence
from pathlib import Path
from unittest.mock import patch

import pytest

from gitstore.repos import (
    BRANCH,
    CHECKOUT,
    Ticker,
    bare_remote,
    git,
    initialised,
    publish_one,
    write,
)
from gitstore.test_identity import RECORD, agrees, prepared
from lodge.core import blob_id
from lodge.gitstore import disk, open_store
from lodge.gitstore import git as runner
from lodge.gitstore.attributes import Conversions
from lodge.gitstore.flags import Flags


def test_identities_run_no_ls_tree_for_published(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)
    with patch.object(runner, "run_bytes", wraps=runner.run_bytes) as calls:
        store.identities()
        assert sum(c.args[0][0] == "ls-tree" for c in calls.call_args_list) == 1
        store.listings()
        assert sum(c.args[0][0] == "ls-tree" for c in calls.call_args_list) == 1
    write(repo, RECORD, "New commit.\n")
    git(repo, "add", "--", RECORD)
    git(repo, "commit", "-m", "Advance head")
    store = open_store(repo, CHECKOUT, Ticker())
    with patch.object(runner, "run_bytes", wraps=runner.run_bytes) as calls:
        store.identities()
        assert sum(c.args[0][0] == "ls-tree" for c in calls.call_args_list) == 1
        store.listings()
        assert sum(c.args[0][0] == "ls-tree" for c in calls.call_args_list) == 2


@pytest.mark.parametrize("change", ["clean", "edit", "untracked", "deleted", "behind", "branch"])
def test_lazy_listings_agree(tmp_path: Path, change: str) -> None:

    if change == "branch":
        repo, clock = initialised(bare_remote(tmp_path), "branch")
        publish_one(repo, clock, {RECORD: "Branch berth.\n"})
        store = open_store(repo, BRANCH, clock)
    else:
        repo, store = prepared(tmp_path)
        if change in {"edit", "behind"}:
            write(repo, RECORD, "Changed berth.\n")
        if change == "behind":
            git(repo, "add", "--", RECORD)
            git(repo, "commit", "-m", "Advance head")
        if change == "untracked":
            write(repo, "lodge/new.md", "Untracked berth.\n")
        if change == "deleted":
            git(repo, "rm", "--", RECORD)
    agrees(store)


def test_staged_between_diff_calls_is_seen(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)
    write(repo, RECORD, "Race edit.\n")
    original = subprocess.Popen.communicate
    staged = False

    def communicate(
        self: subprocess.Popen[bytes], *args: object, **kwargs: object
    ) -> tuple[bytes, bytes]:
        nonlocal staged
        if isinstance(self.args, list) and "diff-index" in self.args:
            result = original(self)
        else:
            return original(self, *args, **kwargs)  # type: ignore[arg-type]
        if isinstance(self.args, list) and "diff-index" in self.args and not staged:
            staged = True
            git(repo, "add", "--", RECORD)
        return result

    with patch.object(subprocess.Popen, "communicate", communicate):
        agrees(store)
    assert staged


def test_index_changing_every_time_falls_back_to_exact(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)
    write(repo, RECORD, "Pinned fallback.\n")
    count = 0
    original = runner.run_many

    def changing(
        calls: Sequence[Sequence[str]], cwd: Path
    ) -> list[subprocess.CompletedProcess[bytes]]:
        nonlocal count
        result = original(calls, cwd)
        count += 1
        os.utime(repo / ".git/index", ns=(1, count))
        return result

    with (
        patch.object(runner, "run_many", changing),
        patch.object(disk, "tree", wraps=disk.tree) as exact,
    ):
        agrees(store)
        assert count == 3
        # trees() is separately exact; the identity fallback is read exactly once.
        assert exact.call_count == 1
    current = store.listings()[0]
    write(repo, RECORD, "Later bytes.\n")
    assert store.texts(current, [RECORD]) == {RECORD: "Pinned fallback.\n"}


def test_conversion_key_takes_no_paths(tmp_path: Path) -> None:
    repo, _ = prepared(tmp_path)
    write(repo, ".gitattributes", "*.md text eol=crlf\n")
    flags = Flags(repo)
    conversions = Conversions(repo, flags)
    flagged = flags.read()
    assert conversions.paths(lambda: {RECORD}, flagged) == {RECORD}

    def forbidden() -> set[str]:
        raise AssertionError("built paths on a conversion cache hit")

    with patch.object(runner, "attempt", wraps=runner.attempt) as calls:
        assert conversions.paths(forbidden, flagged) == {RECORD}
    assert not any(c.args[0][0] == "check-attr" for c in calls.call_args_list)


@pytest.mark.parametrize("indexed", [False, True])
def test_nested_attributes_found_without_a_path_scan(tmp_path: Path, indexed: bool) -> None:
    repo, store = prepared(tmp_path)
    write(repo, "lodge/decisions/.gitattributes", "*.md text eol=crlf\n")
    if indexed:
        git(repo, "add", "--", "lodge/decisions/.gitattributes")
        (repo / "lodge/decisions/.gitattributes").unlink()
    (repo / RECORD).write_bytes(b"Original berth.\r\n")
    agrees(store)


def test_bare_autocrlf_key_converts(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)
    with (repo / ".git/config").open("a") as config:
        config.write("\n[core]\n\tautocrlf\n")
    (repo / RECORD).write_bytes(b"Original berth.\r\n")
    git(repo, "add", "--", RECORD)
    assert not git(repo, "status", "--porcelain", "--", RECORD)
    agrees(store)


def removed_history(repo: Path, attribute: str) -> None:
    marker = "INDEXTXT" if attribute == "filter=berth" else "WORKTREE"
    write(repo, RECORD, f"Original $Id$ {marker} berth.\n")
    git(repo, "add", "--", RECORD)
    git(repo, "commit", "-m", "Synthetic conversion base")
    source = repo / ".gitattributes"
    if attribute == "filter=berth":
        git(repo, "config", "filter.berth.clean", "sed s/WORKTREE/INDEXTXT/g")
        git(repo, "config", "filter.berth.smudge", "sed s/INDEXTXT/WORKTREE/g")
    source.write_text(f"*.md {attribute}\n")
    if attribute == "working-tree-encoding=UTF-16":
        (repo / RECORD).write_bytes("Original $Id$ WORKTREE berth.\n".encode("utf-16"))
    elif attribute == "text eol=crlf":
        (repo / RECORD).write_bytes(b"Original $Id$ WORKTREE berth.\r\n")
    elif attribute in {"ident", "filter=berth"}:
        (repo / RECORD).unlink()
        git(repo, "checkout-index", "-f", "-u", "--", RECORD)
    time.sleep(2.05)
    git(repo, "add", "--", RECORD)
    source.unlink()
    assert not git(repo, "diff-index", "--cached", "HEAD", "--name-only", "--", RECORD)
    assert not git(repo, "diff-files", "--name-only", "--", RECORD)


ATTRIBUTES = ["ident", "working-tree-encoding=UTF-16", "filter=berth", "text eol=crlf"]


@pytest.mark.parametrize("attribute", ATTRIBUTES)
def test_removed_attributes_agree(tmp_path: Path, attribute: str) -> None:
    repo, _ = prepared(tmp_path)
    removed_history(repo, attribute)
    store = open_store(repo, CHECKOUT, Ticker())
    agrees(store)
    # All five indexed reads consume these same pinned listing/text interfaces.
    # gate and add consume trees(), whose blobs must always hash disk bytes.

    assert store.trees()[0].blobs[RECORD] == blob_id((repo / RECORD).read_bytes())


@pytest.mark.skip(reason="awaits the author's STALE-1")
@pytest.mark.parametrize("attribute", ATTRIBUTES)
def test_removed_attributes_follow_the_index(tmp_path: Path, attribute: str) -> None:
    repo, _ = prepared(tmp_path)
    removed_history(repo, attribute)
    store = open_store(repo, CHECKOUT, Ticker())
    store.identities()
    listing = store.listings()[0]
    assert store.texts(listing, [RECORD])[RECORD] == git(repo, "show", f":{RECORD}") + "\n"

    assert store.trees()[0].blobs[RECORD] == blob_id((repo / RECORD).read_bytes())


def test_every_file_read_without_a_conversion_source(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)
    with patch.object(disk, "read_at", wraps=disk.read_at) as reads:
        store.identities()
    assert {c.args[1] for c in reads.call_args_list} == {
        p.relative_to(repo).as_posix() for p in (repo / "lodge").rglob("*") if p.is_file()
    }


def test_exact_fallback_identity_separates_attachment_names(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)
    original = runner.run_many
    generation = 0

    def changing(
        calls: Sequence[Sequence[str]], cwd: Path
    ) -> list[subprocess.CompletedProcess[bytes]]:
        nonlocal generation
        result = original(calls, cwd)
        generation += 1
        os.utime(repo / ".git/index", ns=(1, generation))
        return result

    write(repo, "lodge/attachments/a", "One attachment.\n")
    write(repo, "lodge/attachments/b", "Another attachment.\n")
    with patch.object(runner, "run_many", changing):
        before = agrees(store)
        (repo / "lodge/attachments/a").unlink()
        (repo / "lodge/attachments/b").unlink()
        write(repo, "lodge/attachments/a\nlodge/attachments/b", "One unusual name.\n")
        after = agrees(store)
    assert before.ident != after.ident
