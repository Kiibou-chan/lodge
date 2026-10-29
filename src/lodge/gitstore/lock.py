"""The lock beside the git common directory that keeps two lodge processes apart."""

import os
import time
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from lodge.app import LodgeError

_STALE_AFTER_SECONDS = 600
_POLL_SECONDS = 0.1


class LockHeld(LodgeError):
    """The lock is held by another lodge, or left over by one that was killed."""

    def __init__(self, path: Path, message: str, left_over: bool = False) -> None:
        super().__init__(message)
        self.path = path
        self.left_over = left_over


@contextmanager
def locked(common_dir: Path, wait_seconds: float) -> Iterator[None]:
    """Hold `lodge.lock` for the block; a lock held longer than `wait_seconds` is an error."""
    path = common_dir / "lodge.lock"
    deadline = time.monotonic() + wait_seconds
    while True:
        try:
            handle = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
            break
        except FileExistsError:
            _refuse_stale(path)
            if time.monotonic() >= deadline:
                raise LockHeld(
                    path,
                    f"another lodge is working in this repository; gave up after "
                    f"{wait_seconds:g} s waiting for {path}",
                ) from None
            time.sleep(_POLL_SECONDS)
        except OSError as error:
            raise LodgeError(f"cannot create the lock {path}: {error.strerror}") from error
    try:
        os.write(handle, f"{os.getpid()}\n".encode())
        os.close(handle)
        yield
    finally:
        path.unlink(missing_ok=True)


def _refuse_stale(path: Path) -> None:
    try:
        age = time.time() - path.stat().st_mtime
    except FileNotFoundError:
        return
    if age > _STALE_AFTER_SECONDS:
        raise LockHeld(
            path,
            f"the lock {path} is older than ten minutes, so it may be left over; "
            "delete it if no lodge is running",
            left_over=True,
        )
