"""Deep exact reads preserve every file without exhausting frames or descriptors."""

import os
import resource
from pathlib import Path

from gitstore.repos import write
from gitstore.test_identity import agrees, prepared
from lodge.gitstore import disk


def test_1100_deep_tree_is_read_with_bounded_descriptors(tmp_path: Path) -> None:
    repo, store = prepared(tmp_path)
    folder = repo / "lodge/decisions"
    parents = [folder]
    for _ in range(1100):
        folder /= "d"
        folder.mkdir()
        parents.append(folder)
    path = folder / "deep.md"
    path.write_text("Deep berth.\n")
    expected = path.relative_to(repo).as_posix()
    before = resource.getrlimit(resource.RLIMIT_NOFILE)
    try:
        resource.setrlimit(resource.RLIMIT_NOFILE, (min(128, before[0]), before[1]))
        assert expected in {
            str(Path(p, f).relative_to(repo)) for p, _, fs in os.walk(repo / "lodge") for f in fs
        }
        walked = disk.walk(repo)
        try:
            assert expected in walked.names
            assert not walked.unlistable
            assert disk.read_at(walked, expected) == b"Deep berth.\n"
        finally:
            walked.close()
        # trees() serves the gate, check, and add; identities use the same reader.
        assert store.trees()[0].files[expected] == "Deep berth.\n"
        assert expected in agrees(store).blobs
    finally:
        resource.setrlimit(resource.RLIMIT_NOFILE, before)
        path.unlink()
        for parent in reversed(parents[1:]):
            parent.rmdir()


def test_repository_root_may_be_a_link(tmp_path: Path) -> None:
    root = tmp_path / "real"
    write(root, "lodge/decisions/berth.md", "Berth.\n")
    link = tmp_path / "linked"
    link.symlink_to(root, target_is_directory=True)
    assert disk.tree(link) == disk.tree(root)
