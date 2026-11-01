"""Scratch indexes and deterministic cross-process lock holders."""

import fcntl
import multiprocessing
from collections.abc import Iterator
from contextlib import contextmanager
from multiprocessing.connection import Connection
from pathlib import Path

from lodge.gitstore import open_index
from lodge.gitstore.index_db import IndexDB, build_digest

KEY = ("lodge/spec/berths/s-aaaaaa-berths.md", "a" * 40)


def opened(folder: Path) -> IndexDB:
    index = open_index(folder, "settings")
    assert isinstance(index, IndexDB)
    return index


def filename(folder: Path) -> Path:
    return folder / "lodge" / f"index-{build_digest()}.sqlite"


def lock_holder(path: Path, pipe: Connection) -> None:
    with path.open("rb") as lock:
        fcntl.flock(lock, fcntl.LOCK_SH)
        pipe.send(True)
        pipe.recv()
    pipe.close()


@contextmanager
def shared_elsewhere(path: Path) -> Iterator[None]:
    parent, child = multiprocessing.Pipe()
    process = multiprocessing.get_context("fork").Process(target=lock_holder, args=(path, child))
    process.start()
    assert parent.poll(5) and parent.recv()
    try:
        yield
    finally:
        parent.send(True)
        process.join(5)
        assert process.exitcode == 0
        parent.close()
        child.close()
