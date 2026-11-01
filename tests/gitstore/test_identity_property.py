"""Seeded edit sequences compare the fast listing with exact byte-derived trees."""

import os
import shutil
from pathlib import Path
from random import Random

from gitstore.repos import git, write
from gitstore.test_identity import RECORD, agrees, prepared
from lodge.core import Tree


def test_random_edits_agree(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)
    paths = [RECORD, *(f"lodge/decisions/record-{n:02d}.md" for n in range(39))]
    for n, path in enumerate(paths):
        write(repo, path, f"Berth {n}.\n")
    git(repo, "add", "--", "lodge")
    git(repo, "commit", "-m", "Forty made-up records")
    rng = Random(808)
    operations = (
        "create",
        "edit",
        "delete",
        "untracked",
        "touch",
        "stage",
        "unstage",
        "revert",
        "commit",
        "assume",
        "skip",
        "crlf",
        "folder",
    )
    used: set[str] = set()
    seen: dict[str, tuple[dict[str, str], frozenset[str]]] = {}

    def remember(ident: str, exact: Tree) -> None:
        value = (dict(exact.files), exact.attachments)
        assert seen.setdefault(ident, value) == value

    listing = agrees(store)
    remember(listing.ident, store.trees()[0])
    for sequence in range(200):
        # Remove the source only after eliminating staged CRLF/index-LF histories.
        for path in paths:
            target = repo / path
            if target.is_file():
                raw = target.read_bytes()
                if b"\r\n" in raw:
                    target.write_bytes(raw.replace(b"\r\n", b"\n"))
        (repo / ".gitattributes").unlink(missing_ok=True)
        tracked = list(filter(None, git(repo, "ls-files", "-z", "--", "lodge").split("\0")))
        for flag in ("--no-assume-unchanged", "--no-skip-worktree"):
            git(repo, "update-index", flag, "--", *tracked)
        for step in range(rng.randint(1, 8)):
            operation = rng.choice(operations)
            used.add(operation)
            path = rng.choice(paths)
            target = repo / path
            is_tracked = path in git(repo, "ls-files", "-z", "--", path).split("\0")
            if operation in {"create", "edit", "assume", "crlf", "folder"} and target.is_dir():
                shutil.rmtree(target)
            if operation in {"create", "edit", "assume", "crlf"}:
                if operation == "assume" and is_tracked:
                    git(repo, "update-index", "--assume-unchanged", "--", path)
                write(repo, path, f"Berth {sequence} crane {step}.\n")
                if operation == "crlf":
                    write(repo, ".gitattributes", "*.md text eol=crlf\n")
                    target.write_bytes(target.read_bytes().replace(b"\n", b"\r\n"))
            elif operation == "untracked":
                write(repo, f"lodge/new-{sequence}/untracked-{step}.md", "Untracked berth.\n")
            elif operation in {"delete", "skip"}:
                if operation == "skip" and is_tracked:
                    git(repo, "update-index", "--skip-worktree", "--", path)
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink(missing_ok=True)
            elif operation == "touch" and target.is_file():
                os.utime(target, None)
            elif operation in {"stage", "unstage", "revert"} and is_tracked:
                for flag in ("--no-assume-unchanged", "--no-skip-worktree"):
                    git(repo, "update-index", flag, "--", path)
                if operation == "stage":
                    git(repo, "add", "-A", "--", path)
                elif operation == "unstage":
                    git(repo, "reset", "HEAD", "--", path)
                elif (
                    path
                    in git(repo, "ls-tree", "-r", "--name-only", "HEAD", "--", path).splitlines()
                ):
                    if target.is_dir():
                        shutil.rmtree(target)
                    git(repo, "checkout", "HEAD", "--", path)
            elif operation == "commit":
                git(repo, "commit", "--allow-empty", "-m", "Seeded sequence")
            elif operation == "folder":
                target.unlink(missing_ok=True)
                write(repo, f"{path}/new.md", "A folder replaced a record.\n")
        listing = agrees(store)
        exact, published = store.trees()
        remember(listing.ident, exact)
        remember(store.listings()[1].ident, published)
    assert used == set(operations)
