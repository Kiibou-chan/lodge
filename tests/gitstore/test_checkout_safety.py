"""The checkout store never follows a link out of `lodge/` and never half-writes a change."""

import os
import re
import stat
from pathlib import Path

import pytest

from gitstore.repos import CHECKOUT, Ticker, checkout_project, git, write
from lodge.app import LodgeError, PublishOutcome
from lodge.core import load
from lodge.gitstore import init_store, open_store

DECISION = "lodge/decisions/d-aaaaaa-keep.md"
ENTRY = "lodge/spec/storage/s-aaaaaa-kept.md"


def outside(tmp_path: Path) -> Path:
    folder = tmp_path / "outside"
    folder.mkdir()
    (folder / "secret.txt").write_text("secret\n")
    (folder / "victim.md").write_text("victim\n")
    return folder


def untouched(folder: Path) -> None:
    assert sorted(p.name for p in folder.iterdir()) == ["secret.txt", "victim.md"]
    assert (folder / "victim.md").read_text() == "victim\n"


def test_a_linked_file_is_read_as_its_link_text(tmp_path: Path) -> None:
    _, repo = checkout_project(tmp_path)
    secret = outside(tmp_path) / "secret.txt"
    (repo / DECISION).symlink_to(secret)
    current, _ = open_store(repo, CHECKOUT, Ticker()).trees()
    assert current.files[DECISION] == str(secret)
    assert "secret\n" not in current.files.values()
    assert [p.path for p in load(current).problems] == [DECISION]


def test_a_linked_folder_is_listed_not_followed(tmp_path: Path) -> None:
    _, repo = checkout_project(tmp_path)
    folder = outside(tmp_path)
    (repo / "lodge/spec/area").symlink_to(folder, target_is_directory=True)
    current, _ = open_store(repo, CHECKOUT, Ticker()).trees()
    assert current.files["lodge/spec/area"] == str(folder)
    assert not any(path.startswith("lodge/spec/area/") for path in current.files)


def test_publish_refuses_to_write_through_a_linked_file(tmp_path: Path) -> None:
    _, repo = checkout_project(tmp_path)
    folder = outside(tmp_path)
    (repo / DECISION).symlink_to(folder / "victim.md")
    store = open_store(repo, CHECKOUT, Ticker())
    current, _ = store.trees()
    with pytest.raises(LodgeError, match="symbolic link"):
        store.publish(current, {DECISION: "OVERWRITTEN\n"}, "m")
    untouched(folder)


def test_publish_refuses_to_write_through_a_linked_folder(tmp_path: Path) -> None:
    _, repo = checkout_project(tmp_path)
    folder = outside(tmp_path)
    (repo / "lodge/spec/area").symlink_to(folder, target_is_directory=True)
    store = open_store(repo, CHECKOUT, Ticker())
    current, _ = store.trees()
    with pytest.raises(LodgeError, match=re.escape("lodge/spec/area/s-cccccc-z.md")):
        store.publish(current, {"lodge/spec/area/s-cccccc-z.md": "x\n"}, "m")
    untouched(folder)


def test_a_linked_data_folder_is_refused(tmp_path: Path) -> None:
    folder = outside(tmp_path)
    repo = tmp_path / "solo"
    git(tmp_path, "init", "-b", "main", str(repo))
    (repo / "lodge").symlink_to(folder, target_is_directory=True)
    store = open_store(repo, CHECKOUT, Ticker())
    with pytest.raises(LodgeError, match="symbolic link"):
        store.trees()
    with pytest.raises(LodgeError, match="symbolic link"):
        init_store(repo, CHECKOUT)
    untouched(folder)


def test_data_folder_that_is_a_file_is_named(tmp_path: Path) -> None:
    repo = tmp_path / "solo"
    git(tmp_path, "init", "-b", "main", str(repo))
    (repo / "lodge").write_text("a file\n")
    with pytest.raises(LodgeError, match="a file, not a folder"):
        open_store(repo, CHECKOUT, Ticker()).trees()
    with pytest.raises(LodgeError, match="a file, not a folder"):
        init_store(repo, CHECKOUT)


def test_a_fifo_does_not_hang_the_read(tmp_path: Path) -> None:
    _, repo = checkout_project(tmp_path)
    os.mkfifo(repo / "lodge/decisions/d-bbbbbb-fifo.md")
    current, _ = open_store(repo, CHECKOUT, Ticker()).trees()
    assert current.files["lodge/decisions/d-bbbbbb-fifo.md"] == ""
    assert "lodge/decisions/d-bbbbbb-fifo.md" in {p.path for p in load(current).problems}


def test_publish_into_a_dangling_link_is_a_lodge_error(tmp_path: Path) -> None:
    _, repo = checkout_project(tmp_path)
    (repo / "lodge/spec/gone").symlink_to(tmp_path / "nowhere")
    store = open_store(repo, CHECKOUT, Ticker())
    current, _ = store.trees()
    with pytest.raises(LodgeError, match=re.escape("lodge/spec/gone/s-aaaaaa-x.md")):
        store.publish(current, {"lodge/spec/gone/s-aaaaaa-x.md": "x\n"}, "m")


def test_publish_through_a_file_in_the_way_is_a_lodge_error(tmp_path: Path) -> None:
    _, repo = checkout_project(tmp_path)
    write(repo, "lodge/spec/storage", "a file\n")
    store = open_store(repo, CHECKOUT, Ticker())
    current, _ = store.trees()
    with pytest.raises(LodgeError, match=re.escape("lodge/spec/storage")):
        store.publish(current, {ENTRY: "x\n"}, "m")


@pytest.mark.skipif(os.geteuid() == 0, reason="root ignores folder permissions")
def test_a_failed_write_leaves_nothing_behind(tmp_path: Path) -> None:
    _, repo = checkout_project(tmp_path)
    write(repo, DECISION, "before\n")
    locked = repo / "lodge/spec/locked"
    locked.mkdir()
    locked.chmod(stat.S_IRUSR | stat.S_IXUSR)
    store = open_store(repo, CHECKOUT, Ticker())
    current, _ = store.trees()
    writes = {DECISION: "after\n", "lodge/spec/locked/s-aaaaaa-x.md": "x\n"}
    try:
        with pytest.raises(LodgeError, match=re.escape("lodge/spec/locked/s-aaaaaa-x.md")):
            store.publish(current, writes, "m")
    finally:
        locked.chmod(stat.S_IRWXU)
    assert (repo / DECISION).read_text() == "before\n"
    assert sorted(p.name for p in locked.iterdir()) == []
    assert [p.name for p in (repo / "lodge/decisions").iterdir() if "tmp" in p.name] == []
    assert git(repo, "diff", "--cached", "--name-only") == ""


def test_an_exit_between_the_replaces_leaves_nothing_behind(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, repo = checkout_project(tmp_path)
    write(repo, DECISION, "before\n")
    store = open_store(repo, CHECKOUT, Ticker())
    current, _ = store.trees()
    replace, calls = os.replace, []

    def interrupted(source: str | Path, target: str | Path) -> None:
        calls.append(target)
        if len(calls) == 2:
            raise SystemExit(143)
        replace(source, target)

    monkeypatch.setattr(os, "replace", interrupted)
    with pytest.raises(SystemExit):
        store.publish(current, {DECISION: "after\n", ENTRY: "new\n"}, "m")
    assert (repo / DECISION).read_text() == "before\n" and not (repo / ENTRY).exists()
    assert [p.name for p in repo.rglob("*") if "tmp" in p.name] == []
    assert git(repo, "diff", "--cached", "--name-only") == ""


def test_a_failed_stage_restores_the_files(tmp_path: Path) -> None:
    _, repo = checkout_project(tmp_path)
    write(repo, DECISION, "before\n")
    write(repo, ".gitignore", "lodge/spec/*.tmp\n")
    store = open_store(repo, CHECKOUT, Ticker())
    current, _ = store.trees()
    writes = {DECISION: "after\n", ENTRY: "new\n", "lodge/spec/x.tmp": "ignored\n"}
    with pytest.raises(LodgeError):
        store.publish(current, writes, "m")
    assert (repo / DECISION).read_text() == "before\n"
    assert not (repo / ENTRY).exists() and not (repo / "lodge/spec/x.tmp").exists()
    assert not (repo / "lodge/spec/storage").exists()
    assert git(repo, "diff", "--cached", "--name-only") == ""


def test_publish_still_stages_after_a_replace(tmp_path: Path) -> None:
    _, repo = checkout_project(tmp_path)
    write(repo, DECISION, "before\n")
    store = open_store(repo, CHECKOUT, Ticker())
    current, _ = store.trees()
    assert store.publish(current, {DECISION: "after\n"}, "m") is PublishOutcome.STAGED
    assert (repo / DECISION).read_text() == "after\n"
    assert [p.name for p in (repo / "lodge/decisions").iterdir() if "tmp" in p.name] == []


def test_a_link_at_the_old_temporary_name_is_not_followed(tmp_path: Path) -> None:
    _, repo = checkout_project(tmp_path)
    folder = outside(tmp_path)
    write(repo, DECISION, "before\n")
    planted = repo / "lodge/decisions/.d-aaaaaa-keep.md.lodge-tmp"
    planted.symlink_to(folder / "victim.md")
    store = open_store(repo, CHECKOUT, Ticker())
    current, _ = store.trees()
    assert store.publish(current, {DECISION: "after\n"}, "m") is PublishOutcome.STAGED
    untouched(folder)
    assert planted.is_symlink() and not (repo / DECISION).is_symlink()
    assert (repo / DECISION).read_text() == "after\n"


def test_her_file_at_the_old_temporary_name_is_kept(tmp_path: Path) -> None:
    _, repo = checkout_project(tmp_path)
    write(repo, DECISION, "before\n")
    mine = repo / "lodge/decisions/.d-aaaaaa-keep.md.lodge-tmp"
    mine.write_text("her notes\n")
    store = open_store(repo, CHECKOUT, Ticker())
    current, _ = store.trees()
    assert store.publish(current, {DECISION: "after\n"}, "m") is PublishOutcome.STAGED
    assert mine.read_text() == "her notes\n"


@pytest.mark.parametrize("mode", [0o600, 0o755])
def test_an_edited_record_keeps_its_file_mode(tmp_path: Path, mode: int) -> None:
    _, repo = checkout_project(tmp_path)
    write(repo, DECISION, "before\n")
    (repo / DECISION).chmod(mode)
    store = open_store(repo, CHECKOUT, Ticker())
    current, _ = store.trees()
    store.publish(current, {DECISION: "after\n"}, "m")
    assert stat.S_IMODE((repo / DECISION).stat().st_mode) == mode


def test_a_new_record_gets_the_umask_mode_without_the_umask_being_read(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    _, repo = checkout_project(tmp_path)
    store = open_store(repo, CHECKOUT, Ticker())
    current, _ = store.trees()
    before = os.umask(0o027)
    try:
        monkeypatch.setattr(os, "umask", lambda _mask: pytest.fail("the umask was set"))
        store.publish(current, {ENTRY: "new\n"}, "m")
    finally:
        monkeypatch.undo()
        os.umask(before)
    assert stat.S_IMODE((repo / ENTRY).stat().st_mode) == 0o640
