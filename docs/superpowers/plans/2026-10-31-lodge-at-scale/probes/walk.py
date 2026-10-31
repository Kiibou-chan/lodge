"""Cost of finding the working tree's files under lodge/ without reading them.

  python walk.py STORE
"""

import os
import subprocess
import sys
import time
from pathlib import Path

root = Path(sys.argv[1])
env = {**os.environ, "GIT_CONFIG_GLOBAL": "/dev/null", "GIT_CONFIG_NOSYSTEM": "1"}


def timed(label, fn):
    best = None
    for _ in range(3):
        t = time.perf_counter()
        out = fn()
        took = time.perf_counter() - t
        best = took if best is None else min(best, took)
    print(f"{best * 1000:7.1f} ms  {label}  ({out})")


def scandir_names():
    n = 0
    stack = [str(root / "lodge")]
    while stack:
        with os.scandir(stack.pop()) as it:
            for e in it:
                if e.is_dir(follow_symlinks=False):
                    stack.append(e.path)
                else:
                    n += 1
    return f"{n} files"


def dir_mtimes():
    n = 0
    stack = [str(root / "lodge")]
    seen = {}
    while stack:
        d = stack.pop()
        seen[d] = os.stat(d).st_mtime_ns
        with os.scandir(d) as it:
            for e in it:
                if e.is_dir(follow_symlinks=False):
                    stack.append(e.path)
        n += 1
    return f"{n} folders listed for folders"


folders = []
for dirpath, dirs, _ in os.walk(root / "lodge"):
    folders.append(dirpath)


def stat_folders():
    return f"{len({f: os.stat(f).st_mtime_ns for f in folders})} folders stat'ed"


def read_all():
    n = 0
    for dirpath, _, names in os.walk(root / "lodge"):
        for name in names:
            n += len((Path(dirpath) / name).read_bytes())
    return f"{n} bytes"


def git(*args):
    return lambda: f"{len(subprocess.run(['git', *args], cwd=root, env=env, capture_output=True, check=True).stdout)} bytes"


timed("os.scandir walk, names only", scandir_names)
timed("os.scandir walk of folders only", dir_mtimes)
timed("stat of every folder, list known", stat_folders)
timed("read every file (today's disk_tree work)", read_all)
timed("git diff-files --name-only -- lodge", git("diff-files", "--name-only", "-z", "--", "lodge"))
timed("git diff-index --cached --name-only HEAD -- lodge", git("diff-index", "--cached", "--name-only", "-z", "HEAD", "--", "lodge"))
timed("git ls-files -s -- lodge", git("ls-files", "-s", "-z", "--", "lodge"))
timed("git ls-files -o -- lodge (untracked, ignored too)", git("ls-files", "-o", "-z", "--", "lodge"))
timed("git status --porcelain=v2 --untracked-files=all --ignored -- lodge", git("status", "--porcelain=v2", "-z", "--untracked-files=all", "--ignored", "--", "lodge"))
timed("git rev-parse HEAD HEAD:lodge", git("rev-parse", "HEAD", "HEAD:lodge"))
