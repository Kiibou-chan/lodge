"""The last tip of the shared branch that lodge accepted: a ref only lodge moves.

git's own fetch moves the remote-tracking ref, so only a ref of lodge's own can tell that the
branch was rewritten. Deleting it, with `git update-ref -d`, accepts the rewrite.
"""

from pathlib import Path

from lodge.gitstore.git import attempt, resolve

ACCEPTED = "refs/lodge/accepted"
ACKNOWLEDGE = f"git update-ref -d {ACCEPTED}"


def accept(root: Path, tip: str) -> None:
    """Move the accepted tip to `tip` when there is none or `tip` contains it; a failure is moot."""
    held = resolve(root, ACCEPTED)
    if held == tip:
        return
    if held is None:
        attempt(["update-ref", ACCEPTED, tip, ""], root)
    elif not _rewrites(root, held, tip):
        attempt(["update-ref", ACCEPTED, tip, held], root)


def rewritten(root: Path, tip: str) -> str | None:
    """The accepted tip when `tip` does not contain it, or git cannot say, so a rewrite stands."""
    held = resolve(root, ACCEPTED)
    return held if held is not None and held != tip and _rewrites(root, held, tip) else None


def _rewrites(root: Path, old: str, new: str) -> bool:
    return attempt(["merge-base", "--is-ancestor", old, new], root).returncode != 0
