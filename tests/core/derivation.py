"""Snapshots for the tests of `derive`, read from files so that no defect is built in."""

from builders import files_of

from lodge.core import Area, Imported, Record, Snapshot, Tree, load

IMPORTED = Imported("notes.md", "A heading")


def snapshot_of(*records: Record | Area) -> Snapshot:
    snap = load(Tree(None, files_of(*records), frozenset()))
    assert snap.problems == ()
    return snap
