"""Selected base lookups batch unusual names and preserve unavailable gitlinks."""

from pathlib import Path
from unittest.mock import patch

from gitstore.repos import git, write
from gitstore.test_identity import RECORD, prepared
from lodge.core import blob_id
from lodge.gitstore import git as runner
from lodge.gitstore.committed import Committed


def test_selected_batches_names_and_missing_objects(tmp_path: Path) -> None:
    repo, _ = prepared(tmp_path)
    unusual = "lodge/decisions/a\nspace berth.md"
    write(repo, unusual, "Unusual berth.\n")
    link = "lodge/decisions/unavailable"
    git(repo, "add", "--", "lodge")
    git(repo, "update-index", "--add", "--cacheinfo", f"160000,{'1' * 40},{link}")
    git(repo, "commit", "-m", "Synthetic unusual base")
    rev = git(repo, "rev-parse", "HEAD")
    committed = Committed(repo)
    committed.tree_id(rev)
    with patch.object(runner, "attempt", wraps=runner.attempt) as calls:
        selected = committed.selected(rev, [RECORD, unusual, link, "absent\nfile"], [link])
    assert dict(selected.blobs) == {
        RECORD: blob_id(b"Original berth.\n"),
        unusual: blob_id(b"Unusual berth.\n"),
        link: blob_id(b""),
    }
    assert selected.kinds[link] == "commit"
    assert calls.call_count == 1
    assert calls.call_args.args[0][:2] == ["cat-file", "--batch-check"]
