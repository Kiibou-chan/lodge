# Task 8a report

Status: Task 4 fix round committed and pushed as `a68be3c`; Task 8a complete.
Nothing waits for an agent.
The required decisions, including d-xc4nz9, d-q0tb8r, d-zyqzkg, and d-c0q20c, were read through `lodge show --reasoning`.
No record files were opened or written.

## Scope and existing grouping

Task 8a adds byte-derived blob IDs to exact trees and separates per-file parsing from snapshot assembly without changing the read ports.
The Task 7 report's statement that `written_order` grouping is deferred is stale.
Task 6 already groups current specification entries once per render at `src/lodge/core/render.py:42-44`, constructs an area-local snapshot at line 73, and calls `written_order(local, d, name)` at line 82.
`written_order` still scans its input at `src/lodge/core/order.py:33`, but that input now contains only the area's current entries.
The Task 6 commit's grouping claim is true; the implementation is left as is.

## Skeleton

The new leaf module declares `blob_id` and `Listing`; `Tree` gains a defaulted `blobs` mapping, and snapshot declares `Parsed`, `parse_file`, and `assemble`.
Concrete new function bodies raise `NotImplementedError`; core's front door exports all produced names.

Before writing tests, `uv run --frozen pytest tests/test_structure.py -q` passed 39 tests in 0.35 s, and `uv run --frozen mypy` passed on 225 source files.

## Failing tests

All six required test functions were written and run before implementation with `uv run --frozen pytest tests/core/test_listing.py tests/gitstore/test_tree_blobs.py -q`.
Their 18 parametrised cases failed, with repeated traces omitted:

```text
E       NotImplementedError
src/lodge/core/listing.py:9: NotImplementedError
src/lodge/core/snapshot.py:58: NotImplementedError
src/lodge/core/snapshot.py:63: NotImplementedError
E       AssertionError: assert {} == {<git object IDs>}
E       KeyError: 'lodge/decisions/d-aaaaaa-berths.md'
FAILED tests/core/test_listing.py::test_blob_id_matches_git[empty] - NotImple...
FAILED tests/core/test_listing.py::test_blob_id_matches_git[text] - NotImplem...
FAILED tests/core/test_listing.py::test_blob_id_matches_git[binary] - NotImpl...
FAILED tests/core/test_listing.py::test_assemble_equals_load[empty] - NotImpl...
FAILED tests/core/test_listing.py::test_assemble_equals_load[sample] - NotImp...
FAILED tests/core/test_listing.py::test_assemble_equals_load[all-kinds] - Not...
FAILED tests/core/test_listing.py::test_assemble_equals_load[duplicate-id] - ...
FAILED tests/core/test_listing.py::test_assemble_equals_load[stray] - NotImpl...
FAILED tests/core/test_listing.py::test_assemble_equals_load[attachments] - N...
FAILED tests/core/test_listing.py::test_assemble_equals_load[unreadable] - No...
FAILED tests/core/test_listing.py::test_assemble_equals_load[misplaced] - Not...
FAILED tests/core/test_listing.py::test_assemble_equals_load[ignored] - NotIm...
FAILED tests/core/test_listing.py::test_parse_file_ignores_attachments_and_gitkeep[attachment]
FAILED tests/core/test_listing.py::test_parse_file_ignores_attachments_and_gitkeep[decisions-gitkeep]
FAILED tests/core/test_listing.py::test_parse_file_ignores_attachments_and_gitkeep[spec-gitkeep]
FAILED tests/gitstore/test_tree_blobs.py::test_disk_tree_blobs_hash_the_bytes_read
FAILED tests/gitstore/test_tree_blobs.py::test_disk_tree_ignores_assume_unchanged
FAILED tests/gitstore/test_tree_blobs.py::test_read_tree_blobs_are_git_object_ids
18 failed in 0.71s
```

The assembly cases use independently constructed expected snapshots, as well as equality with `load`, and supply parses in reverse insertion order.
They cover all record kinds, duplicate IDs, strays, attachments supplied both ways, an unreadable header, a misplaced record, ignored paths, and the shared sample text.
The exact-tree tests also include binary bytes, a symbolic link, and a FIFO, and check that attachments are absent from blob mappings.

## Implementation and focused checks

`blob_id` computes git's SHA-1 blob key over the length-prefixed raw bytes, and `Listing` carries revision, identity, blob mapping, and attachments.
`Tree.blobs` is defaulted to preserve existing tree constructors.
`disk_tree` adds keys by re-encoding its already-read text with `surrogateescape`, which exactly preserves the original bytes, including link targets and non-UTF-8 files.
Non-regular files retain the existing empty-file representation and receive the empty blob key.
The checkout diff contains four added and two removed lines, within its six-line allowance.
Committed trees retain object IDs from `ls-tree`, including the existing empty-text representation of non-blob entries, without asking git to hash working-tree files.
Attachments remain listed, never read or hashed.
`MemoryStore` populates keys for both current and published trees, including its gate path.
`parse_file` dispatches each file to its existing parser, returns problems for strays, and ignores attachments, `.gitkeep`, and paths outside the store.
`assemble` keeps sorted-path duplicate handling, problem order and wording, misplaced-record checks, and the union of explicit attachments and attachment paths.
`load` is their composition, and no port or read path changes.
The shared `same_listing` continues comparing exact file contents and attachments, independent of blob metadata.

Before refactoring `load`, all nine independently constructed expected snapshots were checked against its original implementation and matched.
The initial implementation run found one test-fixture error: the committed-tree test's local remote still named the initial commit.
The fixture now pushes its synthetic commit to its local bare remote before comparing the published tree with `HEAD`'s IDs.
The listing test also supports running alone, using the existing repository helper with isolated git configuration.
No existing tests were edited except the planned `tests/app/fakes.py` helper changes; the Task 4 fix-round edits were committed separately.
Focused validation passed: 96 tests in 0.99 s, strict mypy on 227 source files, and Ruff.
Running `tests/core/test_listing.py` alone also passed all 15 cases.

## Timings

The baseline is an installed copy of Task 7's `c388306`, preserved from `git archive` without opening or changing another checkout or worktree.
The after build is installed from this Task 8a worktree.
Both environments are under `/var/tmp/lodge-bench`, use CPython 3.13.5 and PyYAML 6.0.3 with libyaml, and have compiled bytecode.
Replay command: `uv run --frozen python scripts/bench_reads.py /var/tmp/lodge-bench/s9000 --lodge /var/tmp/lodge-bench/venv-task-8a-after/bin/lodge --against /var/tmp/lodge-bench/venv-task-8a-before/bin/lodge --mode seen --runs 3`.
The default list contains 16 commands, including the multi-ref and multi-query reads added before this task.
The full gate and replay initially overlap, so absolute replay timings include that concurrent workload.
The isolated phase measurement ran after the replay and gate finished, with cyclic collection disabled to match the command-line read process.

## Full gate

`UV_FROZEN=true sh scripts/check.sh` passed: formatting (606 files), Ruff, strict mypy on 227 source files, Vulture, 1,631 tests passed with 1 skipped in 53.22 s, and `lodge check --gate` printed `ok`.
`git diff --check` passed.

## Completed replay

The following table is the replay's output; `lodge` is Task 8a, and `against` is Task 7.
The store has 16,120 files on native disk.
Every command's standard output and exit status match across all three measured runs.
The replay completed with exit status 0 and no timeout.

Mode: `seen`; store: `s9000`; runs: 3.

| Command | Build | Best (s) | Median (s) | Exit | Characters | Identical |
|---|---|---:|---:|---|---|---|
| `show {code}` | lodge | 1.469 | 1.489 | 0 | 458 | true |
| `show {code}` | against | 1.413 | 1.425 | 0 | 458 | true |
| `show {entry} --reasoning --provenance` | lodge | 1.523 | 1.525 | 0 | 438 | true |
| `show {entry} --reasoning --provenance` | against | 1.420 | 1.434 | 0 | 438 | true |
| `show {decision}` | lodge | 1.509 | 1.510 | 0 | 261 | true |
| `show {decision}` | against | 1.405 | 1.411 | 0 | 261 | true |
| `search berth --brief` | lodge | 1.660 | 1.669 | 0 | 1946 | true |
| `search berth --brief` | against | 1.632 | 1.643 | 0 | 1946 | true |
| `search "berth crane" --brief` | lodge | 1.788 | 1.811 | 0 | 2009 | true |
| `search "berth crane" --brief` | against | 1.637 | 1.649 | 0 | 2009 | true |
| `search {code} --brief` | lodge | 1.770 | 1.782 | 0 | 1653 | true |
| `search {code} --brief` | against | 1.631 | 1.631 | 0 | 1653 | true |
| `search berth` | lodge | 1.773 | 1.778 | 0 | 5038 | true |
| `search berth` | against | 1.638 | 1.645 | 0 | 5038 | true |
| `waiting` | lodge | 1.455 | 1.459 | 0 | 61 | true |
| `waiting` | against | 1.409 | 1.417 | 0 | 61 | true |
| `threads` | lodge | 1.473 | 1.503 | 0 | 16 | true |
| `threads` | against | 1.402 | 1.409 | 0 | 16 | true |
| `spec --area area-001` | lodge | 1.442 | 1.454 | 0 | 8013 | true |
| `spec --area area-001` | against | 1.421 | 1.422 | 0 | 8013 | true |
| `check` | lodge | 1.441 | 1.445 | 0 | 3 | true |
| `check` | against | 1.407 | 1.409 | 0 | 3 | true |
| `check --gate` | lodge | 1.642 | 1.660 | 0 | 3 | true |
| `check --gate` | against | 1.613 | 1.621 | 0 | 3 | true |
| `show {code} {code2} {entry}` | lodge | 1.453 | 1.458 | 0 | 1004 | true |
| `show {code} {code2} {entry}` | against | 1.427 | 1.429 | 0 | 1004 | true |
| `show A` | lodge | 1.646 | 1.652 | 0 | 1183 | true |
| `show A` | against | 1.616 | 1.627 | 0 | 1183 | true |
| `search berth tide --brief` | lodge | 1.904 | 1.906 | 0 | 3991 | true |
| `search berth tide --brief` | against | 1.854 | 1.860 | 0 | 3991 | true |
| `search --phrase "berth crane" --brief` | lodge | 1.766 | 1.766 | 0 | 1952 | true |
| `search --phrase "berth crane" --brief` | against | 1.735 | 1.743 | 0 | 1952 | true |

## Cost of hashing in `disk_tree`

Commands: `/var/tmp/lodge-bench/venv-task-8a-before/bin/python /var/tmp/lodge-bench/task-8a-phases.py` and `/var/tmp/lodge-bench/venv-task-8a-after/bin/python /var/tmp/lodge-bench/task-8a-phases.py`.
The scratch probe reads the same native-disk `s9000` store and runs three sequential `disk_tree` calls per build, timed with `time.perf_counter` after importing modules and disabling cyclic collection.
On the after build, it then times three in-memory `{path: blob_id(encode(text)) for path, text in tree.files.items()}` passes and asserts that the result equals `tree.blobs`.
The pass includes re-encoding, the blob prefix, SHA-1, hexadecimal conversion, and mapping construction, without file I/O.
No timing assertions are in pytest.

| Phase | Best of three (s) | Median (s) |
|---|---:|---:|
| Task 7 `disk_tree` | 0.338641 | 0.345453 |
| Task 8a `disk_tree` | 0.361383 | 0.364346 |
| Task 8a in-memory encoding, hashing, and mapping | 0.011575 | 0.011675 |

The observed full `disk_tree` difference is 0.022742 s, about 6.7%, at 16,120 files.
The isolated hashing pass is 0.011575 s; the full phase difference also includes allocation and measurement variation.
These are local observations, without a timing threshold or a claim about the later index targets.

## Concerns and delivery

No outstanding implementation concern or NEEDS_CONTEXT remains.
The replay initially overlapped the full gate; its absolute timings therefore include concurrent work and do not isolate hashing.
The later phase probe records that cost separately after both finished.
No read ports, record files, plan steps, structure rules, or deferred ordering implementations were changed.
The report, failing-test evidence, implementation, and new tests are delivered together in the Task 8a commit.
