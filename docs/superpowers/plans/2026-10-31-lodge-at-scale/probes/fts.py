"""FTS5 over core's own words, and what a brief line spends on default fields.

  python fts.py STORE
"""

import os
import sqlite3
import sys
import tempfile
import time

import yaml

from lodge import core
from lodge.core import yamlio
from lodge.core.words import words


class _C(yaml.CSafeLoader):
    yaml_implicit_resolvers = {}
    yaml_constructors = yamlio._TextLoader.yaml_constructors


sys.modules["lodge.core.document"].load_yaml = lambda t: yaml.load(t, Loader=_C)
os.chdir(sys.argv[1])
from lodge.main import _make_lodge  # noqa: E402

w = _make_lodge()._w
current, _ = w.store.trees()
s = core.load(current)
d = core.derive(s)
records = {**s.decisions, **s.entries}


def timed(label, fn):
    t = time.perf_counter()
    out = fn()
    print(f"{time.perf_counter() - t:7.3f} s  {label}", flush=True)
    return out


with tempfile.TemporaryDirectory(dir="/var/tmp") as folder:
    path = os.path.join(folder, "f.sqlite")
    db = sqlite3.connect(path)
    db.execute("create virtual table f using fts5(id unindexed, title, statement, tokenize='ascii')")
    rows = [(i, " ".join(sorted(words(r.title))), " ".join(sorted(words(r.statement)))) for i, r in records.items()]
    timed(f"insert {len(rows)} rows of core's words", lambda: (db.executemany("insert into f values (?, ?, ?)", rows), db.commit()))
    print(f"index file {os.path.getsize(path) / 1e6:.1f} MB")
    for q in ('"berth" OR "crane"', '"berth" AND "crane" AND "tide"', '"zzz"'):
        got = timed(f"match {q}", lambda: db.execute("select id from f where f match ?", (q,)).fetchall())
        print(f"         {len(got)} candidates")
    con2 = sqlite3.connect(path)
    timed("open a second connection and run one match", lambda: con2.execute("select id from f where f match ?", ('"tide" AND "quay" AND "gantry" AND "winch"',)).fetchall())

hits = core.search(s, d, "berth crane", core.Filters(), 200)
lines = [core.format_brief(core.level1(s, d, i, frozenset())) for i in hits]
total = sum(len(x) + 1 for x in lines)
status = sum(x.count(" · current") * len(" · current") for x in lines)
entries = [x for x in lines if x.startswith("s-")]
print(f"brief lines: {len(lines)}, {total} characters; ' · current' {status} ({100 * status / total:.0f} %)")
print("sample:", lines[0])
