"""The schema for one source and dependency build's disposable index."""

import sqlite3

from lodge.gitstore.index_words import create_words


def create(db: sqlite3.Connection) -> None:
    db.execute(
        "CREATE TABLE IF NOT EXISTS meta(epoch INTEGER NOT NULL, kept INTEGER NOT NULL, "
        "written INTEGER NOT NULL)"
    )
    db.execute("INSERT INTO meta SELECT 1,0,0 WHERE NOT EXISTS (SELECT 1 FROM meta)")
    db.execute(
        "CREATE TABLE IF NOT EXISTS parses(rowid INTEGER PRIMARY KEY, "
        "path TEXT NOT NULL, blob TEXT NOT NULL, value BLOB NOT NULL, "
        "UNIQUE(path,blob))"
    )
    db.execute(
        "CREATE TABLE IF NOT EXISTS states(key TEXT PRIMARY KEY, at INTEGER NOT NULL, "
        "value BLOB NOT NULL)"
    )
    db.execute(
        "CREATE TABLE IF NOT EXISTS buckets(key TEXT NOT NULL, name TEXT NOT NULL, "
        "hash TEXT NOT NULL, PRIMARY KEY(key,name)) WITHOUT ROWID"
    )
    db.execute(
        "CREATE TABLE IF NOT EXISTS bucket_blobs(hash TEXT PRIMARY KEY, "
        "value BLOB NOT NULL) WITHOUT ROWID"
    )
    db.execute(
        "CREATE TABLE IF NOT EXISTS answers(key TEXT NOT NULL, name TEXT NOT NULL, "
        "value BLOB NOT NULL, PRIMARY KEY(key,name))"
    )
    db.execute(
        "CREATE TABLE IF NOT EXISTS citers(key TEXT NOT NULL, name TEXT NOT NULL, "
        "value BLOB NOT NULL, PRIMARY KEY(key,name))"
    )
    db.execute("CREATE TABLE IF NOT EXISTS facts(ident TEXT PRIMARY KEY, value BLOB NOT NULL)")
    db.execute("CREATE TABLE IF NOT EXISTS seen(key TEXT PRIMARY KEY, at INTEGER NOT NULL)")
    create_words(db)

    db.execute(
        "CREATE TABLE IF NOT EXISTS folders(root TEXT NOT NULL, path TEXT NOT NULL, "
        "ino INTEGER NOT NULL, "
        "mtime_ns INTEGER NOT NULL, ctime_ns INTEGER NOT NULL, listed_at_ns INTEGER NOT NULL, "
        "base TEXT NOT NULL, added TEXT NOT NULL, removed TEXT NOT NULL, PRIMARY KEY(root,path))"
    )
    db.execute(
        "CREATE TABLE IF NOT EXISTS folder_roots(root TEXT PRIMARY KEY, "
        "folder_count INTEGER NOT NULL)"
    )
