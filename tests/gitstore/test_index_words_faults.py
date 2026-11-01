"""A failed words write rolls back the parse unit and the state's completeness marker."""

import sqlite3
from pathlib import Path
from unittest.mock import patch

from builders import decision
from fake_index import MemoryIndex
from fakes import MemoryStore
from indexed_support import app, printed, seed

from gitstore.index_helpers import filename, opened
from gitstore.test_index_failures import Interrupted
from lodge.gitstore.index_db import IndexDB
from lodge.gitstore.index_space import clear


def test_keep_state_interrupted_leaves_no_searchable_state(tmp_path: Path) -> None:
    initial = opened(tmp_path)
    initial.close()
    db = sqlite3.connect(filename(tmp_path), isolation_level=None, factory=Interrupted)
    db.execute("PRAGMA journal_mode=WAL")
    index = IndexDB(db, None)
    store = MemoryStore(decision(id="d-aaaaaa", title="Uniquequay"))
    fake = MemoryIndex()
    with patch.object(fake, "keep_state", wraps=fake.keep_state) as capture:
        key = seed(store, fake)
    args, kwargs = capture.call_args
    db.count = 0
    index.keep_state(*args, **kwargs)
    count = db.count
    assert index.candidates(["uniquequay"], False)
    expected = printed(app(store), ["search", "uniquequay"])
    for after in range(1, count + 1):
        db.after = 0
        db.execute("BEGIN IMMEDIATE")
        clear(db)
        db.execute("COMMIT")
        # The build predates the clear, requiring every used unit to be written again.
        db.count, db.after = 0, after
        index.keep_state(*args, **kwargs)
        db.after = 0
        assert not db.in_transaction, after
        assert index.state(key) is None, after
        assert index.parses(list(args[5])) == {}, after
        assert index.candidates(["uniquequay"], False) == {}, after
        assert printed(app(store, index), ["search", "uniquequay"]) == expected, after
    index.close()


def test_locked_word_write_keeps_no_state(tmp_path: Path) -> None:
    writer, locker = opened(tmp_path), opened(tmp_path)
    store = MemoryStore(decision(id="d-aaaaaa", title="Uniquequay"))
    fake = MemoryIndex()
    with patch.object(fake, "keep_state", wraps=fake.keep_state) as capture:
        key = seed(store, fake)
    args, kwargs = capture.call_args
    locker.db.execute("BEGIN IMMEDIATE")
    try:
        writer.keep_state(*args, **kwargs)
        assert writer.state(key) is None
        assert writer.parses(list(args[5])) == {}
        assert writer.candidates(["uniquequay"], False) == {}
        assert printed(app(store, writer), ["search", "uniquequay"]) == printed(
            app(store), ["search", "uniquequay"]
        )
    finally:
        locker.db.execute("ROLLBACK")
        writer.close()
        locker.close()
