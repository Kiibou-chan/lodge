# Task 12 report

Implemented the differential run against lodge 0.2 without changing records, staging, committing, or pushing.

Files changed:

- `scripts/differential_dump.py` reads the store and the two core settings tables, derives the Python reference, and emits specification, sorted problems, formatted levels, search results, and rewrite hashes with original-text equality.
- `ts/scripts/differential.ts` computes the matching TypeScript object, compares nested keys and array positions, prints each difference with both values, prints counts, and sets the exit status.
- `scripts/differential.sh` creates a temporary reference under `.drafts/`, invokes both scripts, and removes the reference on exit.
- `ts/package.json` extends dependency-cruiser's inputs to include `scripts`.
- `ts/scripts/differential.test.ts` adds two tests using temporary synthetic stores only.
- This report records the results and limitations.

Tests and first failures:

- `differential compares an empty synthetic store and reports nested differences` was written before the implementation.
  Its first run failed at `expect(same.exitCode).toBe(0)` with `Expected: 0`, `Received: 1`, because `differential.ts` did not exist.
  It now checks successful comparison and counts, and a missing nested record key with its differing value and exit status 1.
- `both dumps rewrite duplicate record files and compare original CRLF bytes` was written before extending rewrite coverage and preserving input bytes.
  Its first run failed at `expect(Object.keys(dump.rewrite)).toHaveLength(2)` with `Expected length: 2`, `Received length: 1`.
  The implementation had selected rewrite paths from the loaded snapshot, which omits duplicate IDs.
  Both scripts now select every record-shaped path independently, skip parse problems, and preserve the original file text for equality.
  The test checks both rewritten paths, false equality for CRLF input, successful cross-language comparison, and the rewrite count.
- No carried core tests or core mutations were needed because the repository run found no core differences.
- No tests cannot hold in TypeScript.

Commands and results:

- `uv run --frozen --quiet lodge waiting`: last line `nothing`, with nothing waiting for either an agent or the author.
- `bun test ts/scripts/differential.test.ts`: first run reported `0 pass`, `1 fail`; the later regression run reported `1 pass`, `1 fail`; the final targeted run reported `2 pass`, `0 fail`, and `10 expect() calls`.
- `uv run --frozen ruff check --fix scripts/differential_dump.py`: initially fixed one import ordering error, ending `Found 1 error (1 fixed, 0 remaining).`
- `uv run --frozen ruff format scripts/differential_dump.py`: `1 file left unchanged`.
- `bunx --no-install biome check --write scripts` from `ts`: final run ended `Checked 2 files in 12ms. Fixed 2 files.`
- `bun --bun run tsc --noEmit -p .` from `ts`: initially failed with a nonexistent `split` export and mixed Map inference; corrected to `splitWords` and an explicit shared record type; the final run exited 0 with no output.
- `uv run --frozen ruff format --check scripts/differential_dump.py`: `1 file already formatted`.
- `uv run --frozen ruff check scripts/differential_dump.py`: `All checks passed!`.
- `sh scripts/differential.sh`: final output below, exit 0.

```text
350 records, 10 areas, 0 threads, 0 problems, 112 queries, 360 rewritten files
0 differences
```

There are no differing record IDs, keys, or core modules to list.
No record content is included in this report.
The scripts read records in place and write only the temporary reference, which the shell script removes.

Limitations and uncertainties:

- Bun TOML parsing collapses `5.0` to an integer-valued JavaScript number, whereas Python's TOML parser preserves a float that core settings reject.
  This repository has no `[length]` table, so the run is unaffected.
  The third plan must account for this distinction.
- The store contains no threads, so thread behaviour rests on the carried tests and Task 6's new test, as specified by the brief.
- The parsed settings are validated by both scripts; the compared read, derive, render, search, and write APIs do not accept settings.
- The coordinator still owns the full Python and TypeScript gate outside the sandbox, the external differential rerun, staging, committing, and pushing.

Final TypeScript gate: `sh scripts/check-ts.sh` exited 0.
Biome checked 105 files with no fixes, TypeScript and knip passed, and dependency-cruiser found no violations across 114 modules and 368 dependencies.
The last test lines were `851 pass`, `0 fail`, `2162 expect() calls`, and `Ran 851 tests across 56 files. [4.37s]`.
