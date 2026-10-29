"""A signal exit waits for git only when the thread that handles signals is the one running it."""

import subprocess
import threading
from pathlib import Path

import pytest

from lodge.gitstore import git as git_module
from lodge.gitstore.git import attempt, request_exit


def test_git_in_another_thread_does_not_defer_the_exit(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(git_module, "_pending", None)
    started, release = threading.Event(), threading.Event()
    real = subprocess.run

    def slow(*args: object, **kwargs: object) -> "subprocess.CompletedProcess[bytes]":
        started.set()
        release.wait(10)
        return real(*args, **kwargs)  # type: ignore[call-overload,no-any-return]

    monkeypatch.setattr(subprocess, "run", slow)
    worker = threading.Thread(target=lambda: attempt(["--version"], tmp_path))
    worker.start()
    try:
        assert started.wait(10)
        with pytest.raises(SystemExit) as raised:
            request_exit(143)
        assert raised.value.code == 143
    finally:
        release.set()
        worker.join()


def test_git_in_the_main_thread_defers_the_exit_until_it_returns(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(git_module, "_pending", None)
    real = subprocess.run

    def signalled(*args: object, **kwargs: object) -> "subprocess.CompletedProcess[bytes]":
        request_exit(129)
        return real(*args, **kwargs)  # type: ignore[call-overload,no-any-return]

    monkeypatch.setattr(subprocess, "run", signalled)
    with pytest.raises(SystemExit) as raised:
        attempt(["--version"], tmp_path)
    assert raised.value.code == 129
