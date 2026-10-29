"""The one place git is run: every call names the repository with `-C` and reads no terminal."""

import os
import subprocess
import threading
from collections.abc import Mapping, Sequence
from pathlib import Path

from lodge.app import LodgeError
from lodge.gitstore.errors import GitMissing

_FIXED_ENV = {"GIT_TERMINAL_PROMPT": "0", "LC_ALL": "C"}
Input = bytes | str | None
_running = threading.local()
_pending: int | None = None


def request_exit(code: int) -> None:
    """Exit with `code` now, or when the git command the main thread is running returns.

    Killing git in the middle of a write leaves its own lock files behind. Git commands in other
    threads (the viewer's requests) never hold the exit back, since only the main thread exits.
    """
    global _pending
    if getattr(_running, "count", 0):
        _pending = code
    else:
        raise SystemExit(code)


def attempt(
    args: Sequence[str], cwd: Path, env: Mapping[str, str] | None = None, input: Input = None
) -> "subprocess.CompletedProcess[bytes]":
    """`git <args>` in `cwd`, whatever its exit status; only a missing `git` is an error."""
    data = input.encode("utf-8", errors="surrogateescape") if isinstance(input, str) else input
    _running.count = getattr(_running, "count", 0) + 1
    try:
        done = subprocess.run(
            ["git", "-C", str(cwd), *args],
            check=False,
            capture_output=True,
            input=data,
            stdin=None if data is not None else subprocess.DEVNULL,
            env={**os.environ, **_FIXED_ENV, **(env or {})},
        )
    except FileNotFoundError as error:
        raise GitMissing("git is not installed or is not on the PATH") from error
    finally:
        _running.count -= 1
    if _pending is not None and threading.current_thread() is threading.main_thread():
        raise SystemExit(_pending)
    return done


def first_line(*streams: bytes) -> str:
    """The first non-empty line of the first stream that has one."""
    for stream in streams:
        for line in stream.decode("utf-8", errors="replace").splitlines():
            if line.strip():
                return line.strip()
    return ""


def run_bytes(
    args: Sequence[str], cwd: Path, env: Mapping[str, str] | None = None, input: Input = None
) -> bytes:
    """The output of `git <args>`; a failure is a `LodgeError` with git's first line of stderr."""
    done = attempt(args, cwd, env, input)
    if done.returncode != 0:
        raise LodgeError(first_line(done.stderr, done.stdout) or f"git {args[0]} failed")
    return done.stdout


def run(
    args: Sequence[str], cwd: Path, env: Mapping[str, str] | None = None, input: Input = None
) -> str:
    """The output of `git <args>` as text, without its final newline."""
    return run_bytes(args, cwd, env, input).decode("utf-8", errors="surrogateescape").rstrip("\n")


def resolve(cwd: Path, ref: str) -> str | None:
    """The commit that `ref` names, None when there is none."""
    done = attempt(["rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"], cwd)
    if done.returncode == 0:
        return done.stdout.decode().strip()
    if done.returncode == 1:
        return None
    raise LodgeError(first_line(done.stderr) or "git rev-parse failed")
