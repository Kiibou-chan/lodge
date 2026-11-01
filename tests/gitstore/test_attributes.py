"""Every conversion source makes raw working-tree bytes authoritative."""

import subprocess
from collections.abc import Mapping, Sequence
from pathlib import Path
from unittest.mock import patch

import pytest

from gitstore.repos import git, write
from gitstore.test_identity import RECORD, agrees, prepared
from lodge.gitstore import git as runner
from lodge.gitstore.attributes import Conversions
from lodge.gitstore.flags import Flags

OTHER = "lodge/spec/plain.txt"


def converting(repo: Path) -> frozenset[str]:
    flags = Flags(repo)
    return Conversions(repo, flags).paths([RECORD, OTHER], flags.read())


@pytest.mark.parametrize("system_disabled", [False, True])
def test_no_sources_no_check_attr_call(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, system_disabled: bool
) -> None:
    original = runner.attempt

    def isolated_system(
        args: Sequence[str],
        cwd: Path,
        env: Mapping[str, str] | None = None,
        input: runner.Input = None,
    ) -> subprocess.CompletedProcess[bytes]:
        if list(args) == ["var", "GIT_ATTR_SYSTEM"]:
            return subprocess.CompletedProcess(
                args, 0, str(tmp_path / "absent-system-attributes").encode(), b""
            )
        return original(args, cwd, {**(env or {}), "GIT_ATTR_NOSYSTEM": "1"}, input)

    repo, store = prepared(tmp_path)
    if not system_disabled:
        monkeypatch.delenv("GIT_ATTR_NOSYSTEM")
    with patch.object(runner, "attempt", side_effect=isolated_system) as calls:
        assert converting(repo) == set()
        agrees(store)
    assert not any(call.args[0][0] == "check-attr" for call in calls.call_args_list)
    variables = [call.args[0] for call in calls.call_args_list if call.args[0][0] == "var"]
    assert all(len(args) == 2 for args in variables)
    assert {args[1] for args in variables} == (
        {"GIT_ATTR_GLOBAL"} if system_disabled else {"GIT_ATTR_GLOBAL", "GIT_ATTR_SYSTEM"}
    )


@pytest.mark.parametrize(
    "value", ["true", "yes", "on", "1", "input", "false", "no", "off", "0", ""]
)
def test_autocrlf_spellings(tmp_path: Path, value: str) -> None:
    repo, store = prepared(tmp_path)
    git(repo, "config", "core.autocrlf", value)
    assert converting(repo) == (
        {RECORD, OTHER} if value in {"true", "yes", "on", "1", "input"} else set()
    )
    agrees(store)


def test_global_attributes_file_reads_from_disk(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo, store = prepared(tmp_path)
    config = tmp_path / "xdg"
    monkeypatch.setenv("XDG_CONFIG_HOME", str(config))
    (config / "git").mkdir(parents=True)
    (config / "git/attributes").write_text("*.md text eol=crlf\n")
    (repo / RECORD).write_bytes(b"Original berth.\r\n")
    git(repo, "add", "--", RECORD)
    assert not git(repo, "diff", "--cached", "--name-only", "--", RECORD)
    assert converting(repo) == {RECORD}
    agrees(store)


@pytest.mark.parametrize("source", ["info", "configured", "system"])
def test_info_attributes_and_attributes_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, source: str
) -> None:
    repo, store = prepared(tmp_path)
    if source == "info":
        path = Path(git(repo, "rev-parse", "--git-path", "info/attributes"))
        path = path if path.is_absolute() else repo / path
    else:
        path = tmp_path / f"{source}-attributes"
        if source == "configured":
            git(repo, "config", "core.attributesFile", str(path))
        else:
            monkeypatch.setenv("GIT_ATTR_SYSTEM", str(path))
            monkeypatch.delenv("GIT_ATTR_NOSYSTEM", raising=False)
    path.write_text("*.md text eol=crlf\n")
    (repo / RECORD).write_bytes(b"Original berth.\r\n")
    original = runner.attempt

    def system_source(
        args: Sequence[str],
        cwd: Path,
        env: Mapping[str, str] | None = None,
        input: runner.Input = None,
    ) -> subprocess.CompletedProcess[bytes]:
        # Model a system installation's attributes path without writing outside tmp_path.
        if source == "system" and list(args) == ["var", "GIT_ATTR_SYSTEM"]:
            return subprocess.CompletedProcess(args, 0, str(path).encode(), b"")
        if source == "system" and args[0] == "check-attr":
            args = ["-c", f"core.attributesFile={path}", *args]
        return original(args, cwd, {**(env or {}), "GIT_ATTR_NOSYSTEM": "1"}, input)

    with patch.object(runner, "attempt", side_effect=system_source):
        assert converting(repo) == {RECORD}
        agrees(store)


@pytest.mark.parametrize("legacy", [False, True], ids=["text-eol", "legacy-crlf"])
def test_text_attribute_on_one_pattern(tmp_path: Path, legacy: bool) -> None:
    repo, store = prepared(tmp_path)
    write(repo, OTHER, "Unconverted.\n")
    write(
        repo,
        ".gitattributes",
        "lodge/*.md crlf\n" if legacy else "lodge/decisions/*.md text eol=crlf\n",
    )
    if legacy:
        git(repo, "config", "core.eol", "crlf")
    path = "lodge/legacy.md" if legacy else RECORD
    write(repo, path, "Original berth.\r\n")
    flags = Flags(repo)
    assert Conversions(repo, flags).paths([path, OTHER], flags.read()) == {path}
    agrees(store)


def test_root_attributes_only_in_the_index(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)
    git(repo, "config", "filter.berth.clean", "sed s/WORKTREE/COMMITTED/g")
    git(repo, "config", "filter.berth.smudge", "sed s/COMMITTED/WORKTREE/g")
    write(repo, ".gitattributes", "*.md filter=berth\n")
    write(repo, RECORD, "WORKTREE statement.\n")
    git(repo, "add", "--", ".gitattributes", RECORD)
    git(repo, "commit", "-m", "Seed conversion")
    (repo / ".gitattributes").unlink()
    assert "COMMITTED" in git(repo, "show", f"HEAD:{RECORD}")
    assert converting(repo) == {RECORD}
    listing = agrees(store)
    assert store.texts(listing, [RECORD]) == {RECORD: "WORKTREE statement.\n"}


def test_git_var_failure_converts_every_path(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)
    original = runner.attempt

    def unsupported(
        args: Sequence[str],
        cwd: Path,
        env: Mapping[str, str] | None = None,
        input: runner.Input = None,
    ) -> subprocess.CompletedProcess[bytes]:
        if args[0] == "var":
            return subprocess.CompletedProcess(args, 129, b"", b"unsupported")
        return original(args, cwd, env, input)

    with patch.object(runner, "attempt", side_effect=unsupported):
        assert converting(repo) == {RECORD, OTHER}
        agrees(store)


def test_warm_change_of_a_source_agrees(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)
    store.identities()
    git(repo, "config", "core.autocrlf", "true")
    (repo / RECORD).write_bytes(b"Original berth.\r\n")
    agrees(store)
    git(repo, "config", "core.autocrlf", "false")
    source = tmp_path / "changed-attributes"
    source.write_text("*.md text eol=crlf\n")
    git(repo, "config", "core.attributesFile", str(source))
    agrees(store)
    source.write_text("*.md filter=berth\n")
    git(repo, "config", "filter.berth.clean", "sed s/WORKTREE/COMMITTED/g")
    write(repo, RECORD, "WORKTREE edit.\n")
    git(repo, "add", "--", RECORD)
    git(repo, "commit", "-m", "Seed filtered bytes")
    agrees(store)
