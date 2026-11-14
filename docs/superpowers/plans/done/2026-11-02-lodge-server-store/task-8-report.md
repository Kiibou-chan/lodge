# Task 8 report

Implemented two writers at once on `server-store-b`.
The task brief's explicit commit and push instructions take precedence over its repeated sandbox-era global constraint.

## Changes by file

- `ts/tests/store/concurrent.test.ts`: carries all three Python titles and their assertions over SQLite events, with separate connections to one temporary file, two stores over one connection, and a stale publish that leaves the project's revision unchanged.
  The separate-connection case reads the final state through a third connection.
  Both interleaved adds assert the publication outcomes, three entries, three decisions, area order, and a successful state check.
- `ts/tests/store/interleaving.ts`: adds `Interleaved`, which runs another Lodge's add once after reading, and `Interleaving`, which queues intervening publications, counts attempts, snapshots successful writes and messages, and includes attachments in `files()`.
  Both forward the remaining current Store methods.
- `ts/tests/store/interleaving.test.ts`: tests queued rejections, successful publication snapshots, stale reads, attachment inclusion, and forwarding.
- `ts/tests/store/wal.test.ts`: reproduces parked review finding m-2 using another process holding a read transaction on a new temporary database.
  The child signals readiness before the tested open, and the test closes connections and removes its temporary directory.
- `ts/src/store/schema.ts`: sets the busy timeout before requesting WAL and checks the returned mode, allowing SQLite's forced `memory` mode for `:memory:` and refusing unexpected modes with `LodgeError`.
- `ts/knip.json`: adds the helper module to entry points for Task 9's later reader.
- `ts/tests/parity.json`: marks the concurrency row ported and assigns Task 8.

## Test-first evidence

The concurrency tests were written and run before their helper existed.
The helper tests were then written and run before its implementation existed.
After implementation, the revision predicate in `touchHead` was temporarily removed, all three carried tests failed, and the original file was restored byte for byte.
No mutation remains in the commit.

| Test | First failure or targeted mutation failure |
|---|---|
| `two_clones_add_at_once` | Missing `./interleaving.ts` initially; removing the `rev` predicate subsequently gave `["published"]` instead of `["rejected", "published"]`. |
| `two_worktrees_of_one_clone_add_interleaved` | Missing `./interleaving.ts` initially; the same predicate mutation gave `["published"]` instead of `["rejected", "published"]`. |
| `stale_tree_publish_rejected_ref_unchanged` | Missing `./interleaving.ts` initially; the predicate mutation returned `"published"` instead of `"rejected"`. |
| `reject_next_lands_one_change_per_attempt_and_records_only_publications` | `Cannot find module './interleaving.ts'`. |
| `moves_after_read_returns_stale_tree_and_files_include_attachments` | `Cannot find module './interleaving.ts'`. |
| `contended_first_open_enters_wal` | Expected `journal_mode: "wal"`, received `journal_mode: "delete"`, before changing schema initialisation. |

## Commands and results

| Command | Last output or result |
|---|---|
| `uv run --frozen --quiet lodge waiting` | Nothing waiting for an agent or the author. |
| `cd ts && bun test tests/store/concurrent.test.ts` before helper | `0 pass`, `1 fail`, `1 error`; missing helper module. |
| `cd ts && bun test tests/store/interleaving.test.ts` before helper | `0 pass`, `1 fail`, `1 error`; missing helper module. |
| `cd ts && bun test tests/store` after helper | `54 pass`, `0 fail`, `165 expect() calls`, eight files. |
| `cd ts && bun test tests/store/wal.test.ts` before fix | `0 pass`, `1 fail`, two assertions; journal mode remained `delete`. |
| `cd ts && bun test tests/store/wal.test.ts` after fix | `1 pass`, `0 fail`, three assertions. |
| `cd ts && bun test tests/store/concurrent.test.ts` with revision predicate removed | `0 pass`, `3 fail`, nine assertions. |
| `cd ts && bunx biome check --write` with the seven changed TypeScript and JSON paths | `Checked 7 files in 5ms. Fixed 4 files.` |
| `sh scripts/check-ts.sh` after restoring the mutation | Exit 0; Biome clean, TypeScript clean, no dependency violations, knip clean; `1125 pass`, `0 fail`, `2793 expect() calls`, 84 files. |

The final gate is repeated after writing this report, before staging explicit paths, committing with the required identity and Codex trailer, and pushing `server-store-b`.
The coordinator's whole gate and ledger update remain the coordinator's work.

## TypeScript adaptations and concerns

No carried assertion is impossible in TypeScript.
Git clone, worktree, remote-reference, and remote-tip mechanics become separate SQLite connections, shared-database stores, the project's revision, and a fresh reader, respectively, as the task requires.
All test data is synthetic, all databases are temporary or in memory, and no test uses the network or a real repository.
No packages were installed or added.
Task 7b's parked caller-base trust issue remains outside this task.
No unresolved implementation uncertainty was found.
