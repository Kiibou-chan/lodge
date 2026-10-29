import os
import time
from pathlib import Path

import pytest

from gitstore.repos import BRANCH, Ticker, bare_remote, clone, git, initialised, seeded
from lodge.app import LodgeError, PublishOutcome
from lodge.core import CoreSettings, LengthGuidance
from lodge.gitstore import (
    GitMissing,
    NotARepository,
    NotInitialised,
    ProjectSettings,
    StoreSettings,
    data_root,
    init_store,
    load_settings,
    open_store,
    repo_root,
)
from lodge.gitstore.git import run

CHECKOUT = StoreSettings()
KEPT = ["lodge/decisions/.gitkeep", "lodge/spec/.gitkeep"]


def test_settings_absent_defaults(tmp_path: Path) -> None:
    assert load_settings(tmp_path) == ProjectSettings(CoreSettings(), StoreSettings(), {})


def test_settings_read_every_section(tmp_path: Path) -> None:
    (tmp_path / ".lodge.toml").write_text(
        '[length]\ntitle_chars = 90\n[import]\nsources = ["notes.md"]\n'
        '[store]\nmode = "branch"\nbranch = "records"\nremote = "upstream"\nbase = "trunk"\n'
        'max_staleness_seconds = 5\ncommit_trailer = "Co-Authored-By: A <a@example.com>"\n'
        "[hook]\nanything = 1\n"
    )
    found = load_settings(tmp_path)
    assert found.core == CoreSettings(LengthGuidance(title_chars=90), ("notes.md",))
    assert found.store == StoreSettings(
        "branch", "records", "upstream", "trunk", 5, "Co-Authored-By: A <a@example.com>"
    )
    assert found.raw["hook"] == {"anything": 1}


def test_settings_malformed_toml_is_lodge_error(tmp_path: Path) -> None:
    (tmp_path / ".lodge.toml").write_text("[store\n")
    with pytest.raises(LodgeError, match=r"\.lodge\.toml"):
        load_settings(tmp_path)


def test_settings_not_utf8_is_lodge_error(tmp_path: Path) -> None:
    (tmp_path / ".lodge.toml").write_bytes(b"[store]\nbranch = '\xff'\n")
    with pytest.raises(LodgeError, match=r"\.lodge\.toml"):
        load_settings(tmp_path)


def test_settings_unknown_section_named(tmp_path: Path) -> None:
    (tmp_path / ".lodge.toml").write_text("[nope]\nx = 1\n")
    with pytest.raises(LodgeError, match=r"unknown section \[nope\]"):
        load_settings(tmp_path)


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("[store]\nspeed = 1\n", "unknown key store.speed"),
        ('[store]\nmode = "server"\n', "store.mode must be"),
        ("[store]\nbranch = 3\n", "store.branch must be"),
        ('[store]\nbranch = "-x"\n', "store.branch must be"),
        ('[store]\nremote = ""\n', "store.remote must be"),
        ("[store]\nmax_staleness_seconds = -1\n", "store.max_staleness_seconds must be"),
        ("[store]\nmax_staleness_seconds = true\n", "store.max_staleness_seconds must be"),
        ("[store]\ncommit_trailer = 4\n", "store.commit_trailer must be"),
        ("store = 4\n", "store must be a table"),
        ("[length]\ntitle_chars = 0\n", "length.title_chars"),
    ],
)
def test_settings_errors_name_the_key(tmp_path: Path, text: str, message: str) -> None:
    (tmp_path / ".lodge.toml").write_text(text)
    with pytest.raises(LodgeError, match=message):
        load_settings(tmp_path)


def test_not_a_repository(tmp_path: Path) -> None:
    with pytest.raises(NotARepository, match="not inside a git repository"):
        repo_root(tmp_path)


def test_repo_root_of_a_subfolder(tmp_path: Path) -> None:
    repo = seeded(bare_remote(tmp_path), "work")
    (repo / "sub").mkdir()
    assert repo_root(repo / "sub") == repo.resolve()


def test_git_missing(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PATH", str(tmp_path))
    with pytest.raises(GitMissing, match="git"):
        repo_root(tmp_path)


def test_git_failure_is_one_line(tmp_path: Path) -> None:
    repo = seeded(bare_remote(tmp_path), "work")
    with pytest.raises(LodgeError) as raised:
        run(["cat-file", "-t", "nothing-here"], repo)
    assert "\n" not in str(raised.value) and "nothing-here" in str(raised.value)


def test_not_initialised_checkout(tmp_path: Path) -> None:
    repo = seeded(bare_remote(tmp_path), "work")
    with pytest.raises(NotInitialised, match="lodge init"):
        open_store(repo, CHECKOUT, Ticker()).trees()


def test_not_initialised_branch(tmp_path: Path) -> None:
    repo = seeded(bare_remote(tmp_path), "work")
    with pytest.raises(NotInitialised, match="lodge init"):
        open_store(repo, BRANCH, Ticker()).trees()


def test_branch_unreachable_remote_is_not_not_initialised(tmp_path: Path) -> None:
    repo = seeded(bare_remote(tmp_path), "work")
    git(repo, "remote", "set-url", "origin", str(tmp_path / "gone.git"))
    with pytest.raises(LodgeError) as raised:
        open_store(repo, BRANCH, Ticker()).trees()
    assert not isinstance(raised.value, NotInitialised)


def test_checkout_init_creates_and_stages(tmp_path: Path) -> None:
    repo = seeded(bare_remote(tmp_path), "work")
    init_store(repo, CHECKOUT)
    assert all((repo / path).is_file() for path in KEPT)
    assert git(repo, "diff", "--cached", "--name-only").splitlines() == KEPT
    assert data_root(repo, CHECKOUT) == repo / "lodge"
    with pytest.raises(LodgeError, match="already initialised"):
        init_store(repo, CHECKOUT)


def test_branch_init_pushes_orphan(tmp_path: Path) -> None:
    remote = bare_remote(tmp_path)
    repo = seeded(remote, "work")
    init_store(repo, BRANCH)
    assert git(remote, "rev-list", "--parents", "lodge").count(" ") == 0
    assert git(remote, "ls-tree", "-r", "--name-only", "lodge").splitlines() == KEPT
    assert git(repo, "rev-parse", "refs/remotes/origin/lodge") == git(remote, "rev-parse", "lodge")
    assert git(repo, "status", "--porcelain") == "" and not (repo / "lodge").exists()
    assert data_root(repo, BRANCH) is None
    with pytest.raises(LodgeError, match="already initialised"):
        init_store(repo, BRANCH)
    with pytest.raises(LodgeError, match="already initialised"):
        init_store(clone(remote, "other"), BRANCH)


def test_branch_init_without_remote_is_lodge_error(tmp_path: Path) -> None:
    repo = tmp_path / "solo"
    git(tmp_path, "init", "-b", "main", str(repo))
    with pytest.raises(LodgeError):
        init_store(repo, BRANCH)


def test_lock_waits_then_reports_path(tmp_path: Path) -> None:
    repo, clock = initialised(bare_remote(tmp_path), "work")
    store = open_store(repo, BRANCH, clock, lock_wait_seconds=0.2)
    current, _ = store.trees()
    lock = Path(git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir")) / "lodge.lock"
    lock.write_text("held")
    started = time.monotonic()
    with pytest.raises(LodgeError, match=r"lodge\.lock") as raised:
        store.publish(current, {"lodge/attachments/d-aaaaaa/a.txt": "x"}, "m")
    assert time.monotonic() - started >= 0.2 and "another lodge" in str(raised.value)
    lock.unlink()
    assert store.publish(current, {"lodge/attachments/d-aaaaaa/a.txt": "x"}, "m") is (
        PublishOutcome.PUBLISHED
    )
    assert not lock.exists()


def test_stale_lock_is_reported_not_broken(tmp_path: Path) -> None:
    repo, clock = initialised(bare_remote(tmp_path), "work")
    store = open_store(repo, BRANCH, clock, lock_wait_seconds=0.2)
    current, _ = store.trees()
    lock = Path(git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir")) / "lodge.lock"
    lock.write_text("held")
    old = time.time() - 601
    os.utime(lock, (old, old))
    with pytest.raises(LodgeError, match="older than ten minutes") as raised:
        store.publish(current, {"lodge/attachments/d-aaaaaa/a.txt": "x"}, "m")
    assert "lodge.lock" in str(raised.value) and lock.exists()


def test_lock_is_released_when_the_work_fails(tmp_path: Path) -> None:
    repo, clock = initialised(bare_remote(tmp_path), "work")
    store = open_store(repo, BRANCH, clock)
    current, _ = store.trees()
    git(repo, "remote", "set-url", "origin", str(tmp_path / "gone.git"))
    with pytest.raises(LodgeError):
        store.publish(current, {"lodge/attachments/d-aaaaaa/a.txt": "x"}, "m")
    lock = Path(git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir")) / "lodge.lock"
    assert not lock.exists()
