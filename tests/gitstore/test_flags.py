"""Flags and conversion caches are private to one process and keyed on both sides."""

from pathlib import Path
from unittest.mock import patch

from gitstore.repos import git, write
from gitstore.test_identity import RECORD, agrees, prepared
from lodge.gitstore import git as runner
from lodge.gitstore.attributes import Conversions
from lodge.gitstore.flags import Flags


def test_assume_unchanged_edit_agrees(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)
    store.identities()
    git(repo, "update-index", "--assume-unchanged", RECORD)
    write(repo, RECORD, "Assumed unchanged, actually edited.\n")
    agrees(store)


def test_skip_worktree_missing_file_agrees(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)
    git(repo, "update-index", "--skip-worktree", RECORD)
    (repo / RECORD).unlink()
    assert RECORD not in agrees(store).blobs


def test_ignore_stat_entries_agree(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)
    git(repo, "config", "core.ignoreStat", "true")
    git(repo, "update-index", "--really-refresh")
    write(repo, RECORD, "IgnoreStat cannot hide this.\n")
    agrees(store)


def test_cached_flags_and_conversions_keyed(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)
    before = Flags(repo).key()
    store.identities()
    git(repo, "update-index", "--assume-unchanged", RECORD)
    assert Flags(repo).key() != before
    write(repo, RECORD, "Edit after the flag change.\n")
    agrees(store)
    source = repo / ".gitattributes"
    source.write_text("*.md text eol=crlf\n")
    (repo / RECORD).write_bytes(b"Converted on disk.\r\n")
    agrees(store)
    with patch.object(runner, "attempt", wraps=runner.attempt) as calls:
        agrees(store)
    assert not any(c.args[0][0] == "check-attr" for c in calls.call_args_list)
    source.write_text("*.md -text -eol\n")
    with patch.object(runner, "attempt", wraps=runner.attempt) as calls:
        agrees(store)
    assert any(c.args[0][0] == "check-attr" for c in calls.call_args_list)
    # An unstable source must not be retained under the stable key.
    source.write_text("*.md text eol=crlf\n")
    original = Conversions._key
    count = 0

    def key(self: Conversions, *args: object, **kwargs: object) -> object:
        nonlocal count
        result = original(self, *args, **kwargs)  # type: ignore[arg-type]
        count += 1
        if count == 1:
            source.write_text("*.md -text -eol\n")
        return result

    with patch.object(Conversions, "_key", key):
        agrees(store)
    agrees(store)


def test_index_attributes_appearing_between_cache_keys(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)
    store.identities()
    write(repo, ".gitattributes", "*.md text eol=crlf\n")
    git(repo, "add", "--", ".gitattributes")
    (repo / ".gitattributes").unlink()
    (repo / RECORD).write_bytes(b"Original berth.\r\n")
    agrees(store)
