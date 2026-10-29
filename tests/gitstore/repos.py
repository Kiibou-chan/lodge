"""Real repositories for the git store tests: a bare remote, clones of it, and worktrees."""

import subprocess
from collections.abc import Mapping
from datetime import datetime, timedelta
from pathlib import Path

from fakes import START

from lodge.app import PublishOutcome
from lodge.core import Tree
from lodge.gitstore import StoreSettings, init_store, open_store

BRANCH = StoreSettings(mode="branch")
CHECKOUT = StoreSettings()


def git(cwd: Path, *args: str, input: str | None = None) -> str:
    done = subprocess.run(
        ["git", "-C", str(cwd), *args],
        check=True,
        capture_output=True,
        text=True,
        errors="surrogateescape",
        input=input,
    )
    return done.stdout.strip()


def bare_remote(tmp_path: Path) -> Path:
    remote = tmp_path / "remote.git"
    subprocess.run(
        ["git", "init", "--bare", "-b", "main", str(remote)], check=True, capture_output=True
    )
    return remote


def clone(remote: Path, name: str) -> Path:
    target = remote.parent / name
    subprocess.run(["git", "clone", str(remote), str(target)], check=True, capture_output=True)
    return target


def seeded(remote: Path, name: str) -> Path:
    """A clone of `remote` whose `main` holds one commit, pushed."""
    target = clone(remote, name)
    commit(target, "README.md", "a made-up project\n", "Start")
    git(target, "push", "origin", "main")
    return target


def worktree(of: Path, name: str) -> Path:
    target = of.parent / name
    git(of, "worktree", "add", "--detach", str(target))
    return target


def commit(repo: Path, path: str, text: str, message: str) -> None:
    write(repo, path, text)
    git(repo, "add", "--", path)
    git(repo, "commit", "-m", message)


def write(repo: Path, path: str, text: str) -> None:
    target = repo / path
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(text, encoding="utf-8")


class Ticker:
    """A clock that stands still until it is advanced."""

    def __init__(self) -> None:
        self.at: datetime = START

    def now(self) -> datetime:
        return self.at

    def advance(self, seconds: float) -> None:
        self.at += timedelta(seconds=seconds)

    def sleep(self, seconds: float) -> None:
        self.advance(seconds)


def initialised(remote: Path, name: str, clock: Ticker | None = None) -> tuple[Path, Ticker]:
    """A seeded clone with the `lodge` branch created on the remote."""
    repo = seeded(remote, name)
    init_store(repo, BRANCH)
    return repo, clock or Ticker()


def publish_one(repo: Path, clock: Ticker, writes: Mapping[str, str], message: str = "m") -> Tree:
    """Read a branch-mode store, publish `writes`, and return the tree that was read."""
    store = open_store(repo, BRANCH, clock)
    current, _ = store.trees()
    assert store.publish(current, writes, message) is PublishOutcome.PUBLISHED
    return current


def checkout_project(tmp_path: Path) -> tuple[Path, Path]:
    """A remote, and a seeded clone of it with the checkout store initialised and committed."""
    remote = bare_remote(tmp_path)
    repo = seeded(remote, "work")
    init_store(repo, CHECKOUT)
    git(repo, "commit", "-m", "Initialise lodge")
    git(repo, "push", "origin", "main")
    return remote, repo
