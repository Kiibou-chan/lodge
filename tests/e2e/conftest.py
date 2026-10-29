"""A project clone with a bare remote, and the command line run in-process in it."""

import os
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

import lodge.main
from gitstore.conftest import isolated_git  # noqa: F401
from gitstore.repos import bare_remote, git, seeded
from lodge.main import main


@dataclass(frozen=True)
class Result:
    code: int
    out: str
    err: str


class Project:
    """A seeded clone of a bare remote; `run` calls `main` from inside the clone."""

    def __init__(self, root: Path, remote: Path, capsys: pytest.CaptureFixture[str]) -> None:
        self.root = root
        self.remote = remote
        self._capsys = capsys
        self._drafts = root.parent / "drafts"

    def run(self, *argv: str, cwd: Path | None = None) -> Result:
        before = Path.cwd()
        os.chdir(cwd or self.root)
        try:
            code = main(list(argv))
        finally:
            os.chdir(before)
        captured = self._capsys.readouterr()
        return Result(code, captured.out, captured.err)

    def configure(self, text: str) -> None:
        (self.root / ".lodge.toml").write_text(text, encoding="utf-8")

    def draft(self, name: str, text: str) -> str:
        """A draft file outside the repository; its path."""
        self._drafts.mkdir(exist_ok=True)
        path = self._drafts / name
        path.write_text(text, encoding="utf-8")
        return str(path)

    def git(self, *args: str) -> str:
        return git(self.root, *args)

    def publish_main(self) -> None:
        """Commit everything staged and push `main`, so the records count as published."""
        self.git("commit", "-m", "Records")
        self.git("push", "origin", "main")


class MinuteClock:
    """Stands for `datetime` in `lodge.main`: each reading is a minute after the last."""

    at = datetime(2026, 10, 29, 9, 30, tzinfo=timezone(timedelta(hours=1)))

    @classmethod
    def now(cls) -> datetime:
        cls.at += timedelta(minutes=1)
        return cls.at


class StuckClock:
    """Stands for `datetime` and `sleep` in `lodge.main`: the same instant until slept on."""

    def __init__(self) -> None:
        self.at = datetime(2026, 10, 29, 9, 30, 0, 250_000, tzinfo=timezone(timedelta(hours=1)))
        self.slept: list[float] = []

    def now(self) -> datetime:
        return self.at

    def sleep(self, seconds: float) -> None:
        self.slept.append(seconds)
        self.at += timedelta(seconds=seconds)


@pytest.fixture
def stuck_clock(project: "Project", monkeypatch: pytest.MonkeyPatch) -> StuckClock:
    """The clock of the next commands stands still, as it does for a scripted chain of adds."""
    clock = StuckClock()
    monkeypatch.setattr(lodge.main, "datetime", clock)
    monkeypatch.setattr(lodge.main, "sleep", clock.sleep)
    return clock


@pytest.fixture
def project(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> Iterator[Project]:
    monkeypatch.setattr(lodge.main, "datetime", MinuteClock)
    remote = bare_remote(tmp_path)
    yield Project(seeded(remote, "work"), remote, capsys)
