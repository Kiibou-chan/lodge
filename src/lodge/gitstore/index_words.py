"""Immutable FTS5 words and candidates sharing parse rowids."""

import sqlite3
from collections.abc import Collection

from lodge.app import FileKey
from lodge.core import Parsed, parse_words


def create_words(db: sqlite3.Connection) -> None:
    try:
        db.execute(
            "CREATE VIRTUAL TABLE IF NOT EXISTS words USING "
            "fts5(title, statement, tokenize='ascii')"
        )
    except sqlite3.OperationalError as error:
        # An absent optional module is safe; any other failure rolls back the writer.
        if str(error) != "no such module: fts5":
            raise


def has_words(db: sqlite3.Connection) -> bool:
    return db.execute("SELECT 1 FROM sqlite_master WHERE name='words'").fetchone() is not None


def insert_words(db: sqlite3.Connection, rowid: int, parsed: Parsed | None) -> None:
    db.execute(
        "INSERT INTO words(rowid,title,statement) VALUES(?,?,?)", (rowid, *parse_words(parsed))
    )


def find_candidates(
    db: sqlite3.Connection, words: Collection[str], every: bool
) -> dict[FileKey, tuple[frozenset[str], frozenset[str]]] | None:
    if not has_words(db):
        return None
    if not words:
        return {}
    quoted = ['"' + word.replace('"', '""') + '"' for word in sorted(set(words))]
    query = "{title statement}: (" + (" AND " if every else " OR ").join(quoted) + ")"
    return {
        (path, blob): (frozenset(title.split()), frozenset(statement.split()))
        for path, blob, title, statement in db.execute(
            "SELECT p.path,p.blob,w.title,w.statement FROM words w "
            "JOIN parses p ON p.rowid=w.rowid WHERE words MATCH ?",
            (query,),
        )
    }
