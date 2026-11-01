# Recheck of 6b and adversarial review of 7b

Status: complete; findings and measurements were written incrementally.
Target: detached `094e9cef866769de115da18a485f05698f98e737`, read-only throughout.
New scripts, copied stores, and raw output: `/var/tmp/lodge-review-pf6/scratch/7b/`.
No command runs in, or writes to, `/var/tmp/lodge-build`.

The external `tasks-6b.md` is the revised document under review; its older tracked copy is not substituted for it.
7b replaces the withdrawn 7; it amends 6b and inherits the original plan's unchanged state keys, transactions, and invariants.
These are plan reviews: Tasks 8c, 9c, and 10 are not implemented at the reviewed commit.

## 6b recheck

“Fixed” below means fixed in the task contract and named implementation tests, not verified as built code.

| Earlier finding or carry-forward | Disposition in revised `tasks-6b.md` |
|---|---|
| F10, raced regular file replaced by FIFO | **Fixed.** Lines 41–45 and 59 require `O_NONBLOCK`, `O_NOFOLLOW`, and descriptor `fstat`; only regular descriptors are read. Line 73 adds the bounded regular-to-FIFO swap test for identity, texts, gate, and add. |
| R1, transient attributes poison private raw entries | **Fixed by withdrawal.** RAW-1 and Task 11b remain removed. |
| R2, unavailable info-only raw blobs | **Fixed by withdrawal**, and line 55 retains one exact fallback tree for identity, listings, and texts. |
| R3, folder/attachment ancestor links and traversal swap | **Fixed.** Lines 43, 59, 73, 96–100 require relative descriptor traversal, reachable real folders, descendant pruning, exact-reader comparison, outside and attachment links, and the pre-entry swap. |
| R4, private stat admission/mmap proof | **Fixed by withdrawal of the private cache.** The previously accepted limitation of Git's own index observations is not newly resolved or relabelled exact. |
| R5, unsupported private stat-cache filesystem proof | **Fixed by withdrawal.** FOLD-1 remains the separately existing folder-signature contract, not a file-stat cache. |
| R6, publication of unvalidated private entries | **Fixed by withdrawal.** No raw-entry publication protocol survives. |
| R7, deleting an aged Git lock | **Fixed by withdrawal.** No age-based Git-lock deletion is specified. |
| R8, timing fixture unlike production raw index | **Fixed by withdrawal.** The private index is no longer the measured design. |
| R9, conversion fallback estimate | **Fixed.** Lines 17–18 and 81 retain full-byte cost and separate conversion reporting. |
| R10, wrong minimum for `--attr-source` | **Fixed by withdrawal.** That capability requirement is gone. |
| R11, removed conversion provenance | **Not resolved; correctly pending STALE-1 with the author.** Lines 62–67 retain both full sentences and correctly map STALE-1 A to R11-B and B to R11-A. Line 72 adds actual removed-attribute histories for ident, UTF-16, a length-preserving filter, and CRLF; gate/add stay byte-based under both. This is not an unreported correctness closure. |
| R12, steady raw CRLF overlay cost | **Fixed by withdrawal.** Conversion reads pay the byte-reading cost and are reported separately. |
| R13, gitlinks, including the two requested follow-ups | **Fixed.** Lines 60 and 74 explicitly name `blob_id(b'')`, the absent checkout submodule, an unavailable commit, and empty/populated checkout cases under `diff.ignoreSubmodules=all`. |
| Git-index replacement race and continuous-change fallback | **Fixed.** Lines 55 and 72 bracket the entire pinned Git group, discard all dependent results, allow three attempts total, then retain one exact disk tree for all three interfaces; the test checks listings and texts as well as identity. |

The prior F1–F9 concern withdrawn 7 rather than 6b; their 7b dispositions are reviewed separately below.

## 7b findings

### B1 Important: the supplied scan drops the existing top-level parse admission check

Where: `measure-7b/phases7b.py:40–43`; Task 9c Interfaces and its corruption cases (`tasks-7b.md:16–24`); existing `src/lodge/gitstore/index_parses.py:25–28`.
Failure scenario: a cached value is valid JSON `123`, `"text"`, `{}`, or `[""]`.
`from_plain` accepts these general codec values without raising; its dataclass validators do not enforce the parse port's result union.
The existing reader rejects each as a miss, while the supplied `safe_scan` returns it as a hit.
`assemble` silently ignores such an item, so a real record can disappear instead of being reparsed.
This does not reopen F1's cross-key document-boundary bug: per-row decoding fixes that by construction.
It is a separate prototype defect and a missing explicit admission step in the proposed algorithm; the task's overarching “keeps its result” requirement already forbids the divergence.
Evidence: `scratch/7b/probe_contracts.py` extracts the actual supplied function; each of the four values differs from `find_parses` at its own key, while the joined-success corruption cases now agree exactly.
Fix: retain the exact `value is None or isinstance(value, (Area, Decision, Problem, SpecEntry, Thread))` check in both paths, with non-parse codec values as misses.
Add those cases and a valid non-parse dataclass to the differential corruption test; benchmark the admitted result.

### B2 Important: second-sighting-only keeps leave the inherited cap permanently disarmed

Where: `tasks-7b.md:35–36,44`; inherited Task 10a Step 3a (original plan lines 534–537), Task 9 cap rule, and `src/lodge/gitstore/index_space.py:96–101`.
Failure scenario: begin with a new index, or immediately after a clear, then read each changed state only once.
SECOND-1 writes markers, new parses, and computed facts but never a complete state; `meta.kept` must remain zero because Step 3a explicitly makes it mean a complete state kept.
`prepare_keep` clears only when `meta.kept` is true.
Thus the very workload SECOND-1 is chosen for can grow immutable parse/facts rows without limit; pruning markers to 64 does not prune those units.
The original full-keep-on-every-build path armed the cap on its first read; 7b removes that guarantee without replacing it.
Evidence: `scratch/7b/probe_cap.py` runs the actual `prepare_keep` before three first-sighting transactions, with a 16 MiB cap and synthetic 10 MB facts payloads.
Used pages reach **30,056,448 bytes**, epoch stays 1, and `kept` stays 0; another pressure check does nothing.
Setting `kept=1` makes the same helper clear to **24,576 bytes** and raise epoch to 2.
Fix: apply pressure control to first-sighting and parse-only writes too, with a separate eligibility rule that is armed by a committed unit/facts write rather than requiring a complete state.
Preserve a bounded allowance for one oversized working set, the clear-in-place epoch rule, and replay of all units needed by a later complete keep.
Test a long sequence of first sightings with zero kept states, both from an empty index and after a clear, and require bounded used pages and successful later second/third reads.

### B3 Minor: `BEGIN` alone does not establish the snapshot expected by the new scan test

Where: `tasks-7b.md:23`, `test_scan_inside_one_read_transaction`.
Failure scenario: connection A executes `BEGIN`; B clears and commits; A issues its first `SELECT`, the scan.
SQLite then sees the cleared table, not the pre-clear rows requested by the test.
This is a safe miss, not a stale answer; a sound implementation cannot satisfy that literal test without an earlier read.
Evidence: `scratch/7b/probe_contracts.txt`: `BEGIN, clear commits, first SELECT: []`; with a prior `SELECT`, the scan returns `[(1,)]` after B's clear.
Fix: establish the snapshot with a read before permitting B's clear, then assert pre-clear scan results; separately allow a clear before the first read to produce misses and whole-read fallback.

### B4 Important: the “whole keep” prototype does not encode the planned rows or perform a complete keep

Where: `measure-7b/phases7b.py:74–113`; `plan-fix-7b.md`, whole-keep table, 71 MB/cap inference, and SECOND-1 cost comparison; original Task 10a `Row` and `keep_state` contracts.
Failure scenario: treat the 8.764 s sum and 71,061,698 bucket bytes as the cost and size of the intended complete state.
The prototype serialises `(Level1, Level3, changed_by)`, including titles, statements, numbers, attachments, and other text already held by parses.
Task 10a instead stores the derived-only `Row`: it includes `FileKey` and `areas`, but excludes those record fields and most `Level3` fields.
This changes the layout and encoded volume in both directions; the statement that rows and buckets follow Task 10a's layout is false.
On the same rerun state, converting the prototype's views to exactly the planned Row fields produces **50,440,556 bytes** in 1,024 buckets, versus the proxy's **71,061,703 bytes**.
This is a payload-size comparison, not a timing of a finished Row builder or complete keep.
Its transaction writes only buckets, a simplified citer table, and one facts pair, not answers, state/completeness metadata, missed parses/FTS units, eviction, or pressure/epoch recovery.
The citer stand-in also sorts date strings rather than timezone-aware dates and omits family exclusion and family-root rows.
The report acknowledges that the citer pass is a stand-in, but its other complete-keep and capacity claims still rely on this different payload.
Fix: label 8.764 s as the sum of the supplied partial proxy stages and withdraw the claimed actual bucket footprint, number of states fitting under the cap, and quantitative SECOND-1 break-even until measured with the planned Row and complete keep.
Task 12 should retain whole-command first/second/third exit timings and include the actual complete keep, with cap clear and eviction apart.
No output-correctness conclusion or permission to change the 3 s target follows from this measurement issue.

### B5 Important: checking the first keep SQL statement does not test deferred construction or all keep failures

Where: `tasks-7b.md:35–38`; inherited `keep_state(state, rows, answers, citing, facts, parses, misses, epoch)`; original Task 10a's separate `app/read_model.py` construction.
Failure scenario: the app eagerly constructs every Row, bucket input, and citer mapping before returning the answer, queues them, then starts SQL only after stdout flushes.
That passes the specified stream/SQL-order test while still paying most of the full-state construction cost before printing, contrary to the explicit ruling.
Alternatively construction or serialisation raises outside a catch scoped only to the database `keep_state` call; the already printed command then fails despite every injected-SQL failure test passing.
The document states the desired outcome, but the inherited materialised-arguments interface and new tests do not establish it.
Fix: specify a deferred operation holding the checked read's pinned inputs; invoke the entire full-row/citer construction and keep only after successful command output and flush, within the cache-failure boundary.
Do not reread live files under the earlier state's key inside that deferred operation: an edit during printing or the long keep must lead the next identity to a different key, while the old key continues to describe the old snapshot.
On a first sighting do not invoke that constructor at all.
Instrument construction as well as SQL; inject failures before SQL in Row/citer building and encoding, and preserve ordinary nonzero command statuses too.
Test a stream accepting writes but raising on flush, a closed Python stdout, a broken pipe with Python's normal SIGPIPE disposition, and SIGPIPE termination separately.
Do not run the deferred keep unconditionally from a `finally` or release hook after output failure.
These are missing implementation/test obligations, not claims that unbuilt Task 10a already violates them.

### B6 Minor: inherited tests still expect a stored hit on the second read

Where: original Task 10a Step 1, `test_seen_state_reads_no_snapshot` and `test_show_code_reads_citers_without_texts` (original plan line 528); `tasks-7b.md:38–39`.
Failure scenario: the second `show` must rebuild in memory under SECOND-1, but both inherited tests patch `assemble` to forbid that on the second `show`.
The new third-read test does not amend those older requirements, so the task contains contradictory expected behaviours.
Fix: move those hit assertions to the third read, after observing the successful post-flush second keep, or preseed a complete state explicitly where lifecycle is not the subject of the test.

## Sequential timing rerun

Fresh copy: `/var/tmp/lodge-review-pf6/scratch/7b/s90000`, copied from `/var/tmp/lodge-bench/s90000` with no hard links; only the copy is changed.
The reference store is not warmed or opened through lodge and its index is not written.
The reviewed source package is copied unchanged from this worktree into `scratch/7b/build/lodge`, compiled there, and imported with explicit `PYTHONPATH`.
The native `/var/tmp/lodge-plan-fix6/venv/bin/python` supplies only CPython 3.13.5 and the dependencies: PyYAML 6.0.3, libyaml 0.2.5, SQLite 3.47.1; Git is 2.56.0.
The source path and versions are printed in the raw output.
Configuration: `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 GIT_ATTR_NOSYSTEM=1`, gc disabled as supplied.

The copy's old `.git/lodge` is removed, then two sequential `waiting` commands warm this build's parse index: **16.480 s**, **8.870 s**, both exit 0.
Append one line to the specified `s-01z2c4` file on disk; each phase run starts with **160,800 requested keys, 160,800 old parse rows, and one parse miss**.
The supplied setup does not preserve the appended line's exact text; mine is `One changed line for plan fix 7b.`.
It adds four token strings to the aggregate and five bytes to the proxy buckets versus the report, with the same single-record edit workload.

I reran the supplied stages twice, sequentially, best of three where supplied and **one call per keep part**.
Before the second pass, only the edited path's newly inserted parse is removed from the scratch index and the scratch keep database is recreated, restoring the one-miss workload.
The second pass additionally times the exact original top-level parse admission check (B1) and compares planned Row payload size after all timings.
No timing jobs overlap; the second pass has no concurrent probe job.
The original script is not changed: scratch adaptations change paths, record raw timing values, and add those two checks.

| Stage or sum | 7b claim | First rerun | Second rerun |
|---|---:|---:|---:|
| Per-key parse lookup | 1.428 s | 1.4400 s | 1.4032 s |
| Ordered per-row scan, supplied function | 1.056 s | 1.0600 s | 1.0394 s |
| Scan retaining the existing top-level admission | — | — | **1.0415 s** |
| Assemble | 0.146 s | 0.1462 s | 0.1437 s |
| Current derive | 0.996 s | 1.0008 s | 0.9936 s |
| Current check_state | 0.577 s | 0.5721 s | 0.5679 s |
| Published snapshot_of with memo | 0.476 s | 0.4685 s | 0.4647 s |
| Published derive + check_state, facts miss | 1.564 s | 1.5691 s | 1.5942 s |
| Published facts load stand-in | 0.028 s | 0.0280 s | 0.0273 s |
| Full check_change, supplied facts | 0.918 s | 0.9144 s | 0.9241 s |
| Failing IDs + unrecorded problems | 0.065 s | 0.0649 s | 0.0646 s |
| Waiting answer construction | 0.012 s | 0.0122 s | 0.0121 s |
| Fixed + lookup + assemble + derive + check_state | **3.181 s** | **3.1852 s** | **3.1506 s** |
| Changed sum, facts hit | **4.680 s** | **4.6731 s** | **4.6434 s** |
| Changed sum, facts miss | **6.216 s** | **6.2142 s** | **6.2103 s** |
| Keep proxy: views | 0.855 s | 0.8750 s | 0.8636 s |
| Keep proxy: encode buckets | 2.190 s | 2.2109 s | 2.1971 s |
| Keep proxy: code_tokens | 2.238 s | 2.2881 s | 2.2182 s |
| Keep proxy: aggregate/order citers | 3.015 s | 3.0323 s | **3.5879 s** |
| Keep proxy: encode citer rows | 0.020 s | 0.0196 s | 0.0193 s |
| Keep proxy: encode facts | 0.030 s | 0.0298 s | 0.0297 s |
| Keep proxy: partial transaction | 0.416 s | 0.4674 s | 0.4420 s |
| Keep proxy sum | **8.764 s** | **8.9231 s** | **9.3577 s** |

The sums retain the supplied **0.406 s fixed-stage estimate**; it is not remeasured or represented as part of a runnable changed command here.
Using the corrected admission scan yields **4.6455 s** with facts, **6.2124 s** without, and **3.1527 s** for the named floor in the second pass.
`change_facts` with all inputs provided is about a microsecond and is included in the sums.
One bucket's supplied decode is about 0.2 ms and the isolated marker write about 0.02 ms, as before.

**What reproduces:** the 1.428→1.056 s lookup improvement, the approximately 4.680/6.216 s stage sums, and the miss of 3 s with these named stages.
The per-row scan equals today's lookup on this valid-row fixture; the corrupt top-level values still need B1's fix.
**What does not reproduce as claimed:** a complete 8.764 s keep or actual 71 MB derived-row payload (B4).
The supplied partial proxy is 8.923 s in the first pass and 9.358 s in the second; its one-call citer aggregate and transaction are variable, with the latter pass's citer time 19% above the original.
The proxy's rough magnitude reproduces, but its exact number is not stable across the two calls.
Neither 4.680 s nor 6.216 s is an end-to-end command timing; the supplied current `read_checked` whole-call diagnostic is **11.702 s** and **11.581 s**, with today's exact trees and per-key implementation, not the proposed fast path.

The stage sums omit small caller work beyond output and missed-parse insertion: materialising the `parsed` dictionary, constructing `memo`, and the final union/sort of current and change problems are outside the timed stages.
The supplied `failing_ids`/`unrecorded_problems` timings use current `check_state`'s result rather than that final merged result.
The facts-hit stage decodes already resident JSON strings, without a SQL lookup, and the fixed-stage estimate comes from earlier measurements.
These are limits on completeness, not additional proof that all future exact approaches must miss 3 s.
The miss remains with the admitted scan before restoring those omissions.

Raw evidence: `scratch/7b/warm7b.txt`, `phases7b-first.txt`, `phases7b.txt`, `timings-first.json`, `timings.json`; runners and adapted scripts are beside them.
Contract probes: `probe_contracts.py/.txt` and `probe_cap.py/.txt`.

## F1–F9 and the binding rulings

| Prior 7 finding | 7b disposition |
|---|---|
| F1, joined documents shift parses across keys | **Closed by construction.** Each selected SQL row retains its full `(path, blob)` alongside its independently decoded document. Neither `null,null` nor the adjacent cross-boundary fragments can create another key's value. B1 is the separate top-level admission issue. |
| F2, citer ordering invalidation | **Closed by removal of delta citers.** A full keep must still implement the original complete-state ordering and family exclusion, not the measurement stand-in. |
| F3, scoped checker drops published context | **Closed by withdrawal.** Full `check_change` and its original helpers run, with the full published snapshot. |
| F4, shared-bucket/base lifetime | **Closed by removal.** No earlier state's buckets or digest map are inputs to the new state; the original own-row transactions and epoch replay apply. |
| F5, self-coupled checker oracle | **Closed by withdrawal of the checker rewrite.** No transitive helper rewrite or new scoped oracle is required. |
| F6, comparison-dependent failing IDs keyed by current ident | **Closed by removal.** `StateFacts` again contains only snapshot-intrinsic `status` and `check_state.problems`; full state rows carry the final failing flags for the complete current/published/settings/time context. |
| F7, rejected alternate target | **Closed.** The 3 s target and Task 12's stop are unconditional in 7b; no TGT-7 branch remains. |
| F8, ancestor citer union changes exact-token matching | **Closed by removal of that lookup amendment.** The original exact-query citer row is used, with that query's family excluded. |
| F9, inadequate delta property generator | **Closed by withdrawal of delta state.** Original whole-state differential tests remain; SECOND-1 lifecycle/cap tests need the additions above. |

The coordinator's no-delta and full-checker rulings are followed; caching immutable parse units and intrinsic published facts is not delta state.
Task 4's existing proved identical-listing shortcut remains the only exception to rebuilding/comparing the two snapshots.
No private file-stat cache is reintroduced.
The scan can be exact by construction with B1's admission guard; the supplied prototype alone is not evidence of corruption equivalence.
The no-full-row-build-before-print rule is stated, but B5 makes its required implementation and tests concrete.
Task 12 keeps 3 s, measures to process exit, records the expected miss with a phase table, and invokes the stop.
STALE-1 remains with the author and both full branches survive, with gate/add byte-based under either.

## SECOND-1 safety analysis

These conclusions follow from the **combined inherited invariants and 7b amendments**, not from an implementation of the unbuilt marker/state adapter.
The independent small probes support specific mechanisms; they are not substitutes for the planned end-to-end concurrency/fault tests.

| Adversarial event | Can it make a seen read answer another snapshot? | Required mechanism and assessment |
|---|---|---|
| Marker left by another build | **No under the specified namespace.** | The source/dependency/schema digest selects a different SQLite file. `seen` must live inside that file, not in a shared sidecar. A marker supplies only keep eligibility, never facts or rows. |
| Same current ident, another published ident or settings | **No.** | Markers use the complete stored-state key, SHA-1 of current ident, published ident, and settings digest. Reusing only the current ident would violate the task. Time validity is separately checked on the complete stored state. |
| Marker from an earlier epoch; clear between marker lookup and keep | **No with inherited replay.** | Clear deletes `seen` in the same transaction as the other tables and raises the epoch. An already observed marker may trigger redundant work, but the full builder owns its inputs; `keep_state` must compare the build's earlier epoch inside the write transaction, after any cap-triggered clear, and reinsert **all** parses and facts used, including hits. Never treat marker existence as completeness. |
| Clear after keep, before the next seen read | **No.** | In a later read transaction the state is absent and the whole read falls back. If the read already established its snapshot, WAL preserves the complete earlier version until that transaction ends. B3 corrects exactly when that snapshot begins. |
| Two first readers find no marker | **No; only promotion may be delayed.** | Both can write the same marker without a state. A later read still builds from its own files/listing before promotion. A marker is not a reservation and need not elect one builder. |
| Two later readers keep the same key at once | **No under full replacement.** | `BEGIN IMMEDIATE` serialises the writers. Each transaction replaces that key's own rows whole and publishes its state row last. The winner is a complete state; existing readers see one committed WAL version. Each row set and validity interval must come from its own pinned checked input, not live files reopened later (B5). |
| Two different states kept at once, eviction/re-keep in between lookups | **No.** | They use different full keys; eviction removes only one state's own rows. A seen read holds one explicit snapshot, and missing promised payloads cause whole-read fallback. |
| Files change after output, during the long keep | **No if B5's inputs remain pinned.** | Keeping the earlier snapshot is safe: it is stored under the earlier identity, and a later identity chooses the changed state. The keep must not combine an old key with a newly reread listing or current snapshot. |
| Crash/SIGKILL mid-keep | **No partial state becomes usable.** | One transaction includes parse/FTS dependencies, facts, eviction, owned rows, and the last completeness row. An uncommitted WAL transaction is not visible; a completed commit is complete. Surviving content-keyed units from separate earlier writes are harmless. |
| Output write fails, flush is interrupted, Python stdout is closed, or a pipe breaks | **No complete keep may start.** | Gate the entire deferred operation on successful whole-command output and explicit flush, not on entering `finally`, `release`, or an `atexit` callback. B5 adds distinct cases, including write success followed by flush failure. A previously written marker alone remains unable to answer anything. |
| SIGPIPE | **No stale or partial state.** | Python normally ignores SIGPIPE and reports a broken pipe as an exception; with default SIGPIPE disposition the process can die before promotion, or roll back a running transaction. A death after commit leaves a complete state. Do not mask signal cancellation as a cache success. |
| Keep fails and changes the command status | **Forbidden, with a test gap in B5.** | Catch ordinary cache failures over **construction, encoding, and SQL**, preserve the command's already computed status (including nonzero aggregate `show` status), print no cache diagnostic, and release resources without replacing that result. SQL-only injection is insufficient. |

`probe_contracts.txt` demonstrates no deferred action after closed stdout, a write-accepting stream whose flush raises `InterruptedError`, a real broken pipe, or default-disposition SIGPIPE.
The latter exits by signal 13; the boundary model deliberately exits 23 for the exception cases.
These are demonstrations of the proposed success boundary, not claims about the final CLI or its output-error exit codes.

I found no marker-induced stale-answer construction if these inherited keys, validity checks, complete transactions, and pinned inputs are honoured.
No extra epoch component in a marker key is needed for correctness: stale markers cannot supply data, and full-keep epoch replay restores dependencies.
Adding one may change promotion policy but does not fix B2's disabled cap.
Under STALE-1 answer A/R11-B, the already documented stat-clean conversion-history case can still make an indexed answer differ from byte-reading files; SECOND-1 neither creates nor repairs that pending author choice.
Under the exact-byte branch, the marker protocol introduces no such exemption.

## First-read published facts

The key is sufficient in the **combined** plan: `(build-specific index file, published ident)`.
For a committed publication the ident is the pinned `lodge/` Git tree ID, including file names and the attachment tree; different commits with the same subtree intentionally reuse facts.
The empty-tree identity has one corresponding empty snapshot.
The original Task 10c still computes the published snapshot from its own listing and parses, with only the existing equal-listing shortcut; it does not borrow the current snapshot merely because most paths match.

`derive(published).status` and `check_state(published).problems` depend only on that snapshot and the build.
They do not depend on current identity, publication comparison, core settings, clock time, or whether the state was ever completely kept.
Consequently `INSERT OR IGNORE` facts written alongside the first marker cannot apply to another publication with a different ident; the same ident denotes the same relevant input.
This would not hold for `check_change` problems or final failing IDs, which are explicitly absent from `StateFacts` after withdrawing 7.
The final change check still uses the full original body and the live current/published pair.

`probe_facts.py/.txt` round-trips the proposed status/problem-key payload against three distinct synthetic publications, including a retired entry and duplicate-code problems; all three full `check_change` results, ordered notes included, equal the version supplied with the round-tripped facts.
Supplying one publication's payload to another deliberately changes the result in the duplicate-code case, confirming why exact key selection matters.
This exercises core's existing facts interface, not the unimplemented first-marker database writer.
Retain a database/CLI test that changes the published ident and proves the old row is not selected, in addition to the specified same-ident hit test.

“Once per published ident” is conditional on a successful write and no later clear, loss, or build change; concurrent first readers may also compute the same facts twice.
Those cases cost time but do not license cross-key reuse.
If a clear loses facts after a marker write, the next build recomputes them; if it happens before a complete keep, the inherited all-used-facts replay restores them.
B2 is the growth issue caused by these first-read facts surviving without a complete keep, not a defect in their content key.

## Scope and verdicts

Read the complete prior 6b/7 review, revised external 6b tasks, 7b report and tasks, all `measure-7b` inputs and outputs, the original plan and brief, and the source implementing the inherited keys, codec, checks, snapshots, index transactions/epoch/cap, and CLI output lifecycle.
No full repository gate is run: no implementation changes are proposed or made here, and these future task adapters/tests do not exist at 094e9ce.
The benchmark and contract probes are scratch work, with every new package import rooted in the unchanged copied source.
Final verification: all 85 copied `.py`/`.md` package files match the worktree byte for byte; `git diff --exit-code` and `git status --porcelain` are clean, and HEAD remains `094e9cef866769de115da18a485f05698f98e737`.
No worktree file was edited, no commit or push was made, and no command ran in or wrote to `/var/tmp/lodge-build`.

Findings: **0 Blocking, 4 Important (B1, B2, B4, B5), 2 Minor (B3, B6)**.
The earlier blocking cross-key joined-decoder failure is closed.

**6b verdict: accept.** The requested F10 hardening and the other named carry-forwards are explicit in the revised task text and tests.
R11 is correctly unresolved with the author, with both full branches retained; acceptance of the task text does not decide STALE-1.

**7b verdict: accept with fixes.** Retain the per-row scan with the original result-type admission, full checks, complete state construction, and first/second/third keep policy.
Fix cap eligibility for first-sighting-only workloads; explicitly defer and contain the complete constructor/keep after successful output; correct the inherited tests and snapshot test; replace the “whole keep” and capacity claims with measurements of the intended payload and complete transaction.
The approximately 4.68/6.22 s stage sums reproduce, the 8.764 s complete-keep claim does not, and **3 s remains the target with Task 12 recording the miss and invoking the existing stop**.
