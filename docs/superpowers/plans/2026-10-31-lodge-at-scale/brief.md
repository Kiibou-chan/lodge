# Brief: lodge at scale, and leaner reads for agents

The author asked (2026-10-31 21:43 and 21:47): make an agent's knowledge reads through lodge cheaper and faster, and "Make sure that this can handle large amounts of data. Possibly through a database or whatever you find works. If the conclusion is that this needs a server that's fine too. Local file based solutions are of course preferred for now."

## Evidence (measured; private sources, cite only the numbers and lodge's own code)

A measured comparison had an agent answer design questions from a store of 1,516 record files read through lodge, against the same knowledge as Markdown files.
With `search --brief` (this branch's base, d-fqymzm) lodge cost less than Markdown, but its wall-clock was 2.5 times Markdown's, all of it lodge's own run time: each call takes 1.3 to 1.7 s, and agents loop over 5 to 11 refs per shell call.
Two independent advisors analysed the transcripts and lodge's code; their reports are private (outside this repository; read them, but never copy a record's name, code, or text from them into this repository).

Timings (this machine; `/home` is NTFS through FUSE, `/var/tmp` and `/` are native ext4; measure on native disk unless a step says otherwise):

1. One `show` on the 1,516-file store: import 0.19 s; header parsing 0.36 s, done twice (current and published trees, identical when nothing is staged); trees about 0.55 s on NTFS, 0.04 to 0.07 s on native disk with packed objects; checks 0.09 s.
2. libyaml (`yaml.CSafeLoader`, available here) parses the 1,514 headers in 0.065 s against 0.357 s; the C loader differs from the Python one on escaped UTF-16 surrogates and on error wording, so a fallback to the Python loader on any C error keeps behaviour (both advisors measured; one found output byte-identical on seven commands with the fallback plus a skipped second parse).
3. Synthetic stores from `scripts/bench_store.py` (this branch, a made-up harbour project, records written through lodge's writer): 1,593 files, 1.6 s per read; 16,008 files, 17.6 s per read on NTFS (parsing 6.8 s, `check_change` 5.9 s, trees 4.7 s); 159,716 files: `git ls-tree -r` 73 ms, `git status --porcelain -- lodge` 3.0 s on NTFS, one `search` still running at minutes.
4. `check_change._missing` (`src/lodge/core/check_change.py:55`) rebuilds a union of all IDs once per published record: quadratic, 0.07 s at 1,516 records, 6.0 s at 16,008.
5. Tokens: brief search lines are about 44 % of all text the agents brought into context; searching for a code splits it into words (`X-1` into `x` and `1`), matching about 700 records of which a handful carry the code; agents searched codes to find sibling records (`X-1.why`, `X-1.b`) and records citing the code, which `show` does not list; `show` takes one ref, so agents loop in the shell (zsh; an `echo =====` separator broke two loops); unquoted multi-word queries are usage errors; the guide's 39 lines on writing are read by agents that only read.

## Coordinator rulings (binding for the plan; record each with `lodge add`, scope `process`, `work_item` the plan)

1. **Correctness first.** The gate (`lodge check --gate`) and `lodge add` keep their full semantics on every store; nothing below may change a check's result, a problem's wording, or a published state's comparison, except where a task says so and records it as a product decision with a spec edit.
2. **Speed, in this order:** fix `_missing` and any other superlinear step a profile at 16,000 and 160,000 files finds; libyaml with a fallback to the Python loader on any C error; reuse the parsed snapshot when current and published trees are identical (file mappings and attachments), and skip the change check only where its result is provably the identical-state result (the plan names the proof and its test).
3. **Scale: a local index, no server unless measured necessary.** A SQLite database (standard-library `sqlite3`, FTS5 if available, with a fallback when not) in the git common dir, never committed, safe to delete, rebuilt on a version mismatch or corruption: parsed records keyed by content hash and parser version; per state identity (the store's tree identity plus the working-tree changes under `lodge/`), the derived statuses, flags, and check results reads need, and a full-text index.
   Reads answer from it; a state not seen before is built from the cached parses of unchanged blobs plus parses of changed files.
   The gate and `add` may use the parse cache (content-addressed, so sound) but always derive and check in full.
   Targets on native disk at 160,000 files: a read on a seen state at most 0.3 s; a read after one changed record at most 3 s; `lodge check --gate` measured and reported, not targeted.
   A long-lived server is out of scope unless the warm read stays above 0.3 s after the index; then the plan stops and reports.
4. **Leaner reads:** `show REF...` (several refs, one state, each record once, per-ref errors with an aggregate exit status); `search` with several queries in one call; a query that is a code returns that code's family (`X-1`, `X-1.*`, never `X-10`) and then the records citing it, before word matches; phrase matching for a quoted phrase and all-words-first ranking; `show` names a record's sibling codes and the records citing it, one brief line each; brief lines drop what is default (the planner proposes which fields with a measurement); `lodge guide --read`, a short guide for agents that only read, with quoted examples.
   Each is a product decision with its spec edit, through `lodge add` on this branch.
5. **Benchmarks are part of the product:** `scripts/bench_store.py` (exists), a read-replay benchmark (a command list run against two lodge builds, timing and output compared), and a recorded table of timings at 1,600, 16,000, and 160,000 files for the plan's final report.
   Synthetic data only; nothing from any other project.

## Process

Plan in this worktree (branch `read-speed`, based on `search-brief`), at `docs/superpowers/plans/2026-10-31-lodge-at-scale.md` with its ledger `-progress.md` and this folder; format as the newest plan under `docs/superpowers/plans/`.
Each task names its tests (test-first), its Produces and Consumes, its files, and its timing check where it has one.
The plan is reviewed (two angles), fixed, and rechecked before any build; tasks are built in order on this branch.
