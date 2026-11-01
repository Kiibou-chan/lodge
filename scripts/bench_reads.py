"""Replay synthetic-store reads, timing separate processes and comparing their output.

Commands are shell-style argument lists, parsed without invoking a shell.
"""

import argparse
import json
import os
import shlex
import shutil
import signal
import sqlite3
import statistics
import subprocess
import tempfile
import time
from hashlib import sha256
from pathlib import Path


def placeholders(store: Path) -> tuple[dict[str, str], Path]:
    records = []
    for path in sorted((store / "lodge").rglob("*.md")):
        if not path.name.startswith(("s-", "d-")):
            continue
        header = path.read_text(encoding="utf-8").split("\n---\n", 1)[0]
        fields = dict(line.split(": ", 1) for line in header.splitlines() if ": " in line)
        records.append((path, fields))
    entry = next((p, f) for p, f in records if f.get("kind") == "spec")
    decision = next(f for _, f in records if f.get("kind") == "decision")
    codes = [f["code"] for _, f in records if "code" in f]
    roots = {code.rsplit(".", 1)[0] for code in codes if "." in code}
    code = next(code for code in codes if code in roots)
    return {
        "entry": entry[1]["id"],
        "decision": decision["id"],
        "code": code,
        "code2": codes[1],
    }, entry[0]


def run(
    store: Path, command: list[str], timeout: float, env: dict[str, str] | None = None
) -> tuple[float, int | None, str | None]:
    start = time.perf_counter()
    try:
        result = subprocess.run(
            command,
            cwd=store,
            capture_output=True,
            text=True,
            check=False,
            timeout=timeout,
            env=env,
        )
    except subprocess.TimeoutExpired:
        return timeout, None, None
    return time.perf_counter() - start, result.returncode, result.stdout


def clear(cache: Path) -> None:
    if cache.exists():
        shutil.rmtree(cache)


def epochs(cache: Path) -> dict[str, int]:
    found = {}
    for path in sorted(cache.glob("index-*.sqlite")):
        try:
            db = sqlite3.connect(path.as_uri() + "?mode=ro", uri=True, timeout=0.2)
            try:
                found[path.name] = db.execute("SELECT epoch FROM meta").fetchone()[0]
            finally:
                db.close()
        except (sqlite3.Error, TypeError, ValueError):
            continue
    return found


def startup(store: Path, build: list[str], timeout: float, env: dict[str, str]) -> None:
    executable = Path(shutil.which(build[0]) or build[0])
    python = executable if executable.name.startswith("python") else executable.with_name("python")
    print("| Start-up | Best of nine (s) |")
    print("|---|---:|")
    for label, command in (
        ("python -c pass", [str(python), "-c", "pass"]),
        ("import lodge.main", [str(python), "-c", "import lodge.main"]),
        ("lodge guide --read", [*build, "guide", "--read"]),
    ):
        samples = [run(store, command, timeout=timeout, env=env) for _ in range(9)]
        if any(code != 0 for _, code, _ in samples):
            raise SystemExit(f"start-up command failed: {label}")
        print(f"| `{label}` | {min(s[0] for s in samples):.6f} |", flush=True)


def measure(store, build, commands, mode, runs, cache, entry, timeout, env=None):
    results = []
    with tempfile.TemporaryDirectory(prefix="read-cache-", dir=store.parent) as folder:
        saved = Path(folder) / "lodge"
        try:
            if mode in {"changed", "chained"}:
                for _, args in commands:
                    for _ in range(2):
                        run(store, [*build, *args], timeout=timeout, env=env)
                if mode == "changed" and cache.exists():
                    shutil.copytree(cache, saved)
            original = entry.read_text(encoding="utf-8")
            number = 0
            for line, args in commands:
                if mode == "seen":
                    for _ in range(2):
                        run(store, [*build, *args], timeout=timeout, env=env)
                samples = []
                for sample in range(1, runs + 1):
                    number += 1
                    if mode in {"cold", "changed"}:
                        clear(cache)
                    if mode in {"changed", "chained"}:
                        if mode == "changed" and saved.exists():
                            shutil.copytree(saved, cache)
                        entry.write_text(f"{original.rstrip()}\nBenchmark run {number}.\n")
                    before = epochs(cache) if mode == "chained" else {}
                    samples.append(run(store, [*build, *args], timeout=timeout, env=env))
                    if mode == "chained":
                        print(
                            "Epochs: "
                            + json.dumps(
                                {
                                    "command": line,
                                    "sample": sample,
                                    "exit": samples[-1][1],
                                    "stdout_sha256": (
                                        sha256(samples[-1][2].encode()).hexdigest()
                                        if samples[-1][2] is not None
                                        else None
                                    ),
                                    "before": before,
                                    "after": epochs(cache),
                                },
                                sort_keys=True,
                            ),
                            flush=True,
                        )
                results.append(samples)
        finally:
            if mode in {"changed", "chained"}:
                subprocess.run(["git", "checkout", "--", "lodge"], cwd=store, check=True, env=env)
    return results


def terminate(signum, _frame):
    raise SystemExit(128 + signum)


def main() -> None:
    signal.signal(signal.SIGTERM, terminate)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("store", type=Path)
    parser.add_argument("--lodge", required=True)
    parser.add_argument("--against")
    parser.add_argument("--timeout", type=float, default=900.0)
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--commands", type=Path, default=Path("scripts/bench_reads.txt"))
    parser.add_argument("--mode", choices=("cold", "seen", "changed", "chained"), default="seen")
    parser.add_argument(
        "--git-config",
        type=Path,
        metavar="FILE",
        help="global git config for every child, with system configuration and attributes off",
    )
    parser.add_argument(
        "--startup",
        action="store_true",
        help="measure the build's Python, imports, and reading guide, best of nine",
    )
    args = parser.parse_args()
    if args.runs < 1:
        parser.error("--runs must be positive")
    if args.timeout <= 0:
        parser.error("--timeout must be positive")
    store = args.store.resolve()
    env = dict(os.environ)
    if args.git_config is not None:
        env.update(
            GIT_CONFIG_GLOBAL=str(args.git_config.resolve()),
            GIT_CONFIG_NOSYSTEM="1",
            GIT_ATTR_NOSYSTEM="1",
        )
    builds = [shlex.split(args.lodge)]
    if args.against:
        builds.append(shlex.split(args.against))
    if args.startup:
        for build in builds:
            startup(store, build, args.timeout, env)
        return
    refs, entry = placeholders(store)
    commands = [
        (line, shlex.split(line.format_map(refs)))
        for line in args.commands.read_text().splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    gitdir = subprocess.check_output(
        ["git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
        cwd=store,
        text=True,
        env=env,
    ).strip()
    cache = Path(gitdir) / "lodge"
    if subprocess.check_output(["git", "status", "--porcelain", "--", "lodge"], cwd=store, env=env):
        parser.error("every mode requires a clean lodge folder")
    subprocess.run(["git", "update-index", "--refresh"], cwd=store, check=True, env=env)
    results = [
        measure(store, build, commands, args.mode, args.runs, cache, entry, args.timeout, env)
        for build in builds
    ]
    print(f"Mode: `{args.mode}`; store: `{store.name}`; runs: {args.runs}.")
    print()
    print("| Command | Build | Best (s) | Median (s) | Exit | Characters | Identical |")
    print("|---|---|---:|---:|---|---|---|")
    for index, (line, _) in enumerate(commands):
        identical = "n/a"
        if len(results) == 2:
            identical = str(
                all(s[1] is not None for build in results for s in build[index])
                and [s[1:] for s in results[0][index]] == [s[1:] for s in results[1][index]]
            ).lower()
        for build_index, build_results in enumerate(results):
            samples = build_results[index]
            times = [sample[0] for sample in samples]
            timed_out = any(s[1] is None for s in samples)
            exits = ", ".join(
                sorted({str(s[1]) if s[1] is not None else "timeout" for s in samples})
            )
            lengths = ", ".join(
                sorted({str(len(s[2])) if s[2] is not None else "n/a" for s in samples})
            )
            completed = [s[0] for s in samples if s[1] is not None]
            best = f"{min(completed):.3f}" if completed else f">{args.timeout:.3f}"
            median = (
                f"{'includes ' if completed else ''}>{args.timeout:.3f}"
                if timed_out
                else f"{statistics.median(times):.3f}"
            )
            label = "lodge" if build_index == 0 else "against"
            print(
                f"| `{line}` | {label} | {best} | {median} | {exits} | {lengths} | {identical} |",
                flush=True,
            )


if __name__ == "__main__":
    main()
