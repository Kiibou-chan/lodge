"""What the gate compares in checkout mode: the committed state, the working tree, the base."""

from pathlib import Path

import pytest

from gitstore.repos import CHECKOUT, Ticker, commit, git, write
from gitstore.repos import checkout_project as project
from lodge.app import LodgeError
from lodge.gitstore import StoreSettings, init_store, open_store

DECISION = "lodge/decisions/d-aaaaaa-keep.md"
ENTRY = "lodge/spec/storage/s-aaaaaa-kept.md"
UNCOMMITTED = "uncommitted record changes in lodge/; commit them before you push"


def test_gate_checks_what_is_committed_and_the_working_tree(tmp_path: Path) -> None:
    _, repo = project(tmp_path)
    commit(repo, DECISION, "committed\n", "Add a decision")
    write(repo, ENTRY, "only on disk\n")
    store = open_store(repo, CHECKOUT, Ticker())
    current, published = store.trees()
    gate = store.gate(current)
    assert gate.published == published
    assert [label for label, _ in gate.checked] == ["committed", "working tree"]
    committed, working = (tree for _, tree in gate.checked)
    assert committed.rev == git(repo, "rev-parse", "HEAD") and ENTRY not in committed.files
    assert working is current
    assert gate.notes == (UNCOMMITTED,)


def test_gate_checks_one_state_when_the_working_tree_is_committed(tmp_path: Path) -> None:
    _, repo = project(tmp_path)
    commit(repo, DECISION, "committed\n", "Add a decision")
    store = open_store(repo, CHECKOUT, Ticker())
    current, _ = store.trees()
    gate = store.gate(current)
    assert gate.checked == (("", current),) and gate.notes == ()


def test_gate_with_an_unborn_head_has_no_history_to_miss(tmp_path: Path) -> None:
    repo = tmp_path / "fresh"
    git(tmp_path, "init", "-b", "main", str(repo))
    init_store(repo, CHECKOUT)
    store = open_store(repo, CHECKOUT, Ticker())
    current, published = store.trees()
    gate = store.gate(current)
    assert gate.published == published and store.freshness() is None
    assert [label for label, _ in gate.checked] == ["committed", "working tree"]


def test_gate_without_the_base_says_which_refs_were_tried(tmp_path: Path) -> None:
    _, repo = project(tmp_path)
    store = open_store(repo, StoreSettings(base="trunk"), Ticker())
    current, _ = store.trees()
    said = store.freshness() or ""
    for part in ("origin/trunk", "trunk", "base", ".lodge.toml"):
        assert part in said
    with pytest.raises(LodgeError) as raised:
        store.gate(current)
    assert str(raised.value) == said and raised.value.exit_code == 2


def test_gate_with_a_base_that_shares_no_history_is_not_found(tmp_path: Path) -> None:
    _, repo = project(tmp_path)
    git(repo, "checkout", "-q", "--orphan", "island")
    commit(repo, "island.txt", "alone\n", "Island")
    store = open_store(repo, CHECKOUT, Ticker())
    current, _ = store.trees()
    assert "origin/main" in (store.freshness() or "")
    with pytest.raises(LodgeError, match="origin/main"):
        store.gate(current)
