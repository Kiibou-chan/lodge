"""Time each phase of one checked read on a store, with `_missing` made linear and libyaml on.

  python phases.py STORE [--pure-yaml] [--profile OUT]

The two patches are what Task 2 and Task 3 build; nothing here changes the store.
"""

import cProfile
import os
import pickle
import sqlite3
import sys
import tempfile
import time
from collections.abc import Iterator

import yaml

from lodge import core
from lodge.core import yamlio
from lodge.core.check_state import problem_at
from lodge.core.model import Problem
from lodge.core.snapshot import Snapshot

args = sys.argv[1:]
store = args[0]
pure = "--pure-yaml" in args
profile = args[args.index("--profile") + 1] if "--profile" in args else None


def _missing(published: Snapshot, after: Snapshot) -> Iterator[Problem]:
    present = after.decisions.keys() | after.entries.keys() | after.threads.keys()
    for record_id in sorted({*published.decisions, *published.entries, *published.threads}):
        if record_id not in present:
            yield problem_at(published, record_id, 2, "was published and is missing from this state")


sys.modules["lodge.core.check_change"]._missing = _missing

if not pure:
    class _C(yaml.CSafeLoader):
        yaml_implicit_resolvers = {}
        yaml_constructors = yamlio._TextLoader.yaml_constructors

        def construct_scalar(self, node):
            return yamlio._PAIR.sub(yamlio._join_pair, yaml.constructor.BaseConstructor.construct_scalar(self, node))

        def construct_mapping(self, node, deep=False):
            seen = set()
            for key_node, _ in node.value:
                if isinstance(key_node, yaml.ScalarNode):
                    if key_node.value in seen:
                        raise yaml.constructor.ConstructorError(None, None, "duplicate key", key_node.start_mark)
                    seen.add(key_node.value)
            return yaml.constructor.SafeConstructor.construct_mapping(self, node, deep)

    fallbacks = [0]

    slow = yamlio.load_yaml

    def fast(text):
        try:
            return yaml.load(text, Loader=_C)
        except Exception:
            fallbacks[0] += 1
            return slow(text)

    sys.modules["lodge.core.document"].load_yaml = fast

os.chdir(store)
from lodge.main import _make_lodge  # noqa: E402

w = _make_lodge()._w
timings = {}


def phase(label, fn):
    t = time.perf_counter()
    out = fn()
    timings[label] = time.perf_counter() - t
    print(f"{timings[label]:8.3f} s  {label}", flush=True)
    return out


def run():
    current, published = phase("store.trees (walk and read, merge base, ls-tree, cat-file)", w.store.trees)
    s = phase("load(current)", lambda: core.load(current))
    phase("check_state(current)", lambda: core.check_state(s))
    d = phase("derive(current)", lambda: core.derive(s))
    p = phase("load(published)", lambda: core.load(published))
    phase("check_change(published, current)", lambda: core.check_change(p, s, w.settings, w.clock.now()))
    failing = frozenset()
    views = phase("level1 of every record", lambda: [core.level1(s, d, i, failing) for i in [*s.decisions, *s.entries]])
    phase("search_counted('berth crane', 20)", lambda: core.search_counted(s, d, "berth crane", core.Filters(), 20))
    records = {**s.decisions, **s.entries}
    blob = phase("pickle.dumps of every parsed record, one by one", lambda: [pickle.dumps(r, 5) for r in records.values()])
    phase("pickle.loads of every parsed record, one by one", lambda: [pickle.loads(b) for b in blob])
    with tempfile.TemporaryDirectory(dir="/var/tmp") as folder:
        db = sqlite3.connect(os.path.join(folder, "probe.sqlite"))
        db.execute("create table parsed(key text primary key, value blob) without rowid")
        db.execute("create table views(state integer, id text, line text, primary key(state, id)) without rowid")
        phase("sqlite insert of every parsed record", lambda: (db.executemany("insert into parsed values (?, ?)", zip(records, blob)), db.commit()))
        phase("sqlite select of every parsed record", lambda: db.execute("select value from parsed").fetchall())
        phase("sqlite insert of every level-1 line for one state", lambda: (db.executemany("insert into views values (1, ?, ?)", ((v.id, core.format_brief(v)) for v in views)), db.commit()))
        some = list(records)[:: max(1, len(records) // 10)]
        phase("sqlite select of ten level-1 lines", lambda: [db.execute("select line from views where state = 1 and id = ?", (i,)).fetchone() for i in some])
        print(f"index file: {os.path.getsize(os.path.join(folder, 'probe.sqlite')) / 1e6:.1f} MB")


if profile:
    cProfile.run("run()", profile)
else:
    run()
if not pure:
    print(f"C loader fell back {fallbacks[0]} times")
