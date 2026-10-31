"""The composition root: the one place that wires the adapters to the operations."""

import io
import secrets
import signal
import sys
from datetime import datetime
from pathlib import Path
from time import sleep

from lodge.app import Lodge, LodgeError
from lodge.cli import run
from lodge.gitstore import (
    ProjectSettings,
    data_root,
    holds_records,
    init_store,
    load_settings,
    open_store,
    repo_root,
    request_exit,
)
from lodge.hook import parse_hook_settings
from lodge.hook import run as run_hook
from lodge.viewer import serve


class _Clock:
    def now(self) -> datetime:
        return datetime.now().astimezone()

    def sleep(self, seconds: float) -> None:
        sleep(seconds)


class _Entropy:
    def entropy(self) -> bytes:
        return secrets.token_bytes(8)


def _settings(root: Path) -> ProjectSettings:
    """The settings of every command but the hook, which no defect in them may stop."""
    settings = load_settings(root)
    parse_hook_settings(settings.raw.get("hook", {}))
    return settings


def _make_lodge() -> Lodge:
    root = repo_root(Path.cwd())
    settings = _settings(root)
    clock = _Clock()
    return Lodge(open_store(root, settings.store, clock), clock, _Entropy(), settings.core)


def _init() -> str:
    root = repo_root(Path.cwd())
    return init_store(root, _settings(root).store)


def _view(port: int, allow_hosts: tuple[str, ...]) -> int:
    _make_lodge()
    return serve(_make_lodge, port, allow_hosts, secrets.token_urlsafe(32))


def _existing_folder(edited: Path) -> Path:
    """The nearest folder at or above a file that may not exist yet."""
    folder = edited.resolve().parent
    while not folder.is_dir():
        folder = folder.parent
    return folder


def _hook_context(edited: Path) -> tuple[Path, Path | None, tuple[str, ...]] | None:
    root = repo_root(_existing_folder(edited))
    settings = load_settings(root)
    if not holds_records(root, settings.store):
        return None
    return root, data_root(root, settings.store), parse_hook_settings(settings.raw.get("hook", {}))


def _hook() -> int:
    try:
        cwd: Path | None = Path.cwd()
    except OSError:
        cwd = None
    return run_hook(sys.stdin, sys.stdout, _hook_context, cwd)


def _exit_on_signals() -> None:
    """Turn SIGTERM and SIGHUP into `SystemExit`, so the lock and temporary files are released.

    The exit waits for a running git command to return.
    """
    for sent in (signal.SIGTERM, signal.SIGHUP):
        code = 128 + sent

        def leave(_number: int, _frame: object, code: int = code) -> None:
            request_exit(code)

        signal.signal(sent, leave)


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        _exit_on_signals()
    for stream in (sys.stdout, sys.stderr):
        if isinstance(stream, io.TextIOWrapper):
            stream.reconfigure(errors="replace")
    args = sys.argv[1:] if argv is None else argv
    try:
        return run(args, _make_lodge, _init, _view, _hook)
    except LodgeError as error:
        print(f"lodge: {error}", file=sys.stderr)
        return error.exit_code


if __name__ == "__main__":
    raise SystemExit(main())
