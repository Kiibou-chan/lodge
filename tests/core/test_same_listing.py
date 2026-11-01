"""Exact-tree equality depends on file contents and attachments alone."""

import pytest

from lodge.core import Tree, same_listing


@pytest.mark.parametrize(
    ("other", "equal"),
    [
        pytest.param(Tree("other", {"a": "text"}, frozenset({"attachment"})), True, id="revision"),
        pytest.param(Tree("rev", {"a": "edited"}, frozenset({"attachment"})), False, id="contents"),
        pytest.param(Tree("rev", {"b": "text"}, frozenset({"attachment"})), False, id="paths"),
        pytest.param(Tree("rev", {"a": "text"}), False, id="attachments"),
    ],
)
def test_same_listing_compares_files_and_attachments(other: Tree, equal: bool) -> None:
    first = Tree("rev", {"a": "text"}, frozenset({"attachment"}))
    assert same_listing(first, other) is equal
