"""The real CLI prints the same text with a warm, absent, or read-only index."""

import os

import pytest

from e2e.conftest import Project


def prepared(project: Project) -> None:
    project.run("init")
    draft = project.draft(
        "decision.md",
        "---\nkind: decision\ncode: BERTH-1\ntitle: Keep transcripts\n"
        "scope: product\ndecided_by: coordinator\n---\n\nKeep transcripts whole.\n",
    )
    assert project.run("add", draft).code == 0
    project.publish_main()


def test_index_off_same_output(project: Project, monkeypatch: pytest.MonkeyPatch) -> None:
    prepared(project)
    for command in (
        ("show", "BERTH-1"),
        ("search", "transcripts"),
        ("waiting",),
        ("spec",),
        ("check", "--gate"),
    ):
        for _ in range(2):
            monkeypatch.setenv("LODGE_INDEX", "off")
            off = project.run(*command)
            monkeypatch.delenv("LODGE_INDEX")
            on = project.run(*command)
            assert on == off
    assert list((project.root / ".git/lodge").glob("index-*.sqlite"))


def test_read_only_common_dir_reads(project: Project) -> None:
    if os.geteuid() == 0:
        pytest.skip("root bypasses permission bits")
    prepared(project)
    before = project.run("show", "BERTH-1")
    folder = project.root / ".git/lodge"
    assert list(folder.glob("index-*.sqlite"))
    modes = {p: p.stat().st_mode & 0o777 for p in [folder, *folder.iterdir()]}
    for path in modes:
        path.chmod(0o500 if path.is_dir() else 0o400)
    try:
        assert project.run("show", "BERTH-1") == before
        assert before.code == 0
    finally:
        for path, mode in modes.items():
            path.chmod(mode)
