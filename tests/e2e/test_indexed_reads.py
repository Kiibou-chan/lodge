"""The stored model follows checkout edits, commits, branch tips, and viewer wiring."""

import os
from collections.abc import Callable
from pathlib import Path

import pytest
from builders import decision, files_of

from e2e.conftest import Project
from gitstore.repos import BRANCH, Ticker, clone, git, publish_one
from lodge import main
from lodge.app import Lodge
from lodge.gitstore import open_store
from lodge.gitstore.index_db import IndexDB, open_index


def prepared(project: Project) -> Path:
    project.run("init")
    files = files_of(decision(id="d-aaaaaa", code="A", title="Synthetic berth"))
    for name, text in files.items():
        target = project.root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)
    project.git("add", "lodge")
    project.publish_main()
    for _ in range(3):
        assert project.run("show", "A").code == 0
    return next(project.root.glob("lodge/decisions/*.md"))


def test_edit_on_disk_then_show_sees_it(project: Project) -> None:
    path = prepared(project)
    path.write_text(path.read_text().replace("Synthetic berth", "Edited berth"))
    for _ in range(3):
        result = project.run("show", "A")
        assert result.code == 0 and "Edited berth" in result.out

    index = open_index(project.root / ".git")
    assert isinstance(index, IndexDB)
    assert index.db.execute("SELECT count(*) FROM states").fetchone()[0] == 2
    index.close()


def test_commit_then_show_sees_it(project: Project) -> None:
    path = prepared(project)
    path.write_text(path.read_text().replace("Synthetic berth", "Committed berth"))
    project.git("add", "lodge")
    project.git("commit", "-m", "Synthetic edit")
    result = project.run("show", "A")
    assert result.code == 0 and "Committed berth" in result.out
    assert result.out == project.run("show", "A").out == project.run("show", "A").out


def test_branch_mode_after_fetch_sees_the_new_tip(project: Project) -> None:
    project.configure('[store]\nmode = "branch"\n')
    project.run("init")
    clock = Ticker()
    files = files_of(decision(id="d-aaaaaa", code="A", title="Old berth"))
    publish_one(project.root, clock, files)
    for _ in range(3):
        assert "Old berth" in project.run("show", "A").out
    other = clone(project.remote, "other")
    git(other, "config", "user.name", "Synthetic")
    git(other, "config", "user.email", "synthetic@example.invalid")
    publish_one(other, clock, files_of(decision(id="d-aaaaaa", code="A", title="New berth")))
    project.git("fetch", "origin", "lodge")
    # The store pins the newly fetched remote tip on its next refresh.
    project.git("update-ref", "refs/remotes/origin/lodge", "FETCH_HEAD")

    store = open_store(project.root, BRANCH, clock)
    store.trees()
    assert "New berth" in project.run("show", "A").out


def test_viewer_factory_has_no_read_model(
    project: Project, monkeypatch: pytest.MonkeyPatch
) -> None:
    prepared(project)
    factories = []

    def serve(factory: Callable[[], Lodge], *args: object) -> int:
        factories.append(factory)
        lodge = factory()
        try:
            assert lodge._read_model is False
        finally:
            lodge.release()
        return 0

    monkeypatch.setattr(main, "serve", serve)
    assert project.run("view").code == 0 and factories


def test_git_status_refresh_does_not_write_a_seen_state(project: Project) -> None:
    path = prepared(project)
    before = (project.root / ".git/index").read_bytes()
    stat = path.stat()
    os.utime(path, ns=(stat.st_atime_ns, stat.st_mtime_ns + 2_000_000_000))
    project.git("status", "--porcelain")
    assert (project.root / ".git/index").read_bytes() != before
    cache = project.root / ".git/lodge"
    paths = [p for p in cache.iterdir() if p.name.endswith((".sqlite", "-wal"))]
    contents = {p: p.read_bytes() for p in paths}
    assert "Synthetic berth" in project.run("show", "A").out
    assert {p: p.read_bytes() for p in paths} == contents
