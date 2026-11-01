"""Flags and conversion caches are private to one process and keyed on both sides."""

import subprocess
from collections.abc import Mapping, Sequence
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
    flags = Flags(repo)
    original = runner.attempt
    count = 0

    def race_flags(
        args: Sequence[str],
        cwd: Path,
        env: Mapping[str, str] | None = None,
        input: runner.Input = None,
    ) -> subprocess.CompletedProcess[bytes]:
        nonlocal count
        if args[0] == "ls-files":
            count += 1
            if count == 1:
                git(repo, "update-index", "--assume-unchanged", RECORD)
        return original(args, cwd, env, input)

    with patch.object(runner, "attempt", side_effect=race_flags):
        assert RECORD in flags.read().paths
        assert RECORD in flags.read().paths
        flags.read()
    assert count == 2  # The raced result was not kept; the stable one was.
    before = flags.key()
    git(repo, "update-index", "--no-assume-unchanged", RECORD)
    assert flags.key() != before and RECORD not in flags.read().paths
    write(repo, RECORD, "Edit after flag race.\n")
    agrees(store)

    source = repo / ".gitattributes"
    source.write_text("*.md text eol=crlf\n")
    conversions = Conversions(repo, flags)
    paths = [RECORD, "lodge/spec/plain.txt"]
    flagged = flags.read()
    assert conversions.paths(paths, flagged) == {RECORD}
    with patch.object(runner, "attempt", wraps=original) as calls:
        conversions.paths(paths, flagged)
        assert not any(call.args[0][0] == "check-attr" for call in calls.call_args_list)
    git(repo, "config", "core.autocrlf", "true")
    assert conversions.paths(paths, flagged) == set(paths)
    git(repo, "config", "core.autocrlf", "false")
    source.write_text("*.md -text -eol\n")
    assert conversions.paths(paths, flagged) == set()
    source.write_text("*.md text eol=crlf\n")
    # A changed-and-restored source has identical bytes but a different ctime.
    count = 0

    def race_attributes(
        args: Sequence[str],
        cwd: Path,
        env: Mapping[str, str] | None = None,
        input: runner.Input = None,
    ) -> subprocess.CompletedProcess[bytes]:
        nonlocal count
        if args[0] != "check-attr":
            return original(args, cwd, env, input)
        count += 1
        if count != 1:
            return original(args, cwd, env, input)
        raw = source.read_bytes()
        source.write_text("*.md -text -eol\n")
        try:
            return original(args, cwd, env, input)
        finally:
            source.write_bytes(raw)

    with patch.object(runner, "attempt", side_effect=race_attributes):
        assert conversions.paths(paths, flagged) == set()
        assert conversions.paths(paths, flagged) == {RECORD}
        assert conversions.paths(paths, flagged) == {RECORD}
    assert count == 2
    (repo / RECORD).write_bytes(b"Filtered on disk.\r\n")
    agrees(store)


def test_index_attributes_appearing_between_cache_keys(tmp_path: Path) -> None:
    repo, _ = prepared(tmp_path)
    flags = Flags(repo)
    stale_flags = flags.read()
    conversions = Conversions(repo, flags)
    write(repo, ".gitattributes", "*.md text eol=crlf\n")
    git(repo, "add", "--", ".gitattributes")
    (repo / ".gitattributes").unlink()
    # The index changed after flags were collected and before conversions took its key.
    assert conversions.paths([RECORD], stale_flags) == set()
    assert conversions.paths([RECORD], flags.read()) == {RECORD}
