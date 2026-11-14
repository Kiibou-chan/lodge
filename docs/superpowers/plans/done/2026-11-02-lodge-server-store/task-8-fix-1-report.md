# Task 8 fix round 1 report

Status: DONE_WITH_CONCERNS.

## Changes

- `ts/tests/app/fakes.ts:60`: filter attachment paths with `ATTACHMENTS`, which already ends in a slash.
- `ts/tests/store/interleaving.test.ts:44`: add a direct fake regression, a SQLite-backed attachment inclusion and forwarding probe, and a refusal test using a staged inner store.
- `ts/tests/store/wal.test.ts:47`: exercise the unexpected journal mode branch with SQLite's private temporary database, asserting both `LodgeError` and its message.
- `ts/knip.json:7`: remove the unnecessary helper entry, retaining ordinary dependency discovery through its tests.
  Task 9 therefore has no helper entry to remove.

## Test-first evidence

Before fixing the fake, `bun test tests/store/interleaving.test.ts tests/store/wal.test.ts` reported 6 pass and 1 fail.
`memory_store_attachment_texts_include_attachment_paths` failed at `ts/tests/store/interleaving.test.ts:49`: expected a map containing the attachment, received an empty map.
The other new tests exercise existing behaviour, so their first failures were established through the targeted mutations below before final verification.
Each mutation was applied separately and restored in a `finally` block.

| Mutation | Mutated handle | Command from `ts/` | First failure and result |
|---|---|---|---|
| H1: omit attachment texts from `files()` | `ts/tests/store/interleaving.ts:63` | `bun test tests/store/interleaving.test.ts` | SQLite probe at `ts/tests/store/interleaving.test.ts:60`, expected attachment map, received empty map; 4 pass, 1 fail, exit 1 |
| H12: forward an empty map | `ts/tests/store/interleaving.ts:13` | `bun test tests/store/interleaving.test.ts` | SQLite probe at `ts/tests/store/interleaving.test.ts:61`, expected attachment map, received empty map; existing forwarding assertion also fails; 3 pass, 2 fail, exit 1 |
| H7: remove the refusal throw | `ts/tests/store/interleaving.ts:68` | `bun test tests/store/interleaving.test.ts` | Refusal probe at `ts/tests/store/interleaving.test.ts:68`, expected rejection, received resolved promise; 4 pass, 1 fail, exit 1 |
| W2: remove the unexpected journal mode throw | `ts/src/store/schema.ts:65` | `bun test tests/store/wal.test.ts` | Temporary database probe at `ts/tests/store/wal.test.ts:54`, expected rejection, received resolved promise; 1 pass, 1 fail, exit 1 |

## Verification

- `uv run --frozen --quiet lodge waiting`: nothing waiting for an agent or the author.
- Focused tests after restoring all mutations: 7 pass, 0 fail, 29 assertions across 2 files.
- Biome initially requested import ordering in `wal.test.ts`; `bunx biome check --write tests/store/wal.test.ts` fixed that import order.
- Final gate: `sh scripts/check-ts.sh` exited 0, including knip without the removed entry.
  Last lines: 1129 pass, 0 fail, 2802 expect() calls, 84 files.
  Biome, TypeScript, dependency-cruiser, and knip all passed.
- No carried Python test was changed or found impossible in TypeScript.
- No module approaches the 300-line limit.

## Concern: journal mode contract

`openDatabase("")` opens SQLite's private temporary database, which cannot enter WAL, and currently rejects with `LodgeError("the database at  could not enter WAL mode")`.
The new test states and guards this existing behaviour without changing it.
The plan at `2026-11-02-lodge-server-store.md:390` requires setting the WAL pragma but does not explicitly require refusing every non-`:memory:` path that cannot enter WAL.
As instructed by this fix brief, the stricter policy is left unchanged and reported as a concern for the coordinator, rather than inferred as a new requirement.
