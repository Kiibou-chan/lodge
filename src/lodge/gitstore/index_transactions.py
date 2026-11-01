"""Explicit transactions that let a multi-lookup read retain its WAL snapshot."""

import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager


@contextmanager
def transaction(db: sqlite3.Connection, *, write: bool = False) -> Iterator[None]:
    if db.in_transaction and not write:
        yield
        return
    try:
        db.execute("BEGIN IMMEDIATE" if write else "BEGIN")
        yield
        db.execute("COMMIT")
    finally:
        if db.in_transaction:
            db.execute("ROLLBACK")
