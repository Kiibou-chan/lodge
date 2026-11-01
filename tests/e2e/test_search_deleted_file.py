"""A deleted real record leaves historical FTS words without poisoning later searches."""

from unittest.mock import patch

from e2e.conftest import Project
from e2e.index_property_support import harbour, memory_read
from lodge.gitstore.index_db import IndexDB, open_index


def test_six_searches_after_deleted_record_use_stored_rows(project: Project) -> None:
    paths = harbour(project)
    args = ["search", "berth", "--brief"]
    for _ in range(2):
        assert project.run(*args).code == 0
    paths[0].unlink()
    expected = memory_read(project, args)
    for _ in range(2):
        assert project.run(*args) == expected
    index = open_index(project.root / ".git")
    assert isinstance(index, IndexDB)
    before = index.epoch()
    with (
        patch("lodge.app.reads.search_many", side_effect=AssertionError("must use stored rows")),
        patch.object(IndexDB, "keep_state", side_effect=AssertionError("must not keep")) as keeps,
    ):
        for _ in range(6):
            assert project.run(*args) == expected
        assert keeps.call_count == 0
    assert index.epoch() == before
    index.close()
