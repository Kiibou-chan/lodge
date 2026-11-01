# Task 12 measurement tools

These scripts retain the Task 12 experiment and its fix-round rerun on synthetic stores.
`LODGE_BENCH_ROOT` defaults to `/var/tmp/lodge-bench`; stores, source copies, logs, and the native `venv` and historical `venv-base` live below it.
`LODGE_BENCH_WORKSPACE` defaults to this checkout, derived from the scripts' location.
The native environments must already contain the corresponding dependencies, and `scripts/bench_store.py` supplies `s900`, `s9000`, and `s90000` at the benchmark root.
Run stages sequentially while other CPU-heavy work is idle.

From the checkout, recreate the initial four-way source comparison with:

```sh
tools=docs/superpowers/plans/2026-10-31-lodge-at-scale/task12-tools
uv run --frozen python "$tools/setup.py" --source-ref bb9fe48
uv run --frozen python "$tools/measure.py" matrix
uv run --frozen python "$tools/measure.py" small-options
uv run --frozen python "$tools/measure.py" base
uv run --frozen python "$tools/measure.py" diagnostics
uv run --frozen python "$tools/measure.py" clear
uv run --frozen python "$tools/audit.py"
```

For the final production rerun, retain the initial `results.jsonl` and `oracles.json`, and run:

```sh
tools=docs/superpowers/plans/2026-10-31-lodge-at-scale/task12-tools
uv run --frozen python "$tools/setup.py" --production-only
LODGE_TASK12_RESULTS="${LODGE_BENCH_ROOT:-/var/tmp/lodge-bench}/task12/results-fix.jsonl" \
  uv run --frozen python "$tools/measure.py" fix
uv run --frozen python "$tools/audit.py" --fix
uv run --frozen python "$tools/render.py"
```

The `fix` stage records every targeted s90000 seen and changed sighting, three independent ten-edit cycles, CONV-1, best-of-nine start-up, every seen phase diagnostic, and changed-show diagnostics.
A run appends durable rows, so use a fresh results filename for a new experiment.
Setup refreshes each store's git index once after cloning or reusing it, and measurement refreshes it after restoring baselines and before reads.
These explicit `git update-index --refresh` calls are outside all timed reads.
The renderer replaces the remeasured s90000 R11-B / 1,900 groups in place, preserving the other combinations and the smaller-store rows.
The audit checks sample coverage, exact-reader streams, seen metadata stability, and cycle output digests.
`probe.py` wraps only the diagnostic child and adds an exclusive phase trailer to stderr; ordinary production reads contain no instrumentation.

`relist.py` reproduces the I-A new-commit and cold-index identity measurements on an independent synthetic copy, with three samples and every git process counted through `subprocess.Popen`, including store construction.
To compare the code before this round with production, extract only the old application sources into the benchmark area, compile them, and use the same frozen workspace Python for both runs:

```sh
tools=docs/superpowers/plans/2026-10-31-lodge-at-scale/task12-tools
bench_root="${LODGE_BENCH_ROOT:-/var/tmp/lodge-bench}"
mkdir -p "$bench_root/task12-fix/source-before"
git archive 98cc34e src/lodge | tar -x -C "$bench_root/task12-fix/source-before"
uv run --frozen python -m compileall -q "$bench_root/task12-fix/source-before/src"
PYTHONPATH="$bench_root/task12-fix/source-before/src" \
  uv run --frozen python "$tools/relist.py" --label before
PYTHONPATH="$PWD/src" uv run --frozen python "$tools/relist.py" --label after
```

Each sample commits a distinct synthetic file edit, then measures a full relist against the changed base and a second full relist with a cold lodge index.
The explicit git-index refresh is outside the timed region in both cases.
