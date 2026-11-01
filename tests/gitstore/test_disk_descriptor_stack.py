"""A deep walk keeps bounded descriptors and opens each path component linearly."""

import os
from pathlib import Path
from unittest.mock import patch

from lodge.gitstore import disk


def test_deep_path_reuses_a_bounded_descriptor_stack(tmp_path: Path) -> None:
    path = tmp_path / "lodge"
    path.mkdir()
    depth = 180
    for _ in range(depth):
        path /= "d"
        path.mkdir()
    (path / "leaf.md").write_text("Deep berth.\n")
    real_open, real_close = os.open, os.close
    live: set[int] = set()
    maximum = 0

    def opened(
        path: str | Path, flags: int, mode: int = 0o777, *, dir_fd: int | None = None
    ) -> int:
        nonlocal maximum
        fd = real_open(path, flags, mode, dir_fd=dir_fd)
        live.add(fd)
        maximum = max(maximum, len(live))
        return fd

    def closed(fd: int) -> None:
        live.discard(fd)
        real_close(fd)

    with patch.object(os, "open", side_effect=opened) as calls, patch.object(os, "close", closed):
        walked = disk.walk(tmp_path)
        try:
            assert (
                disk.read_at(walked, path.relative_to(tmp_path).as_posix() + "/leaf.md")
                == b"Deep berth.\n"
            )
        finally:
            walked.close()
        assert calls.call_count < 4 * depth, calls.call_count
    assert maximum <= 66
    assert not live
