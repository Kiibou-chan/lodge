"""Check complete experimental coverage and the recorded stream comparisons."""

import os
import hashlib
import json
import sys
from pathlib import Path

root = Path(os.environ.get("LODGE_BENCH_ROOT", "/var/tmp/lodge-bench")) / "task12"
work = Path(os.environ.get("LODGE_BENCH_WORKSPACE", Path(__file__).resolve().parents[5]))
rows = [json.loads(l) for l in (root / "results.jsonl").read_text().splitlines()]
lines = (work / "scripts/bench_reads.txt").read_text().splitlines()
targets = [l for l in lines if l.split()[0] in {"show", "search", "waiting", "threads"}]
branches = ["a1500", "a1900", "b1500", "b1900"]
sizes = ["s900", "s9000", "s90000"]
if "--fix" in sys.argv:
    rows = [json.loads(line) for line in (root / "results-fix.jsonl").read_text().splitlines()]
    references = json.loads((root / "oracles.json").read_text())
    replay = [r for r in rows if r["kind"] == "replay"]
    expected = {
        (line, mode, n, False)
        for line in targets
        for mode in ["seen", "changed-1", "changed-2", "changed-3"]
        for n in range(1, 4)
    }
    expected |= {
        (line, mode, n, True)
        for line in ["show {code}", "waiting", "search berth --brief"]
        for mode in ["seen", "changed-1", "changed-2", "changed-3"]
        for n in range(1, 4)
    }
    expected |= {("thread q-000000", "seen", n, False) for n in range(1, 4)}
    actual = [(r["command"], r["mode"], r["sample"], r["conversion"]) for r in replay]
    assert len(actual) == len(set(actual)) and set(actual) == expected
    assert len(replay) == 195 and all(r["identical"] for r in replay)
    assert all(r["before"] == r["after"] for r in replay if r["mode"] in {"seen", "changed-3"})
    cycles = [r for r in rows if r["kind"] == "cycle"]
    assert len(cycles) == 90
    assert {(r["sample"], r["cycle"], r["sight"]) for r in cycles} == {
        (s, c, t) for s in range(1, 4) for c in range(1, 11) for t in range(1, 4)
    }
    reference = references[json.dumps(["s90000", "show {code}", 1])]
    for r in cycles:
        assert r["code"] == reference["code"]
        assert r["stdout_sha256"] == hashlib.sha256(reference["out"].encode()).hexdigest()
        assert r["stderr_sha256"] == hashlib.sha256(reference["err"].encode()).hexdigest()
    phases = [r for r in rows if r["kind"] == "phases"]
    expected = {
        (line, "seen", s) for line in [*targets, "thread q-000000"] for s in range(1, 4)
    } | {
        ("show {code}", m, s) for m in ["changed-1", "changed-2", "changed-3"] for s in range(1, 4)
    }
    assert (
        len(phases) == 51 and {(r["command"], r["mode"], r["sample"]) for r in phases} == expected
    )
    assert all(sum(r["stages"].values()) <= r["app_seconds"] + 0.01 for r in phases)
    assert all(r["store"] == "s90000" and r["branch"] == "b1900" for r in replay + cycles + phases)
    print(
        json.dumps(
            dict(
                replay_samples=len(replay),
                cycle_samples=len(cycles),
                phase_samples=len(phases),
                cycle_samples_per_sequence=3,
                cycle_clears=sum(r["after"]["epoch"] - r["before"]["epoch"] for r in cycles),
            ),
            sort_keys=True,
        )
    )
    raise SystemExit(0)
expected = set()
for size in sizes:
    for branch in branches:
        for line in targets:
            for mode in ["seen", "changed-1"] + (
                ["changed-2", "changed-3"] if size == "s90000" else []
            ):
                for n in range(1, 4):
                    expected.add((size, branch, False, line, mode, n))
    for line in lines:
        for n in range(1, 4):
            expected.add((size, "a1500", False, line, "cold", n))
        if line not in targets:
            for mode in ["seen", "changed-1"]:
                for n in range(1, 4):
                    expected.add((size, "a1500", False, line, mode, n))
for branch in branches:
    for line in ["show {code}", "waiting", "search berth --brief"]:
        for mode in ["seen", "changed-1", "changed-2", "changed-3"]:
            for n in range(1, 4):
                expected.add(("s90000", branch, True, line, mode, n))
    for n in range(1, 4):
        expected.add(("s90000", branch, False, "thread q-000000", "seen", n))
replay = [r for r in rows if r["kind"] == "replay"]
actual = [
    (r["store"], r["branch"], r["conversion"], r["command"], r["mode"], r["sample"]) for r in replay
]
assert len(actual) == len(set(actual)), "duplicate replay samples"
assert set(actual) == expected, (len(expected - set(actual)), len(set(actual) - expected))
assert len(replay) == 1602 and all(r["identical"] for r in replay)
assert all(r["before"] == r["after"] for r in replay if r["mode"] in {"seen", "changed-3"}), (
    "seen metadata changed"
)
references = json.loads((root / "oracles.json").read_text())
cycles = [r for r in rows if r["kind"] == "cycle"]
assert len(cycles) == 360
assert len({(r["store"], r["branch"], r["cycle"], r["sight"]) for r in cycles}) == 360
for r in cycles:
    p = references[json.dumps([r["store"], "show {code}", 1])]
    assert r["code"] == p["code"]
    assert r["stdout_sha256"] == hashlib.sha256(p["out"].encode()).hexdigest()
    assert r["stderr_sha256"] == hashlib.sha256(p["err"].encode()).hexdigest()
base = [r for r in rows if r["kind"] == "base"]
assert len(base) == 288
assert len({(r["store"], r["command"], r["mode"], r["sample"]) for r in base}) == 288
assert all(
    r["identical"] is True
    for r in base
    if r["code"] is not None and r["command"].split()[0] not in {"show", "search"}
)
phases = [r for r in rows if r["kind"] == "phases"]
assert len(phases) == 216
assert len({(r["store"], r["branch"], r["command"], r["mode"], r["sample"]) for r in phases}) == 216
assert all(sum(r["stages"].values()) <= r["app_seconds"] + 0.01 for r in phases)
clears = [r for r in rows if r["kind"] == "clear"]
assert len(clears) == 3
assert all(
    r["after"]["epoch"] == r["before"]["epoch"] + 1
    and r["after"]["inode"] == r["before"]["inode"]
    and r["after"]["file_bytes"] == r["before"]["file_bytes"]
    and r["secure_delete"] == 0
    for r in clears
)
chain = [
    json.loads(l.removeprefix("Epochs: "))
    for l in (root / "chained.log").read_text().splitlines()
    if l.startswith("Epochs: ")
]
assert len(chain) == 100
reference = references[json.dumps(["s90000", "show {code}", 1])]
assert all(
    r["exit"] == reference["code"]
    and r["stdout_sha256"] == hashlib.sha256(reference["out"].encode()).hexdigest()
    for r in chain
)
print(
    json.dumps(
        dict(
            replay_samples=len(replay),
            cycle_samples=len(cycles),
            base_samples=len(base),
            base_timeouts=sum(r["code"] is None for r in base),
            phase_samples=len(phases),
            clear_samples=len(clears),
            chained_samples=len(chain),
            chained_clears=sum(
                sum(max(0, v - r["before"].get(k, v)) for k, v in r["after"].items()) for r in chain
            ),
        ),
        sort_keys=True,
    )
)
