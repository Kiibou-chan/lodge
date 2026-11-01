"""Composition shares repository discovery and releases each request's index explicitly."""

import sqlite3
from http import HTTPStatus
from urllib.parse import urlsplit

import pytest

import lodge.main as entrypoint
from e2e.conftest import Project
from lodge.gitstore import index_db, project_index, setup
from lodge.gitstore.git import run
from lodge.gitstore.index_db import IndexDB
from lodge.viewer import server, writes


def test_common_directory_discovered_once(
    project: Project, monkeypatch: pytest.MonkeyPatch
) -> None:
    assert project.run("init").code == 0
    original = run
    calls: list[list[str]] = []

    def spy(args: list[str], *rest: object, **kwargs: object) -> str:
        if args == ["rev-parse", "--path-format=absolute", "--git-common-dir"]:
            calls.append(args)
        return original(args, *rest, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(setup, "run", spy)
    monkeypatch.setattr(index_db, "run", spy, raising=False)
    assert project.run("waiting").code == 0
    assert len(calls) == 1


@pytest.mark.parametrize(
    "operation", ["cli", "cli-error", "viewer", "viewer-error", "post", "post-error"]
)
def test_factory_releases_retained_index(
    project: Project, monkeypatch: pytest.MonkeyPatch, operation: str
) -> None:
    assert project.run("init").code == 0
    original = project_index
    indexes: list[IndexDB] = []

    def retain(*args: object, **kwargs: object) -> IndexDB:
        index = original(*args, **kwargs)  # type: ignore[arg-type]
        assert isinstance(index, IndexDB)
        indexes.append(index)
        return index

    monkeypatch.setattr(entrypoint, "project_index", retain)
    if operation.startswith("cli"):
        project.run(*(("show", "missing") if operation.endswith("error") else ("waiting",)))
    elif operation.startswith("viewer"):
        monkeypatch.chdir(project.root)
        path = "/r/missing" if operation.endswith("error") else "/problems"
        server.render(entrypoint._make_lodge, urlsplit(path), "token")
    else:
        monkeypatch.chdir(project.root)

        def confirm(post: writes._Post) -> writes.Reply:
            if operation.endswith("error"):
                raise RuntimeError("injected POST failure")
            return writes.Reply(HTTPStatus.SEE_OTHER, "", "/")

        monkeypatch.setattr(writes._Post, "confirm", confirm)
        reply = writes.handle_post(
            entrypoint._make_lodge,
            writes.Gatekeeper("t" * 32, frozenset({"localhost:8000"})),
            "/confirm",
            {
                "host": "localhost:8000",
                "origin": "http://localhost:8000",
                "content-type": "application/x-www-form-urlencoded",
            },
            b"token=" + b"t" * 32,
        )
        assert reply.status == (
            HTTPStatus.INTERNAL_SERVER_ERROR
            if operation.endswith("error")
            else HTTPStatus.SEE_OTHER
        )
    assert len(indexes) == 1
    assert indexes[0].lock is None
    with pytest.raises(sqlite3.ProgrammingError):
        indexes[0].db.execute("SELECT 1")
