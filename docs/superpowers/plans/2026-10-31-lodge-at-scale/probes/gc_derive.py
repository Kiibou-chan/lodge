"""Whether derive's growth is the collector's: derive and level 1 with the cyclic GC on, then frozen.

  python gc_derive.py STORE
"""

import gc
import os
import sys
import time

import yaml

from lodge import core
from lodge.core import yamlio


class _C(yaml.CSafeLoader):
    yaml_implicit_resolvers = {}
    yaml_constructors = yamlio._TextLoader.yaml_constructors


sys.modules["lodge.core.document"].load_yaml = lambda t: yaml.load(t, Loader=_C)
os.chdir(sys.argv[1])
from lodge.main import _make_lodge  # noqa: E402

w = _make_lodge()._w
current, _ = w.store.trees()
s = core.load(current)


def timed(label, fn):
    t = time.perf_counter()
    fn()
    print(f"{time.perf_counter() - t:7.3f} s  {label}", flush=True)


for mode in ("gc on", "gc frozen after load", "gc off"):
    if mode == "gc frozen after load":
        gc.collect()
        gc.freeze()
    if mode == "gc off":
        gc.disable()
    timed(f"derive, {mode}", lambda: core.derive(s))
    d = core.derive(s)
    timed(f"level1 of every record, {mode}", lambda: [core.level1(s, d, i, frozenset()) for i in [*s.decisions, *s.entries]])
