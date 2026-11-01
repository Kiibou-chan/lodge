"""DISK-1 keeps four states and raises the per-file allowance."""

from lodge.gitstore.index_space import INDEX_BYTES_PER_FILE, index_file_cap
from lodge.gitstore.index_states import KEPT_STATES


def test_authorised_index_cap() -> None:
    assert INDEX_BYTES_PER_FILE == 1_900
    assert index_file_cap(160_000) == 304_000_000
    assert KEPT_STATES == 4
