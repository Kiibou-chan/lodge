# Planner report: lodge at scale

Written as the work goes; the probes are in `probes/`, run from the worktree root with `uv run --frozen python docs/superpowers/plans/2026-10-31-lodge-at-scale/probes/<name>.py`.

## Set-up

- Synthetic stores built on native ext4 with `scripts/bench_store.py`: `/var/tmp/lodge-bench/s900` (1,593 files, 0.75 s), `s9000` (16,008 files, 5.5 s), `s90000` (159,716 files, 63 s).
- SQLite here: the project's Python 3.13.5 links SQLite 3.47.1 with `ENABLE_FTS5`; `yaml.__with_libyaml__` is True.
- A code is `[A-Za-z0-9][A-Za-z0-9._-]*` (`src/lodge/core/fields.py:11`).

## Probes so far (native disk, best of 3 where repeated)

- Start-up: bare Python 0.025 s; `import lodge.main` 0.10 s from a native-disk venv with bytecode compiled, 0.25 s from a venv on a FUSE-mounted NTFS disk, 0.35 s on a native venv before its bytecode was written.
- `probes/walk.py` at 159,716 files: today's `disk_tree` read of every file 2.02 s; a names-only `os.scandir` walk 85 ms; `stat` of the 2,253 known folders 4.3 ms; `git diff-files` 45 ms; `git diff-index --cached HEAD` 12 ms; `git ls-files -s` 40 ms; `git ls-files -o` 134 ms; `git status --porcelain=v2 --untracked-files=all --ignored` 176 ms; `git rev-parse HEAD HEAD:lodge` 1.6 ms. At 16,008 files the same are 8, 8, 0.4, 200, 14, 4, 5, 12, 19, and 2 ms.
- git's untracked cache does not help a pathspec'd status here: 175 to 184 ms with `core.untrackedCache=true` set and the cache built, on a copy of the 160,000 store.
- `probes/phases.py` (with `_missing` linear and libyaml on): at 16,008 files `load` 0.67 s with libyaml against 3.47 s pure, the C loader fell back 0 times; `check_change` 0.60 s once `_missing` is linear (6.7 s of `_missing` alone in the unpatched profile); `check_state` 0.13 s, `derive` 0.056 s, level 1 of every record 0.035 s, one search 0.2 s, pickle of every record 0.06 s each way, SQLite insert of every parsed record 0.11 s, select of all 0.02 s, an index file of 48 MB.
- Gotcha for probes: `lodge.core.check_change` is the re-exported function, not the module, so a patch needs `sys.modules["lodge.core.check_change"]`; `document.py` binds `load_yaml` at import.
- The coordinator's measurement: one `lodge search berth --brief --limit 3` on the 159,716-file store on NTFS, this branch's build, did not finish within 900 s (`timeout 900`).
- `probes/phases.py` at 159,716 files (native disk, `_missing` linear, libyaml on): `store.trees` 5.48 s, `load(current)` 7.09 s, `check_state` 8.98 s, `derive` 1.39 s, `load(published)` 6.38 s, `check_change` 23.77 s, level 1 of every record 0.37 s, one search 2.20 s, pickle of every record 0.93 s out and 1.56 s back, SQLite insert of every parsed record 1.38 s, select of all 0.19 s, insert of every level-1 line 0.92 s, select of ten lines under 1 ms, index file 476 MB.
- So `check_state` is superlinear: 0.009 s, 0.13 s, 8.98 s at 1,593, 16,008, and 159,716 files (69 times for 10 times the records); `check_change` runs it twice and `derive` four times.
- `probes/gc_derive.py`: `derive` 0.043 s at 16,008 files and 1.32 s at 159,716 with the collector on, 0.91 s with it off; level 1 of every record 0.40 s and 0.34 s; a profile of `derive` alone shows no single hot spot (largest: `_reverse` 0.26 s cumulative), so its growth is spread, not one quadratic step.
- The 160,000 profile (`probes/phases.py --profile`): `check_areas`' generator over all entries per area takes 19.6 s (areas times entries); `derive` runs 8 times in one checked read (`check_state` through `check_areas`, `check_change` through `check_state` twice, `check_entries` twice, `_links_to_dead` twice).
- `probes/codec.py` at 16,008 files: marshal of plain tuples 0.011 s out, 0.014 s back, rebuilding the dataclasses 0.021 s, SQLite select of every row 0.012 s; pickle of the whole list 0.048 s out, 0.029 s back, and 1.56 s back one by one at 160,000.
- `probes/fts.py` at 159,716 files: FTS5 (`tokenize='ascii'`) over core's own words, 1.09 s to insert 157,466 rows, 52.8 MB; `"berth" OR "crane"` 0.156 s and 107,247 candidates, three words with AND 0.033 s; the synthetic vocabulary has 60 words, so every word matches most records and the store is a worst case for search.
- Brief lines on the synthetic store: ` · current` is 10 % of the characters of 200 lines under the default filter.
- `git check-attr --stdin` for text, eol, filter, ident, and working-tree-encoding over all 159,716 paths: 224 to 232 ms; `git ls-files --eol`: 1.43 s; `git config --get-regexp`: 2 ms.
- The coordinator's constraint: a read in a read-only sandbox, or with the database locked, never fails and never changes its output.
