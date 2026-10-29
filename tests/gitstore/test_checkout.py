from pathlib import Path

import pytest

from gitstore.repos import (
    CHECKOUT,
    Ticker,
    clone,
    commit,
    git,
    worktree,
    write,
)
from gitstore.repos import checkout_project as project
from lodge.app import LodgeError, PublishOutcome
from lodge.core import Tree, load
from lodge.gitstore import StoreSettings, init_store, open_store

DECISION = "lodge/decisions/d-aaaaaa-keep.md"
ENTRY = "lodge/spec/storage/s-aaaaaa-kept.md"
ATTACHMENT = "lodge/attachments/d-aaaaaa/log.txt"


def test_checkout_publish_stages_not_commits(tmp_path: Path) -> None:
    _, repo = project(tmp_path)
    head = git(repo, "rev-parse", "HEAD")
    store = open_store(repo, CHECKOUT, Ticker())
    current, _ = store.trees()
    outcome = store.publish(current, {DECISION: "one\n", ENTRY: "two\n"}, "lodge: add")
    assert outcome is PublishOutcome.STAGED
    assert git(repo, "rev-parse", "HEAD") == head
    assert git(repo, "diff", "--cached", "--name-only").splitlines() == [DECISION, ENTRY]
    assert (repo / DECISION).read_text() == "one\n"
    assert store.freshness() is None
    assert store.trees()[0].files[DECISION] == "one\n"


def test_checkout_current_is_the_working_tree(tmp_path: Path) -> None:
    _, repo = project(tmp_path)
    write(repo, DECISION, "untracked\n")
    current, _ = open_store(repo, CHECKOUT, Ticker()).trees()
    assert current.rev is None
    assert current.files == {
        "lodge/decisions/.gitkeep": "",
        "lodge/spec/.gitkeep": "",
        DECISION: "untracked\n",
    }


def test_checkout_published_is_merge_base_with_remote_base(tmp_path: Path) -> None:
    remote, repo = project(tmp_path)
    commit(repo, DECISION, "base\n", "Add a decision")
    git(repo, "push", "origin", "main")
    git(repo, "switch", "-c", "feature")
    commit(repo, ENTRY, "feature\n", "Add an entry")
    other = clone(remote, "other")
    commit(other, "lodge/decisions/d-bbbbbb-later.md", "later\n", "Land on main")
    git(other, "push", "origin", "main")
    git(repo, "fetch", "origin")
    write(repo, "lodge/decisions/d-cccccc-draft.md", "draft\n")
    current, published = open_store(repo, CHECKOUT, Ticker()).trees()
    assert set(published.files) == {"lodge/decisions/.gitkeep", "lodge/spec/.gitkeep", DECISION}
    assert published.rev == git(repo, "merge-base", "HEAD", "origin/main")
    assert {ENTRY, "lodge/decisions/d-cccccc-draft.md"} <= set(current.files)


def test_checkout_published_falls_back_to_local_base(tmp_path: Path) -> None:
    repo = tmp_path / "solo"
    git(tmp_path, "init", "-b", "main", str(repo))
    commit(repo, "README.md", "x\n", "Start")
    init_store(repo, CHECKOUT)
    git(repo, "commit", "-m", "Initialise")
    write(repo, DECISION, "new\n")
    _, published = open_store(repo, CHECKOUT, Ticker()).trees()
    assert published.rev == git(repo, "rev-parse", "HEAD")
    assert DECISION not in published.files and "lodge/spec/.gitkeep" in published.files


def test_checkout_published_empty_without_base(tmp_path: Path) -> None:
    _, repo = project(tmp_path)
    store = open_store(repo, StoreSettings(base="trunk"), Ticker())
    assert store.trees()[1] == Tree(None, {})


def test_checkout_unborn_head_published_empty(tmp_path: Path) -> None:
    repo = tmp_path / "fresh"
    git(tmp_path, "init", "-b", "main", str(repo))
    init_store(repo, CHECKOUT)
    current, published = open_store(repo, CHECKOUT, Ticker()).trees()
    assert published == Tree(None, {}) and "lodge/spec/.gitkeep" in current.files


def test_checkout_publish_rejects_changed_file(tmp_path: Path) -> None:
    _, repo = project(tmp_path)
    store = open_store(repo, CHECKOUT, Ticker())
    write(repo, DECISION, "mine\n")
    current, _ = store.trees()
    write(repo, DECISION, "theirs\n")
    assert store.publish(current, {DECISION: "new\n"}, "m") is PublishOutcome.REJECTED
    assert (repo / DECISION).read_text() == "theirs\n"
    assert git(repo, "diff", "--cached", "--name-only") == ""


def test_checkout_publish_rejects_path_that_appeared(tmp_path: Path) -> None:
    _, repo = project(tmp_path)
    store = open_store(repo, CHECKOUT, Ticker())
    current, _ = store.trees()
    write(repo, DECISION, "theirs\n")
    assert store.publish(current, {DECISION: "new\n", ENTRY: "e\n"}, "m") is (
        PublishOutcome.REJECTED
    )
    assert not (repo / ENTRY).exists()


def test_checkout_publish_rejects_path_that_vanished(tmp_path: Path) -> None:
    _, repo = project(tmp_path)
    write(repo, DECISION, "mine\n")
    store = open_store(repo, CHECKOUT, Ticker())
    current, _ = store.trees()
    (repo / DECISION).unlink()
    assert store.publish(current, {DECISION: "new\n"}, "m") is PublishOutcome.REJECTED


def test_checkout_publish_ignores_other_changed_files(tmp_path: Path) -> None:
    _, repo = project(tmp_path)
    write(repo, DECISION, "mine\n")
    store = open_store(repo, CHECKOUT, Ticker())
    current, _ = store.trees()
    write(repo, DECISION, "edited by hand\n")
    assert store.publish(current, {ENTRY: "e\n"}, "m") is PublishOutcome.STAGED


@pytest.mark.parametrize(
    "path", ["../x.md", "lodge/../x.md", "other/x.md", "/etc/x", "lodge//x.md"]
)
def test_publish_refuses_paths_outside_the_data(tmp_path: Path, path: str) -> None:
    _, repo = project(tmp_path)
    store = open_store(repo, CHECKOUT, Ticker())
    current, _ = store.trees()
    with pytest.raises(LodgeError, match="outside"):
        store.publish(current, {path: "x"}, "m")


def test_attachments_listed(tmp_path: Path) -> None:
    _, repo = project(tmp_path)
    write(repo, ATTACHMENT, "unread\n")
    current, _ = open_store(repo, CHECKOUT, Ticker()).trees()
    assert current.attachments == {ATTACHMENT} and ATTACHMENT not in current.files
    git(repo, "add", "--", ATTACHMENT)
    git(repo, "commit", "-m", "Attach")
    git(repo, "push", "origin", "main")
    published = open_store(repo, CHECKOUT, Ticker()).trees()[1]
    assert published.attachments == {ATTACHMENT} and ATTACHMENT not in published.files


def test_stray_and_non_utf8_files_reported(tmp_path: Path) -> None:
    _, repo = project(tmp_path)
    write(repo, "lodge/notes.txt", "stray\n")
    (repo / "lodge/decisions/d-bbbbbb-bad.md").write_bytes(b"---\nid: \xff\n---\n")
    (repo / ATTACHMENT).parent.mkdir(parents=True)
    (repo / ATTACHMENT).write_bytes(b"\xff\xfe")
    current, _ = open_store(repo, CHECKOUT, Ticker()).trees()
    problems = load(current).problems
    assert {(p.path, p.check) for p in problems} == {
        ("lodge/notes.txt", 1),
        ("lodge/decisions/d-bbbbbb-bad.md", 1),
    }
    assert any(p.message == "the text is not valid UTF-8" for p in problems)


def test_unreadable_file_is_a_problem_not_a_crash(tmp_path: Path) -> None:
    _, repo = project(tmp_path)
    (repo / "lodge/decisions/d-bbbbbb-gone.md").symlink_to(tmp_path / "nowhere")
    current, _ = open_store(repo, CHECKOUT, Ticker()).trees()
    assert [p.path for p in load(current).problems] == ["lodge/decisions/d-bbbbbb-gone.md"]


def test_two_worktrees_share_the_lock_but_not_the_files(tmp_path: Path) -> None:
    _, repo = project(tmp_path)
    other = worktree(repo, "second")
    a = open_store(repo, CHECKOUT, Ticker())
    b = open_store(other, CHECKOUT, Ticker())
    assert a.publish(a.trees()[0], {DECISION: "a\n"}, "m") is PublishOutcome.STAGED
    assert DECISION not in b.trees()[0].files
