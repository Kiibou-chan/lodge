"""The store on a branch of its own: reads the remote-tracking ref, commits, pushes."""

from collections.abc import Mapping
from datetime import datetime
from pathlib import Path

from lodge.app import Clock, Gate, LodgeError, PublishOutcome
from lodge.core import Tree
from lodge.gitstore.accepted import ACCEPTED, ACKNOWLEDGE, accept, rewritten
from lodge.gitstore.errors import NOT_INITIALISED, NotInitialised
from lodge.gitstore.git import attempt, first_line, resolve, run
from lodge.gitstore.lock import LockHeld, locked
from lodge.gitstore.plumbing import check_writes, commit_files, push, remote_tip
from lodge.gitstore.settings import StoreSettings
from lodge.gitstore.trees import KEPT, read_tree

GATE_NOTE = "in branch mode the gate runs inside lodge add; a push to the branch by hand skips it"


class BranchStore:
    def __init__(
        self,
        root: Path,
        settings: StoreSettings,
        clock: Clock,
        common_dir: Path,
        lock_wait_seconds: float,
    ) -> None:
        self._root = root
        self._s = settings
        self._clock = clock
        self._common = common_dir
        self._wait = lock_wait_seconds
        self._ref = f"refs/remotes/{settings.remote}/{settings.branch}"
        self._stamp = common_dir / "lodge-fetched"
        self._stale = False
        self._failure: str | None = None
        self._held: LockHeld | None = None
        self._rev: str | None = None

    def trees(self) -> tuple[Tree, Tree]:
        """The branch's tree, twice; fetched first when the last fetch is old or the store stale.

        When another lodge holds the lock for longer than the wait, the cached tip is served.
        """
        held: LockHeld | None = None
        if self._needs_fetch():
            try:
                with locked(self._common, self._wait):
                    if self._needs_fetch():
                        self._fetch()
            except LockHeld as error:
                held = error
        tip = resolve(self._root, self._ref)
        if tip is None:
            raise held or self._missing()
        self._held = held
        self._rev = tip
        kept = rewritten(self._root, tip)
        accept(self._root, tip)
        tree = read_tree(self._root, tip)
        return tree, tree if kept is None else read_tree(self._root, kept)

    def freshness(self) -> str | None:
        rev = self._rev or resolve(self._root, self._ref)
        line = self._age_line(rev)
        if rev is None or line is None or rewritten(self._root, rev) is None:
            return line
        return (
            f"{line}\nthe {self._s.branch} branch was rewritten since lodge last accepted it; "
            f"the accepted tip is at {ACCEPTED}; run lodge check --gate; tell the author; "
            f"only the author accepts a rewrite, with {ACKNOWLEDGE}"
        )

    def _age_line(self, rev: str | None) -> str | None:
        fetched = self._fetched_at()
        when = fetched.isoformat(timespec="seconds") if fetched else "unknown"
        if self._held is not None:
            path = self._held.path
            if self._held.left_over:
                reason = (
                    f"{path} is older than ten minutes and may be left over; "
                    "delete it if no lodge is running"
                )
            else:
                reason = f"another lodge holds {path}"
            return f"not fetched: {reason}; data as of {when}"
        if self._failure is not None:
            return f"fetch failed; data as of {when}"
        if rev is None:
            return None
        if fetched is None:
            return f"{self._s.branch}@{rev[:7]}, never fetched"
        seconds = max(0, int((self._clock.now() - fetched).total_seconds()))
        return f"{self._s.branch}@{rev[:7]}, fetched {seconds} s ago"

    def gate(self, current: Tree) -> Gate:
        """The branch against itself, or against the accepted tip while a rewrite stands."""
        kept = None if current.rev is None else rewritten(self._root, current.rev)
        published = current if kept is None else read_tree(self._root, kept)
        return Gate(published, (("", current),), (GATE_NOTE,))

    def publish(self, base: Tree, writes: Mapping[str, str], message: str) -> PublishOutcome:
        """Commit `writes` on `base` and push; REJECTED when the branch is no longer at `base`."""
        check_writes(base, writes)
        with locked(self._common, self._wait):
            tip = resolve(self._root, self._ref)
            if tip is None or tip != base.rev:
                return PublishOutcome.REJECTED
            commit = commit_files(self._root, tip, writes, message, self._s)
            if not push(self._root, self._s, commit, tip):
                self._stale = True
                return PublishOutcome.REJECTED
            attempt(["update-ref", self._ref, commit, tip], self._root)
            accept(self._root, commit)
        return PublishOutcome.PUBLISHED

    def _needs_fetch(self) -> bool:
        fetched = self._fetched_at()
        if self._stale or fetched is None:
            return True
        age = (self._clock.now() - fetched).total_seconds()
        return age < 0 or age >= self._s.max_staleness_seconds

    def _fetched_at(self) -> datetime | None:
        try:
            ref, _, when = self._stamp.read_text(encoding="utf-8").strip().partition(" ")
            at = datetime.fromisoformat(when)
        except (OSError, ValueError):
            return None
        if ref != self._ref:
            return None
        return at if at.tzinfo is not None else None

    def _fetch(self) -> None:
        s = self._s
        refspec = f"+refs/heads/{s.branch}:{self._ref}"
        done = attempt(["fetch", "--quiet", "--no-tags", s.remote, refspec], self._root)
        if done.returncode == 0:
            self._write_stamp()
            self._stale = False
            self._failure = None
        else:
            self._failure = first_line(done.stderr) or "git fetch failed"

    def _write_stamp(self) -> None:
        text = f"{self._ref} {self._clock.now().isoformat()}"
        try:
            self._stamp.write_text(text, encoding="utf-8")
        except OSError as error:
            raise LodgeError(f"cannot write {self._stamp}: {error.strerror}") from error

    def _missing(self) -> LodgeError:
        failure = self._failure
        if failure is None or "couldn't find remote ref" in failure:
            return NotInitialised(NOT_INITIALISED)
        return LodgeError(f"cannot fetch {self._s.remote}/{self._s.branch}: {failure}")


def init_branch(root: Path, settings: StoreSettings, common_dir: Path, wait: float) -> str:
    """The branch as a parentless commit holding the empty store, pushed to the remote."""
    s = settings
    with locked(common_dir, wait):
        if remote_tip(root, s) is not None:
            raise LodgeError(f"lodge is already initialised: {s.remote} has a branch {s.branch}")
        commit = commit_files(root, None, dict.fromkeys(KEPT, ""), "lodge: initialise", s)
        if not push(root, s, commit, None):
            raise LodgeError(f"lodge is already initialised: {s.remote} has a branch {s.branch}")
        run(["update-ref", f"refs/remotes/{s.remote}/{s.branch}", commit], root)
        accept(root, commit)
    return f"created the branch {s.branch} on {s.remote}"
