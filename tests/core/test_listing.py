"""Per-file parsing composes into the exact snapshot, with git-compatible byte keys."""

import sys
from pathlib import Path

import pytest
from builders import area, decision, entry, files_of, snapshot_of, thread
from samples import DECISION_PATH, EXAMPLE, EXAMPLE_TEXT

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "app"))

from gitstore.repos import git
from lodge.core import (
    Listing,
    Problem,
    Snapshot,
    Tree,
    assemble,
    blob_id,
    load,
    new_record_path,
    parse_file,
)


@pytest.mark.parametrize(
    "raw", [b"", b"Berth\n", b"\xff\x00\x80\r\n"], ids=["empty", "text", "binary"]
)
def test_blob_id_matches_git(raw: bytes, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    config = tmp_path / "gitconfig"
    config.write_text("")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(config))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR"):
        monkeypatch.delenv(name, raising=False)
    git(tmp_path, "init", "-b", "main")
    expected = git(tmp_path, "hash-object", "--stdin", input=raw.decode("utf-8", "surrogateescape"))
    ident = blob_id(raw)
    listing = Listing(None, "state", {"lodge/notes.txt": ident}, frozenset())
    assert listing.blobs == {"lodge/notes.txt": expected}
    assert listing.rev is None and listing.ident == "state" and listing.attachments == frozenset()


def sample_trees() -> list[tuple[Tree, Snapshot]]:
    """The sample text, every record kind, and the loader's exceptional file shapes."""
    held, choice, spec, discussion = area(), decision(id="d-aaaaaa"), entry(id="s-aaaaaa"), thread()
    first = decision(id="d-bbbbbb", title="First")
    second = decision(id="d-bbbbbb", title="Second")
    kept, dropped = new_record_path(first), new_record_path(second)
    duplicate = f"the ID {first.id} is in both {kept} and {dropped}; the first is kept"
    broken = "lodge/decisions/broken.md"
    attachment = "lodge/attachments/d-aaaaaa/log.bin"
    stray = "lodge/notes.txt"
    stray_message = (
        "this file is not a record; lodge holds decisions in lodge/decisions/, specification "
        "entries in lodge/spec/<area>/, and attachments in lodge/attachments/"
    )
    misplaced = "lodge/decisions/s-aaaaaa-misplaced.md"
    return [
        (Tree(None, {}), snapshot_of()),
        (Tree("sample", {DECISION_PATH: EXAMPLE_TEXT}), snapshot_of(EXAMPLE)),
        (
            Tree(None, files_of(held, choice, spec, discussion)),
            snapshot_of(held, choice, spec, discussion),
        ),
        (
            Tree(None, files_of(first, second)),
            snapshot_of(
                first, problems=(Problem(kept, 2, duplicate), Problem(dropped, 2, duplicate))
            ),
        ),
        (Tree(None, {stray: "notes"}), snapshot_of(problems=(Problem(stray, 1, stray_message),))),
        (
            Tree(None, {attachment: "\udcff"}, frozenset({"lodge/attachments/listed.bin"})),
            snapshot_of(attachments=(attachment, "lodge/attachments/listed.bin")),
        ),
        (
            Tree(None, {broken: "---\ninvalid\n"}),
            snapshot_of(problems=(Problem(broken, 1, "the header is not closed by a --- line"),)),
        ),
        (
            Tree(None, {misplaced: next(iter(files_of(spec).values()))}),
            snapshot_of(
                problems=(Problem(misplaced, 1, "this record belongs in lodge/spec/<area>/"),)
            ),
        ),
        (Tree(None, {"README.md": "outside", "lodge/spec/.gitkeep": ""}), snapshot_of()),
    ]


@pytest.mark.parametrize(
    ("tree", "expected"),
    sample_trees(),
    ids=[
        "empty",
        "sample",
        "all-kinds",
        "duplicate-id",
        "stray",
        "attachments",
        "unreadable",
        "misplaced",
        "ignored",
    ],
)
def test_assemble_equals_load(tree: Tree, expected: Snapshot) -> None:
    parsed = {path: parse_file(path, text) for path, text in reversed(list(tree.files.items()))}
    assert assemble(parsed, tree.attachments) == load(tree) == expected


@pytest.mark.parametrize(
    "path",
    ["lodge/attachments/d-aaaaaa/log.bin", "lodge/decisions/.gitkeep", "lodge/spec/.gitkeep"],
    ids=["attachment", "decisions-gitkeep", "spec-gitkeep"],
)
def test_parse_file_ignores_attachments_and_gitkeep(path: str) -> None:
    assert parse_file(path, "not a header\udcff") is None
