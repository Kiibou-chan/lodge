# Final fix wave

Sources: `final-review-correctness.md` (R1, G1 to G4, C1 to C3, A1, H1) and `final-review-design.md` (D1 to D13) in this folder, plus the ledger's parked minors.
Each item below names the finding; read its Handle, Scenario, and Fix in the review file, and follow the ruling here where it differs.
Test-first for every behaviour change: write the test, see it fail, then fix.
Held for the author, do not touch: D1 (reads running checks 4 to 6), D13 (the spec and the brainstorm), and every file under `lodge/`.
D12 is done by the coordinator.

## Part A: Important and must-fix

1. G4, a rewritten `lodge` branch.
   In `_fetch`, read the tracking ref before fetching; when the new tip does not contain the old (`merge-base --is-ancestor old new` fails), keep the old tip under `refs/lodge/rewritten/<UTC time>` and expose it through the Store port as the published tree for `check --gate`, so check 5 compares old and new.
   Reads print one line in the freshness text: "the lodge branch was rewritten since the last fetch; the previous tip is kept at <ref>; run lodge check --gate".
   Keep `core` and `app` pure: the time comes through `Clock`.
2. C1, the checkout gate.
   `check --gate` in checkout mode checks two states against the published one, `HEAD`'s tree and the working tree, and fails when either fails, naming which (`committed:` or `working tree:` before the problem).
   When the working tree's `lodge/` differs from `HEAD`'s, print a note: "uncommitted record changes in lodge/; commit them before you push".
3. C2, a missing base.
   Tell "no history" (unborn `HEAD`, or no commit holds `lodge/`) from "base not found" (neither ref resolves, or `merge-base` fails).
   In the second case `check --gate` exits 2 with one sentence naming the refs it tried and the `base` setting; reads say it in the freshness line.
4. G1, a killed add.
   In `main`, SIGTERM and SIGHUP raise `SystemExit` (143 and 129) so every `finally` runs.
   In branch mode, a read that cannot take the lock within the wait serves the cached ref, with the freshness line "not fetched: another lodge holds <lock path>", as the offline rule serves the cache on a failed fetch; writes keep waiting and reporting as now.
5. R1, author lookalikes.
   Check 3 reports a `decided_by` that is not exactly `author` but whose stripped, casefolded form contains `author`: "decided_by is <value>; write author exactly, with a quote, or use your own role".
6. D2, her decision behind an agent's entry edit.
   In `derive`, a flagged decision that changes an entry is also filed against the decision behind that entry's previous standing change when that decision is hers or confirmed by her, so her decision shows `awaiting the author on <id>`; a test beside `test_level1_status_who_flags`.
7. Task 5 N1 (parked, must-fix): author reasoning is compared exactly in check 5 (`check_immutable.py:24`), not by word list; an agent's reasoning keeps the word comparison.

## Part B: Minors

1. G2: `update-ref <ref> <commit> <tip>`, its failure ignored.
2. G3: when the tip is neither the commit nor its parent, fetch and count the push as landed if `merge-base --is-ancestor <commit> <tip>`.
3. C3: in branch mode `check --gate` prints a note that the gate runs inside `lodge add`; the guide says a hand push to the branch skips it.
4. A1 and D3: a fourth outcome `UNCHANGED`, printed `nothing changed`, the note dropped.
5. H1: `FROZEN_TEXT` adds "If the author asked for this edit, tell her the file is frozen and ask before reversing it."
6. D4: the timeline reports `more` and the page says "50 of N shown".
7. D5: the remedies on the four commonest check messages, as the review words them.
8. D6: `lodge draft` of a decision prints a stderr note "decisions are immutable; to change one, write a new decision with replaces or narrows", and the `draft` help says so.
9. D7 and Task 13 M1: dry-run feedback marks new IDs `(provisional)`, and the guide says the real add mints new IDs.
10. D8: `lodge spec` on an empty store prints "Nothing is recorded yet."; `lodge init` ends with "next: lodge guide"; a busy port names `--port`.
11. D9: one `core` function for the level-1 header parts, used by `views._head` and the viewer's `meta`.
12. D10: `core.attachment_path(decision_id, name)` and `core.ATTACHMENTS`, used by the five places.
13. D11: an entry's level 2 in the viewer renders `Level1` views, not linked CLI text.
14. Task 7 N1: the ID message names the expected prefix and form instead of always "IDs are lower case".
15. Task 8 M5 and R4: feedback "d-aaaaaa is already replaced by d-cccccc"; a test for the entry branch of `_raced` (construction in `task-8-recheck-2.md`).
16. Task 9 M1: create new files with `os.open(..., O_CREAT | O_EXCL | O_NOFOLLOW, 0o666)` instead of reading the umask by setting it.
17. Task 10 N1 and N2: the guide says a listed attachment name is the file's base name; the add's date wait applies only when the newest decision is within a few seconds ahead of the clock, and says so otherwise.
18. Task 11 N1 and N2: `render_spec` escapes indented `#` lines and underline headings; flag IDs on search, timeline, and spec rows are links.
19. Task 12 N1: a relative path without a payload `cwd` is resolved the same way in `context` and `respond`.
20. The `Derived` docstring says its maps hold known entries only; a project-named constant in `tests/core/derivation.py` becomes `IMPORTED`.
21. Part A recheck 2 (`final-wave-a-recheck-2.md`), M1: the deferred exit counts git calls per thread and defers only when the main thread runs git, so `lodge view` stops on SIGTERM.
22. M2: the rewrite test fails closed when git cannot answer (an error is reported, the accepted ref does not move); the README says detection lives in a clone that read the branch before the rewrite.
23. M3: an add refused over a rewrite prints the rewrite line, ending "tell the author; only the author accepts a rewrite".
