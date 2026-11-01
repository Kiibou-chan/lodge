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
