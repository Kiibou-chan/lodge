"""Cost of storing and restoring every parsed record: pickle against marshal of plain tuples.

  python codec.py STORE
"""

import dataclasses
import marshal
import os
import pickle
import sqlite3
import sys
import tempfile
import time

import yaml

from lodge import core
from lodge.core import yamlio
from lodge.core.model import Change, Decision, Imported, NumberHandle, Quote, SpecEntry


class _C(yaml.CSafeLoader):
    yaml_implicit_resolvers = {}
    yaml_constructors = yamlio._TextLoader.yaml_constructors


sys.modules["lodge.core.document"].load_yaml = lambda t: yaml.load(t, Loader=_C)
os.chdir(sys.argv[1])
from lodge.main import _make_lodge  # noqa: E402

w = _make_lodge()._w
current, _ = w.store.trees()
s = core.load(current)
records = [*s.decisions.values(), *s.entries.values()]


def flat(value):
    if dataclasses.is_dataclass(value):
        return tuple(flat(getattr(value, f.name)) for f in dataclasses.fields(value))
    if isinstance(value, tuple):
        return tuple(flat(v) for v in value)
    return str(value) if hasattr(value, "value") else value


def decision(t):
    (i, title, scope, by, date, st, reason, code, changes, replaces, narrows, confirms, work,
     quote, numbers, attach, imported) = t
    return Decision(
        i, title, scope, by, date, st, reason, code,
        tuple(Change(e, a) for e, a in changes), replaces, narrows, confirms,
        work, Quote(*quote) if quote else None, tuple(NumberHandle(*n) for n in numbers), attach,
        Imported(*imported) if imported else None,
    )


def timed(label, fn):
    t = time.perf_counter()
    out = fn()
    print(f"{time.perf_counter() - t:7.3f} s  {label}", flush=True)
    return out


print([f.name for f in dataclasses.fields(Decision)])
flats = timed("flatten every record to tuples", lambda: [flat(r) for r in records])
blobs = timed("marshal.dumps each", lambda: [marshal.dumps(f) for f in flats])
back = timed("marshal.loads each", lambda: [marshal.loads(b) for b in blobs])
ds = [b for b, r in zip(back, records) if isinstance(r, Decision)]
timed(f"rebuild {len(ds)} decisions from tuples", lambda: [decision(t) for t in ds])
es = [b for b, r in zip(back, records) if isinstance(r, SpecEntry)]
timed(f"rebuild {len(es)} entries from tuples", lambda: [SpecEntry(*t[:5], None, t[6]) for t in es])
pick = timed("pickle.dumps of the whole list at once", lambda: pickle.dumps(records, 5))
timed("pickle.loads of the whole list at once", lambda: pickle.loads(pick))
whole = timed("marshal.dumps of all tuples at once", lambda: marshal.dumps(flats))
timed("marshal.loads of all tuples at once", lambda: marshal.loads(whole))
print(f"sizes: pickle {len(pick) / 1e6:.1f} MB, marshal {len(whole) / 1e6:.1f} MB")
with tempfile.TemporaryDirectory(dir="/var/tmp") as folder:
    db = sqlite3.connect(os.path.join(folder, "c.sqlite"))
    db.execute("create table p(path text, blob text, value blob, primary key (path, blob)) without rowid")
    rows = [(s.paths[r.id], r.id, b) for r, b in zip(records, blobs)]
    timed("sqlite insert of marshalled rows", lambda: (db.executemany("insert into p values (?,?,?)", rows), db.commit()))
    got = timed("sqlite select of every row", lambda: db.execute("select value from p").fetchall())
    timed("marshal.loads of every selected row", lambda: [marshal.loads(v) for (v,) in got])
