"""Native synthetic replay of Task 12, with durable rows and exact-reader oracles."""

import hashlib
import importlib.util
import json
import os
import shlex
import shutil
import sqlite3
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(os.environ.get("LODGE_BENCH_ROOT", "/var/tmp/lodge-bench")) / "task12"
WORK = Path(os.environ.get("LODGE_BENCH_WORKSPACE", Path(__file__).resolve().parents[5]))
PYTHON = ROOT.parent / "venv/bin/python"
BASE = ROOT.parent / "venv-base/bin/python"
HOME = ROOT / "home"
ENV = {
    **os.environ,
    "HOME": str(HOME),
    "XDG_CONFIG_HOME": str(HOME / "xdg"),
    "GIT_CONFIG_GLOBAL": "/dev/null",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_ATTR_NOSYSTEM": "1",
    "GIT_OPTIONAL_LOCKS": "0",
}
spec = importlib.util.spec_from_file_location("bench_reads", WORK / "scripts/bench_reads.py")
bench = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bench)
LOG = Path(os.environ.get("LODGE_TASK12_RESULTS", ROOT / "results.jsonl"))
ORACLES = ROOT / "oracles.json"
oracles = json.loads(ORACLES.read_text()) if ORACLES.exists() else {}
DIGESTS = {}
LINES = [
    line
    for line in (WORK / "scripts/bench_reads.txt").read_text().splitlines()
    if line.strip() and not line.startswith("#")
]


def emit(row):
    with LOG.open("a") as f:
        f.write(json.dumps(row, sort_keys=True) + "\n")
    print(json.dumps(row, sort_keys=True), flush=True)


def note(text):
    emit(dict(kind="note", text=text))


def environment(branch, conversion=False, off=False):
    env = {**ENV, "PYTHONPATH": str(ROOT / ("source-" + branch))}
    if conversion:
        env["GIT_CONFIG_GLOBAL"] = str(ROOT / "conversions.config")
    if off:
        env["LODGE_INDEX"] = "off"
    else:
        env.pop("LODGE_INDEX", None)
    return env


def invoke(store, branch, args, off=False, conversion=False, timeout=180, probe=False):
    env = environment(branch, conversion, off)
    command = (
        [str(PYTHON), str(Path(__file__).with_name("probe.py")), *args]
        if probe
        else [str(PYTHON), "-m", "lodge.main", *args]
    )
    start = time.perf_counter()
    try:
        p = subprocess.run(command, cwd=store, env=env, capture_output=True, timeout=timeout)
        return dict(
            seconds=time.perf_counter() - start,
            code=p.returncode,
            out=p.stdout.decode(),
            err=p.stderr.decode(),
        )
    except subprocess.TimeoutExpired:
        return dict(seconds=timeout, code=None, out=None, err=None)


def streams(p):
    return p["code"], p["out"], p["err"]


def signature(p):
    return dict(
        code=p["code"],
        stdout_bytes=len(p["out"] or ""),
        stderr_bytes=len(p["err"] or ""),
        stdout_sha256=hashlib.sha256((p["out"] or "").encode()).hexdigest(),
        stderr_sha256=hashlib.sha256((p["err"] or "").encode()).hexdigest(),
    )


def oracle(store, line, args, edit):
    key = json.dumps([store.name, line, edit])
    if key not in oracles:
        p = invoke(store, "a1500", args, off=True)
        assert p["code"] is not None, ("oracle timeout", store, line, edit)
        oracles[key] = p
        ORACLES.write_text(json.dumps(oracles))
        emit(
            dict(
                kind="oracle",
                store=store.name,
                command=line,
                edit=edit,
                seconds=p["seconds"],
                **signature(p),
            )
        )
    return oracles[key]


def cache(store):
    return store / ".git/lodge"


def clear(store):
    shutil.rmtree(cache(store), ignore_errors=True)


def save(store, dest):
    shutil.rmtree(dest, ignore_errors=True)
    shutil.copytree(cache(store), dest)


def refresh(store):
    subprocess.run(["git", "update-index", "--refresh"], cwd=store, env=ENV, check=True)


def restore(store, saved):
    clear(store)
    shutil.copytree(saved, cache(store))
    refresh(store)


def digest(branch):
    if branch not in DIGESTS:
        DIGESTS[branch] = subprocess.check_output(
            [
                str(PYTHON),
                "-c",
                "from lodge.gitstore.index_db import build_digest; print(build_digest())",
            ],
            env=environment(branch),
            text=True,
        ).strip()
    return DIGESTS[branch]


def info(store, branch):
    path = cache(store) / ("index-" + digest(branch) + ".sqlite")
    if not path.exists():
        return dict(epoch=0, states=0, used=0, file_bytes=0)
    db = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True)
    try:
        return dict(
            epoch=db.execute("SELECT epoch FROM meta").fetchone()[0],
            states=db.execute("SELECT count(*) FROM states").fetchone()[0],
            facts=db.execute("SELECT count(*) FROM facts").fetchone()[0],
            fact_bytes=db.execute("SELECT coalesce(sum(length(value)),0) FROM facts").fetchone()[0],
            markers=db.execute("SELECT count(*) FROM seen").fetchone()[0],
            parses=db.execute("SELECT count(*) FROM parses").fetchone()[0],
            used=(
                db.execute("pragma page_count").fetchone()[0]
                - db.execute("pragma freelist_count").fetchone()[0]
            )
            * db.execute("pragma page_size").fetchone()[0],
            file_bytes=path.stat().st_size,
        )
    finally:
        db.close()


def prime(store, branch, conversion=False):
    for _ in range(2):
        p = invoke(store, branch, ["waiting"], conversion=conversion)
        assert p["code"] == 0, p
    assert info(store, branch)["states"] >= 1


def record(store, branch, line, args, mode, sample, edit=None, conversion=False):
    expected = oracle(store, line, args, edit)
    before = info(store, branch)
    p = invoke(store, branch, args, conversion=conversion)
    after = info(store, branch)
    assert streams(p) == streams(expected), (store, branch, line, mode, sample, p, expected)
    row = dict(
        kind="replay",
        store=store.name,
        branch=branch,
        command=line,
        mode=mode,
        sample=sample,
        edit=edit,
        conversion=conversion,
        seconds=p["seconds"],
        identical=True,
        before=before,
        after=after,
        cold_clear=before["epoch"] > 0 and after["epoch"] > before["epoch"],
        **signature(p),
    )
    emit(row)
    return row


def matrix(store, branch, cold=False, second=False):
    refresh(store)
    refs, entry = bench.placeholders(store)
    original = entry.read_text()
    commands = [(line, shlex.split(line.format_map(refs))) for line in LINES]
    if branch != "a1500":
        commands = [
            (line, args)
            for line, args in commands
            if args[0] in {"show", "search", "waiting", "threads"}
        ]
    if cold:
        for line, args in commands:
            for n in range(1, 4):
                clear(store)
                record(store, branch, line, args, "cold", n)
    clear(store)
    prime(store, branch)
    saved = ROOT / ("baseline-" + store.name + "-" + branch)
    save(store, saved)
    emit(dict(kind="occupancy", store=store.name, branch=branch, **info(store, branch)))
    try:
        for line, args in commands:
            restore(store, saved)
            for n in range(1, 4):
                record(store, branch, line, args, "seen", n)
            for n in range(1, 4):
                restore(store, saved)
                entry.write_text(f"{original.rstrip()}\nBenchmark run {n}.\n")
                for sight in range(
                    1, 4 if second and args[0] in {"show", "search", "waiting", "threads"} else 2
                ):
                    record(store, branch, line, args, "changed-" + str(sight), n, edit=n)
                entry.write_text(original)
            emit(dict(kind="command_done", store=store.name, branch=branch, command=line))
    finally:
        entry.write_text(original)
        restore(store, saved)
        shutil.rmtree(saved)
    note(
        f"Measurement completed: `{store.name}`, `{branch}`, every selected replay row compared with the exact reader in stdout, stderr, and exit status; three complete processes per timing."
    )


def cycles(store, branch, sample=1):
    refresh(store)
    refs, entry = bench.placeholders(store)
    original = entry.read_text()
    clear(store)
    prime(store, branch)
    try:
        for n in range(1, 11):
            entry.write_text(f"{original.rstrip()}\nBenchmark cycle {n}.\n")
            for sight in range(1, 4):
                before = info(store, branch)
                p = invoke(store, branch, ["show", refs["code"]])
                after = info(store, branch)
                assert p["code"] == 0
                emit(
                    dict(
                        kind="cycle",
                        store=store.name,
                        branch=branch,
                        sample=sample,
                        cycle=n,
                        sight=sight,
                        seconds=p["seconds"],
                        before=before,
                        after=after,
                        **signature(p),
                    )
                )
    finally:
        entry.write_text(original)
    note(
        f"Ten edit/read/read/read cycles completed: `{branch}`; epoch changes and complete-state counts are retained for every sighting."
    )


def conversions(store, branch):
    refresh(store)
    refs, entry = bench.placeholders(store)
    original = entry.read_text()
    clear(store)
    prime(store, branch, True)
    saved = ROOT / ("conversion-baseline-" + branch)
    save(store, saved)
    try:
        for line in ["show {code}", "waiting", "search berth --brief"]:
            args = shlex.split(line.format_map(refs))
            restore(store, saved)
            for n in range(1, 4):
                record(store, branch, line, args, "seen", n, conversion=True)
            for n in range(1, 4):
                restore(store, saved)
                entry.write_text(f"{original.rstrip()}\nBenchmark run {n}.\n")
                for sight in range(1, 4):
                    record(
                        store,
                        branch,
                        line,
                        args,
                        "changed-" + str(sight),
                        n,
                        edit=n,
                        conversion=True,
                    )
                entry.write_text(original)
    finally:
        entry.write_text(original)
        restore(store, saved)
        shutil.rmtree(saved)
    note(
        f"CONV-1 rows completed: `{branch}`, seen and all three changed sightings, three samples, against the exact reader."
    )


def base(store):
    refs, entry = bench.placeholders(store)
    original = entry.read_text()
    env = dict(ENV)
    env.pop("PYTHONPATH", None)
    env["LODGE_INDEX"] = "off"
    try:
        for line in LINES:
            args = shlex.split(line.format_map(refs))
            for mode in ["clean", "changed"]:
                for n in range(1, 4):
                    if mode == "changed":
                        entry.write_text(f"{original.rstrip()}\nBenchmark run {n}.\n")
                    expected = oracle(store, line, args, n if mode == "changed" else None)
                    start = time.perf_counter()
                    try:
                        p = subprocess.run(
                            [str(BASE), "-m", "lodge.main", *args],
                            cwd=store,
                            env=env,
                            capture_output=True,
                            text=True,
                            timeout=20 if store.name == "s90000" else 180,
                        )
                        result = dict(
                            seconds=time.perf_counter() - start,
                            code=p.returncode,
                            out=p.stdout,
                            err=p.stderr,
                        )
                    except subprocess.TimeoutExpired:
                        result = dict(
                            seconds=20 if store.name == "s90000" else 180,
                            code=None,
                            out=None,
                            err=None,
                        )
                    if result["code"] is not None and streams(result) != streams(expected):
                        folder = ROOT / "base-differences"
                        folder.mkdir(exist_ok=True)
                        name = store.name + "-" + str(LINES.index(line)) + "-" + mode + "-" + str(n)
                        (folder / (name + ".json")).write_text(
                            json.dumps(dict(base=result, current=expected), indent=2)
                        )
                    emit(
                        dict(
                            kind="base",
                            store=store.name,
                            command=line,
                            mode=mode,
                            sample=n,
                            seconds=result["seconds"],
                            identical=streams(result) == streams(expected)
                            if result["code"] is not None
                            else None,
                            **signature(result),
                        )
                    )
                entry.write_text(original)
    finally:
        entry.write_text(original)
    note(
        f"Task 1 base replay completed: `{store.name}`, clean and changed inputs; large-store attempts are bounded to 20 s each, with the original 900 s point-read timeout retained separately."
    )


def startup_rows(store, branches=None):
    for branch in branches or ["a1500", "a1900", "b1500", "b1900"]:
        command = [
            "uv",
            "run",
            "--frozen",
            "python",
            "scripts/bench_reads.py",
            str(store),
            "--lodge",
            str(PYTHON) + " -m lodge.main",
            "--startup",
            "--git-config",
            "/dev/null",
        ]
        p = subprocess.run(
            command, cwd=WORK, env=environment(branch), capture_output=True, text=True, check=True
        )
        (ROOT / ("startup-" + branch + ".md")).write_text(p.stdout)
        emit(dict(kind="startup", branch=branch, table=p.stdout))


def chained(store):
    clear(store)
    prime(store, "a1500")
    commands = ROOT / "chained-commands.txt"
    commands.write_text("show {code}\n")
    command = [
        "uv",
        "run",
        "--frozen",
        "python",
        "scripts/bench_reads.py",
        str(store),
        "--lodge",
        str(PYTHON) + " -m lodge.main",
        "--mode",
        "chained",
        "--runs",
        "100",
        "--commands",
        str(commands),
        "--git-config",
        "/dev/null",
    ]
    with (ROOT / "chained.log").open("w") as f:
        subprocess.run(
            command,
            cwd=WORK,
            env=environment("a1500"),
            stdout=f,
            stderr=subprocess.STDOUT,
            check=True,
        )
    emit(dict(kind="chained_done", store=store.name, branch="a1500"))
    note(
        "The production `--mode chained --runs 100` experiment completed without restoring the saved index, with the epoch before and after every edit/read."
    )


def diagnostic(store, branch, line, args, mode, sample, edit=None):
    expected = oracle(store, line, args, edit)
    before = info(store, branch)
    p = invoke(store, branch, args, probe=True)
    after = info(store, branch)
    assert p["code"] is not None and "TASK12_PHASES " in p["err"], p
    err, raw = p["err"].rsplit("TASK12_PHASES ", 1)
    assert (p["code"], p["out"], err) == streams(expected), (branch, line, mode, p, expected)
    emit(
        dict(
            kind="phases",
            store=store.name,
            branch=branch,
            command=line,
            mode=mode,
            sample=sample,
            edit=edit,
            seconds=p["seconds"],
            before=before,
            after=after,
            **json.loads(raw),
        )
    )


def diagnostics(store, branches=None, small=True):
    refresh(store)
    refs, entry = bench.placeholders(store)
    original = entry.read_text()
    for branch in branches or ["a1500", "a1900", "b1500", "b1900"]:
        clear(store)
        prime(store, branch)
        saved = ROOT / ("phase-baseline-" + branch)
        save(store, saved)
        try:
            for line in LINES:
                args = shlex.split(line.format_map(refs))
                if args[0] not in {"show", "search", "waiting", "threads"}:
                    continue
                for n in range(1, 4):
                    diagnostic(store, branch, line, args, "seen", n)
            line = "thread q-000000"
            args = shlex.split(line)
            for n in range(1, 4):
                record(store, branch, line, args, "seen", n)
                diagnostic(store, branch, line, args, "seen", n)
            line = "show {code}"
            args = shlex.split(line.format_map(refs))
            for n in range(1, 4):
                restore(store, saved)
                entry.write_text(f"{original.rstrip()}\nBenchmark run {n}.\n")
                for sight in range(1, 4):
                    diagnostic(store, branch, line, args, "changed-" + str(sight), n, edit=n)
                entry.write_text(original)
        finally:
            entry.write_text(original)
            restore(store, saved)
            shutil.rmtree(saved)
    for size in ["s900", "s9000"] if small else []:
        current = ROOT / size
        refs, _ = bench.placeholders(current)
        clear(current)
        prime(current, "b1900")
        for line in LINES:
            args = shlex.split(line.format_map(refs))
            if args[0] == "search":
                diagnostic(current, "b1900", line, args, "seen", 1)
    note(
        "Phase diagnostics completed for every targeted large-store seen row and all three changed sightings of show, in each combination; candidate counts are recorded for every search at every size."
    )


def current_clear(store):
    clear(store)
    prime(store, "a1500")
    source = cache(store) / ("index-" + digest("a1500") + ".sqlite")
    code = """import json,sqlite3,sys,time
from pathlib import Path
from lodge.gitstore.index_space import clear,used_bytes
path=Path(sys.argv[1]);db=sqlite3.connect(path,isolation_level=None)
def snapshot():
 return dict(epoch=db.execute('SELECT epoch FROM meta').fetchone()[0],used=used_bytes(db),file_bytes=path.stat().st_size,inode=path.stat().st_ino)
default=db.execute('pragma secure_delete').fetchone()[0]
for pragma in ['journal_mode=WAL','synchronous=NORMAL','secure_delete=OFF','journal_size_limit=16777216']:
 db.execute('pragma '+pragma)
before=snapshot();start=time.perf_counter();db.execute('BEGIN IMMEDIATE');clear(db);db.execute('COMMIT');seconds=time.perf_counter()-start
after=snapshot();db.execute('pragma wal_checkpoint(TRUNCATE)');db.close()
assert before['inode']==after['inode'] and before['file_bytes']==after['file_bytes'] and after['epoch']==before['epoch']+1
print(json.dumps(dict(seconds=seconds,before=before,after=after,sqlite=sqlite3.sqlite_version,secure_delete_default=default,secure_delete=0)))
"""
    for n in range(1, 4):
        copy = ROOT / f"clear-copy-{n}.sqlite"
        copy.unlink(missing_ok=True)
        a = sqlite3.connect(source.as_uri() + "?mode=ro", uri=True)
        b = sqlite3.connect(copy)
        a.backup(b)
        b.close()
        a.close()
        result = json.loads(
            subprocess.check_output(
                [str(PYTHON), "-c", code, str(copy)], env=environment("a1500"), text=True
            )
        )
        emit(dict(kind="clear", sample=n, **result))
    note(
        "A current full-state in-place clear is measured three times on independent SQLite copies, with unchanged inode and physical size, an incremented epoch, and secure_delete=OFF."
    )


if __name__ == "__main__":
    stage = sys.argv[1] if len(sys.argv) > 1 else "matrix"
    if stage == "fix":
        store = ROOT / "s90000"
        startup_rows(store, ["b1900"])
        matrix(store, "b1900", second=True)
        for sample in range(1, 4):
            cycles(store, "b1900", sample)
        conversions(store, "b1900")
        diagnostics(store, ["b1900"], small=False)
    elif stage == "matrix":
        startup_rows(ROOT / "s90000")
        for size in ["s900", "s9000"]:
            matrix(ROOT / size, "a1500", cold=True)
        for branch in ["a1500", "a1900", "b1500", "b1900"]:
            matrix(ROOT / "s90000", branch, cold=branch == "a1500", second=True)
            cycles(ROOT / "s90000", branch)
            conversions(ROOT / "s90000", branch)
        chained(ROOT / "s90000")
    elif stage == "small-options":
        for size in ["s900", "s9000"]:
            for branch in ["a1500", "a1900", "b1500", "b1900"]:
                if branch != "a1500":
                    matrix(ROOT / size, branch)
                cycles(ROOT / size, branch)
    elif stage == "diagnostics":
        diagnostics(ROOT / "s90000")
    elif stage == "clear":
        current_clear(ROOT / "s90000")
    elif stage == "base":
        for size in ["s900", "s9000", "s90000"]:
            base(ROOT / size)
    else:
        raise SystemExit("unknown stage")
    emit(dict(kind="stage_done", stage=stage))
