# Task 7a correctness review

Reviewed `03383f6..e40f55a` against Task 7a, its report, the Python command and output modules, and every carried Python test.
Two Important findings concern lost Python assertions; no unmutated output discrepancy was observed.
Only this review is changed in the review worktree.
All probes and mutations ran in a temporary detached worktree at `e40f55a`, with each mutation restored before the next run.

1. **Important: the orphaned-thread carry omits the waiting-output assertion.**
   Handle: `ts/tests/app/thread-fix-paths.test.ts:21`.
   The test exercises only `threads` and `thread`, whereas `tests/app/test_thread_fix_paths.py:32` also requires `waiting_text` to include `about s-zzzzzz, not found`.
   The direct head and thread formatter assertions are covered through those two commands, but the waiting assertion has no replacement.
   The row is marked `ported`, and Task 7a requires these assertions to carry.
   The report's front-door ruling explains using commands instead of exporting formatters; it does not require losing the waiting assertion.

   Probe: in `ts/src/cli/thread-output.ts:22` and `:25`, replace `threadHead(t, waiting.titles.get(t.about))` with `threadHead(t, waiting.titles.get(t.about) ?? "unknown")`.
   Both `bun test tests/e2e tests/cli tests/app/thread-fix-paths.test.ts tests/parity.test.ts` (250 passes) and `bun test` (1,741 passes) remain green with this incorrect orphan subject line.
   A scratch regression probe seeds a project, asks an agent doubt about its entry, reads the resulting thread through `paths` and `stored`, and uses `handEdit` to replace its subject with `s-zzzzzz`.
   Its assertion, `expect((await p.run("waiting")).out).toContain("about s-zzzzzz, not found")`, passes before mutation and fails after mutation: the subject line becomes `unknown`.
   Restore the waiting assertion through `run(["waiting"], io)` over the existing synthetic Lodge's decoded results, retaining the prescribed front door and MemoryStore.

2. **Important: ordering assertions accept missing output that Python rejects.**
   Handles: `ts/tests/e2e/show-levels.test.ts:28` and `ts/tests/e2e/waiting.test.ts:47`.
   Python's `str.index` raises when either operand is absent; JavaScript's `indexOf` returns `-1`, which satisfies these comparisons when the first item disappears.
   Thus `show_entry_reasoning_lists_its_decisions` no longer requires the Reasoning heading, and `waiting` no longer requires the flagged decision to remain in the author group after opening a thread.
   This weakens `tests/e2e/test_show_levels.py:25` and the final ordering assertion in `tests/e2e/test_waiting.py`, beyond the permitted substitutions.

   Probe A: in `ts/src/cli/output.ts:42`, change `section("Reasoning", shown.level2)` to `section(shown.level1.id.startsWith("s-") ? "Wrong" : "Reasoning", shown.level2)`.
   The focused 250 tests and the complete 1,741-test suite both pass, although an entry now prints `## Wrong`.
   A scratch assertion requiring `## Reasoning` in the seeded entry's `show --reasoning` output passes before mutation and fails after mutation.

   Probe B: in `ts/src/cli/thread-output.ts:24`, change `...listed.items.map(formatLevel1),` to `...(waiting.forAuthor.length ? [] : listed.items.map(formatLevel1)),`.
   `bun test tests/e2e/waiting.test.ts` still reports two passes, although the flagged decision disappears when a thread joins the author group.
   Assert both operands' presence before comparing their positions, including the analogous heading and group ordering comparisons in these files.

Checked and found sound:

- The client request method, URL, project body, version checks, JSON error, reachability error, error-kind mapping, check-failed result decoding, and exit codes match the plan; token probes require `LODGE_TOKEN` in `Authorization` only and no token in printed output.
- The command and formatter lines match Python, with the prescribed init, held, dry-run approval, provisional-ID, and server changes; Unicode ID boundaries, escaped IDs, problem deduplication, exact thread messages, and stream selection are covered by the inspected tests.
- Drafts and attachments are read before settings, while ask, reply, and close message files are read after settings; a scratch precedence probe additionally confirmed attachment errors precede malformed settings and malformed settings precede all three message-file errors.
- `fromWire` recursively reverses `toWire` for the supported nested maps, sets, objects, arrays, nulls, and astral text; every guide change matches the plan, including the retained verbatim author-message instruction and the 60-line limit.
- `server.ts`, `project.ts`, and `support.ts` implement the prescribed in-memory server, authenticated approvals, clocks, store access, file fixtures, and optional binary transport; no socket or binary mode was exercised in this review.
- The parity statuses, reasons, dropped names, wheel deferral, and widened checks match the plan; `#cli` exports exactly the union of Tasks 2, 3, and 7a, without exposing the output helpers or guide text.

Validation: the clean focused run passed 250 tests, and `sh scripts/check-ts.sh` exited 0 with 1,741 passes and no failures.
The three additional scratch assertions passed on the original code; each of the two principal mutations made its corresponding assertion fail.
As a control on the report's mutation evidence, suppressing `readLines` freshness failed `check_deduplicates_every_problem_field` and `thread_wire_prints_closed_messages_exactly`.
Additional mutations of the empty-section fallback and a problem path without a line number survived the focused suite; these are branch-coverage limits, not observed implementation defects or additional lost Python assertions.
All source mutations were restored, scratch probe tests were removed, and the temporary worktree was removed after the review.
