"""Actual process death and pipe signals cannot publish a partial state."""

import multiprocessing
import os
import signal
import sqlite3
import sys
from multiprocessing.connection import Connection
from pathlib import Path

import pytest
from builders import decision
from fakes import CountingIds, FixedClock, MemoryStore

from gitstore.index_helpers import KEY, filename, opened
from gitstore.state_helpers import FACT, changed_rows, keep
from lodge.app import Lodge
from lodge.cli import run
from lodge.core import CoreSettings
from lodge.gitstore.index_space import clear


def killed_keep(folder: Path, pipe: Connection) -> None:
    index = opened(folder)
    original = index.db

    class StopAfterBucket(sqlite3.Connection):
        buckets = 0

        def execute(self, sql: str, parameters: object = (), /) -> sqlite3.Cursor:
            cursor = super().execute(sql, parameters)  # type: ignore[arg-type]
            if sql.startswith("INSERT INTO buckets"):
                self.buckets += 1
                if self.buckets == 1024:
                    pipe.send("bucket")
                    pipe.recv()
            return cursor

    index.db = sqlite3.connect(filename(folder), isolation_level=None, factory=StopAfterBucket)
    original.close()
    keep(index, "killed", changed_rows())


def test_killed_during_keep_leaves_no_state(tmp_path: Path) -> None:
    index = opened(tmp_path)
    keep(index)
    parent, child = multiprocessing.Pipe()
    process = multiprocessing.get_context("fork").Process(
        target=killed_keep, args=(tmp_path, child)
    )
    process.start()
    try:
        assert parent.poll(5) and parent.recv() == "bucket"
        assert process.pid is not None
        os.kill(process.pid, signal.SIGKILL)
        process.join(5)
        assert process.exitcode == -signal.SIGKILL
        assert index.state("killed") is None and index.state("one")
        assert index.all_rows("killed") == {}
    finally:
        if process.is_alive():
            process.kill()
            process.join(5)
        parent.close()
        child.close()
        index.close()


def broken_pipe(folder: Path, disposition: int) -> None:

    index = opened(folder)
    lodge = Lodge(
        MemoryStore(decision(id="d-aaaaaa")), FixedClock(), CountingIds(), CoreSettings(), index
    )
    # First sighting has no state. A second sighting will attempt a keep only after output.
    lodge.show_many(["d-aaaaaa"])
    read_fd, write_fd = os.pipe()
    os.close(read_fd)
    sys.stdout = os.fdopen(write_fd, "w", buffering=1)
    signal.signal(signal.SIGPIPE, disposition)
    try:
        run(["show", "d-aaaaaa"], lambda: lodge, lambda: "", lambda *_: 0, lambda: 0)
    except BrokenPipeError:
        os._exit(23)
    os._exit(0)


@pytest.mark.parametrize("disposition", [signal.SIG_DFL, signal.SIG_IGN])
def test_output_failure_with_real_broken_pipe(tmp_path: Path, disposition: int) -> None:
    index = opened(tmp_path)
    process = multiprocessing.get_context("fork").Process(
        target=broken_pipe, args=(tmp_path, disposition)
    )
    process.start()
    process.join(5)
    try:
        assert process.exitcode == (-signal.SIGPIPE if disposition == signal.SIG_DFL else 23)
        assert index.db.execute("SELECT count(*) FROM states").fetchone()[0] == 0
    finally:
        if process.is_alive():
            process.kill()
            process.join(5)
        index.close()


def clear_in_process(folder: Path) -> None:

    index = opened(folder)
    index.db.execute("BEGIN IMMEDIATE")
    clear(index.db)
    index.db.execute("COMMIT")
    index.close()


def test_keep_after_a_process_clear(tmp_path: Path) -> None:

    a = opened(tmp_path)
    keep(a)
    epoch, parses, facts = a.epoch(), a.parses([KEY]), a.facts("published")
    process = multiprocessing.get_context("fork").Process(target=clear_in_process, args=(tmp_path,))
    process.start()
    process.join(5)
    assert process.exitcode == 0
    assert facts is not None
    keep(a, "after", parses=parses, facts={"published": facts}, misses=(), epoch=epoch)
    assert a.state("after") and a.parses([KEY]) == parses and a.facts("published") == FACT
    a.close()
