"""Replay synthetic-store reads, timing separate processes and comparing their output.

Commands are shell-style argument lists, parsed without invoking a shell.
"""

import argparse
import shlex
import shutil
import statistics
import subprocess
import tempfile
import time
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


def run(store: Path, command: list[str]) -> tuple[float, int, str]:
    start = time.perf_counter()
    result = subprocess.run(command, cwd=store, capture_output=True, text=True, check=False)
    return time.perf_counter() - start, result.returncode, result.stdout


def clear(cache: Path) -> None:
    if cache.exists():
        shutil.rmtree(cache)


def measure(store, build, commands, mode, runs, cache, entry):
    results = []
    with tempfile.TemporaryDirectory(prefix="read-cache-", dir=store.parent) as folder:
        saved = Path(folder) / "lodge"
        try:
            if mode == "changed":
                for _, args in commands:
                    run(store, [*build, *args])
                if cache.exists():
                    shutil.copytree(cache, saved)
            original = entry.read_text(encoding="utf-8")
            for _, args in commands:
                if mode == "seen":
                    run(store, [*build, *args])
                samples = []
                for number in range(1, runs + 1):
                    if mode in {"cold", "changed"}:
                        clear(cache)
                    if mode == "changed":
                        if saved.exists():
                            shutil.copytree(saved, cache)
                        entry.write_text(f"{original.rstrip()}\nBenchmark run {number}.\n")
                    samples.append(run(store, [*build, *args]))
                results.append(samples)
        finally:
            if mode == "changed":
                subprocess.run(["git", "checkout", "--", "lodge"], cwd=store, check=True)
    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("store", type=Path)
    parser.add_argument("--lodge", required=True)
    parser.add_argument("--against")
    parser.add_argument("--runs", type=int, default=3)
    parser.add_argument("--commands", type=Path, default=Path("scripts/bench_reads.txt"))
    parser.add_argument("--mode", choices=("cold", "seen", "changed"), default="seen")
    args = parser.parse_args()
    if args.runs < 1:
        parser.error("--runs must be positive")
    store = args.store.resolve()
    refs, entry = placeholders(store)
    commands = [
        (line, shlex.split(line.format_map(refs)))
        for line in args.commands.read_text().splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    gitdir = subprocess.check_output(
        ["git", "rev-parse", "--absolute-git-dir"], cwd=store, text=True
    ).strip()
    cache = Path(gitdir) / "lodge"
    if args.mode == "changed" and subprocess.check_output(
        ["git", "status", "--porcelain", "--", "lodge"], cwd=store
    ):
        parser.error("changed mode requires a clean lodge folder")
    builds = [shlex.split(args.lodge)]
    if args.against:
        builds.append(shlex.split(args.against))
    results = [
        measure(store, build, commands, args.mode, args.runs, cache, entry) for build in builds
    ]
    print(f"Mode: `{args.mode}`; store: `{store.name}`; runs: {args.runs}.")
    print()
    print("| Command | Build | Best (s) | Median (s) | Exit | Characters | Identical |")
    print("|---|---|---:|---:|---|---|---|")
    for index, (line, _) in enumerate(commands):
        identical = "n/a"
        if len(results) == 2:
            identical = str(
                [s[1:] for s in results[0][index]] == [s[1:] for s in results[1][index]]
            ).lower()
        for build_index, build_results in enumerate(results):
            samples = build_results[index]
            times = [sample[0] for sample in samples]
            exits = ", ".join(str(value) for value in sorted({s[1] for s in samples}))
            lengths = ", ".join(str(value) for value in sorted({len(s[2]) for s in samples}))
            label = "lodge" if build_index == 0 else "against"
            print(
                f"| `{line}` | {label} | {min(times):.3f} | {statistics.median(times):.3f} "
                f"| {exits} | {lengths} | {identical} |",
                flush=True,
            )


if __name__ == "__main__":
    main()
