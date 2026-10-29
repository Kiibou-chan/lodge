"""Committing and pushing without touching the working tree, the index, or a checked-out branch."""

import tempfile
from collections.abc import Mapping
from pathlib import Path

from lodge.app import LodgeError
from lodge.core import Tree
from lodge.gitstore.git import attempt, first_line, run
from lodge.gitstore.settings import StoreSettings
from lodge.gitstore.trees import encode


def check_writes(base: Tree, writes: Mapping[str, str]) -> None:
    """Refuse a path outside `lodge/` and an attachment that exists.

    A path is outside when it has an empty, `.`, `..`, or `.git` part.
    """
    for path in writes:
        parts = path.split("/")
        inside = parts[0] == "lodge" and len(parts) > 1 and "\\" not in path and "\0" not in path
        if not inside or any(part in {"", ".", "..", ".git"} for part in parts):
            raise LodgeError(f"{path} is outside lodge/, which is all the store writes")
        if path in base.attachments:
            raise LodgeError(f"{path} is an attachment, and lodge never overwrites an attachment")


def commit_files(
    root: Path,
    parent: str | None,
    writes: Mapping[str, str],
    message: str,
    settings: StoreSettings,
) -> str:
    """A commit of `parent`'s tree with `writes` on top, made in a temporary index."""
    with tempfile.TemporaryDirectory() as folder:
        env = {"GIT_INDEX_FILE": str(Path(folder) / "index")}
        if parent is not None:
            run(["read-tree", parent], root, env)
        for path, text in writes.items():
            blob = run(["hash-object", "-w", "--stdin"], root, env, input=encode(text))
            run(["update-index", "--add", "--cacheinfo", f"100644,{blob},{path}"], root, env)
        tree = run(["write-tree"], root, env)
    body = message.rstrip()
    if settings.commit_trailer:
        body = f"{body}\n\n{settings.commit_trailer}"
    parents = ["-p", parent] if parent is not None else []
    return run(["commit-tree", tree, *parents, "-F", "-"], root, input=body + "\n")


def remote_tip(root: Path, settings: StoreSettings) -> str | None:
    """Where the remote's branch is now, None when it has none."""
    target = f"refs/heads/{settings.branch}"
    out = run(["ls-remote", settings.remote, target], root)
    for line in out.splitlines():
        sha, _, ref = line.partition("\t")
        if ref == target:
            return sha
    return None


def push(root: Path, settings: StoreSettings, commit: str, parent: str | None) -> bool:
    """Push `commit` on top of `parent` without force; False when the branch moved on.

    Whatever the reason for a failed push, the remote is asked where the branch is, since the
    wording of a refusal differs between hosts, a lost race has its own, and a push can land with
    its report lost: the branch at `commit`, or at a commit built on it, is a push that succeeded.
    """
    target = f"refs/heads/{settings.branch}"
    done = attempt(["push", "--porcelain", settings.remote, f"{commit}:{target}"], root)
    if done.returncode == 0:
        return True
    failure = first_line(done.stderr, done.stdout) or "git push failed"
    try:
        tip = remote_tip(root, settings)
    except LodgeError:
        raise LodgeError(failure) from None
    if tip == commit:
        return True
    if tip != parent:
        return tip is not None and _landed_below(root, settings, commit)
    raise LodgeError(failure)


def _landed_below(root: Path, settings: StoreSettings, commit: str) -> bool:
    """True when the remote's branch, fetched, contains `commit`."""
    fetched = attempt(
        ["fetch", "--quiet", "--no-tags", settings.remote, f"refs/heads/{settings.branch}"], root
    )
    if fetched.returncode != 0:
        return False
    return attempt(["merge-base", "--is-ancestor", commit, "FETCH_HEAD"], root).returncode == 0
