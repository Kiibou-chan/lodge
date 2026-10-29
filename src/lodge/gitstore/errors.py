"""The environment errors of the git store, each reported as one sentence."""

from lodge.app import LodgeError

NOT_INITIALISED = "lodge has no data in this repository yet; run `lodge init`"


class NotARepository(LodgeError):
    """The working directory is not inside a git repository."""


class NotInitialised(LodgeError):
    """The store has no data yet; `lodge init` creates it."""


class GitMissing(LodgeError):
    """The `git` program cannot be run."""
