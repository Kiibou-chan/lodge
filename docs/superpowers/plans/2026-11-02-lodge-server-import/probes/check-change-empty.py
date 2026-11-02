"""Probe 9: lodge 0.2's check_change from an empty state on a store's files.

Usage: check-change-empty.py ROOT [TOML]; ROOT holds lodge/ and .lodge.toml, TOML replaces the latter's text.
"""

import pathlib
import sys
import tomllib
from collections import Counter
from datetime import datetime, timezone

from lodge import core
from lodge.core.snapshot import Tree, load

root = pathlib.Path(sys.argv[1])
files = {
    p.relative_to(root).as_posix(): p.read_bytes().decode("utf-8", "surrogateescape")
    for p in (root / "lodge").rglob("*")
    if p.is_file()
}
attachments = frozenset(k for k in files if k.startswith("lodge/attachments/"))
records = {k: v for k, v in files.items() if k not in attachments}
text = sys.argv[2] if len(sys.argv) > 2 else (root / ".lodge.toml").read_text()
table = tomllib.loads(text)
settings = core.parse_core_settings({k: v for k, v in table.items() if k in ("length", "import")})
after = load(Tree(rev=None, files=records, attachments=attachments))
print("files", len(files), "state problems", len(core.check_state(after).problems))
result = core.check_change(
    load(Tree(rev=None, files={})), after, settings, datetime(2026, 11, 3, tzinfo=timezone.utc)
)
print("change problems", len(result.problems), dict(Counter(p.check for p in result.problems)))
for p in result.problems:
    print(p.check, p.path, p.message)
