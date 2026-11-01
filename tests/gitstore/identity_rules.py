"""The alternative R11 rule is selected at its single production switch."""

from collections.abc import Iterator
from contextlib import contextmanager
from unittest.mock import patch

from lodge.gitstore import identity


@contextmanager
def r11b() -> Iterator[None]:
    with patch.object(identity, "candidates", lambda obj, rev, trunk: obj.stat_current(rev, trunk)):
        yield
