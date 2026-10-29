"""The states a checkout's gate compares: the published one, and the one that would go out."""

from dataclasses import dataclass
from pathlib import Path

from lodge.app import Gate
from lodge.core import Tree
from lodge.gitstore.git import attempt, resolve
from lodge.gitstore.settings import StoreSettings
from lodge.gitstore.trees import read_tree

UNCOMMITTED = "uncommitted record changes in lodge/; commit them before you push"


@dataclass(frozen=True)
class Published:
    """The merge base of `HEAD` with the base branch; `missing` says why there is none to read.

    With no history, an unborn `HEAD`, the tree is empty and nothing is missing.
    """

    tree: Tree
    missing: str | None = None


def published_state(root: Path, s: StoreSettings) -> Published:
    if resolve(root, "HEAD") is None:
        return Published(Tree(None, {}))
    tried = f"{s.remote}/{s.base}"
    base = resolve(root, f"refs/remotes/{tried}") or resolve(root, f"refs/heads/{s.base}")
    merged = None if base is None else attempt(["merge-base", "HEAD", base], root)
    if merged is None or merged.returncode != 0 or not merged.stdout.strip():
        return Published(Tree(None, {}), _not_found(tried, s.base))
    return Published(read_tree(root, merged.stdout.decode().strip()))


def committed_gate(root: Path, current: Tree, published: Tree) -> Gate:
    """`published` against `HEAD`'s tree and the working tree, or against `current` if the same."""
    head = resolve(root, "HEAD")
    committed = Tree(None, {}) if head is None else read_tree(root, head)
    if (committed.files, committed.attachments) == (current.files, current.attachments):
        return Gate(published, (("", current),))
    states = (("committed", committed), ("working tree", current))
    return Gate(published, states, (UNCOMMITTED,))


def _not_found(tried: str, base: str) -> str:
    return (
        f"the published state cannot be found: {tried} and {base} were tried, and neither "
        f"exists here or shares history with HEAD; set base in .lodge.toml to your trunk "
        f"branch, or fetch it"
    )
