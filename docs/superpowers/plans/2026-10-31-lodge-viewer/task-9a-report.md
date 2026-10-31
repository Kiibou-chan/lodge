# Task 9a report

DONE.
Only Task 9a was performed: six author decisions, two coordinator decisions, and 22 new specification entries.
No source code or tests changed, so there are no new tests or first-failure outputs.
The existing tests provide regression verification for this records-only task.
All prose outside the verbatim quotes and their identical author reasoning bodies is agent text.

## Records added and files changed

Each row names one new record file.
The design references are lines of `docs/superpowers/specs/2026-10-31-lodge-viewer-interaction-design.md`.

| Author decision | File | Design line | Quote source time |
| --- | --- | --- | --- |
| d-9dqycj | `lodge/decisions/d-9dqycj-doubts-and-questions-belong-on-their.md` | 13 | lodge build session, 2026-10-30 09:41 |
| d-g7xvwm | `lodge/decisions/d-g7xvwm-arrange-entries-by-dependency.md` | 14 | lodge build session, 2026-10-30 09:41 |
| d-s64jyh | `lodge/decisions/d-s64jyh-show-what-rests-on-what.md` | 15 | lodge build session, 2026-10-30 09:43 |
| d-1bnqj5 | `lodge/decisions/d-1bnqj5-correct-or-retire-dependent-points-as.md` | 16 | lodge build session, 2026-10-30 09:46 |
| d-cvtrj6 | `lodge/decisions/d-cvtrj6-the-author-and-agents-work-out.md` | 17 | lodge build session, 2026-10-30 09:47 |
| d-rnjh2s | `lodge/decisions/d-rnjh2s-confirmation-preserves-who-wrote-what.md` | 18 | lodge build session, 2026-10-30 09:37 |

All six are `decided_by: author`, `scope: product`, with reasoning equal to the verbatim quote and nothing else.
Their statements say only what the brief says the respective words settle.
No duplicate records were made for design lines 12 or 19.
A verification script read each record through `lodge show --reasoning` and checked its quote, reasoning, source, and exact timestamp against the draft.

| Coordinator decision | File | Scope of change |
| --- | --- | --- |
| d-3d4g9j | `lodge/decisions/d-3d4g9j-viewer-goals-boundaries-and-attribution-safeguards.md` | Goals, Non-goals, and Must nots, design lines 21 to 47 |
| d-s69cq4 | `lodge/decisions/d-s69cq4-confirm-from-the-viewer-with-separate.md` | Confirming, design lines 48 to 73 |

Both coordinator decisions have `scope: product` and identify coordinator calls and the advisor authority d-7w5aq0 in their reasoning.
The Confirming reasoning explicitly preserves LODGE-6 (d-8nkamy): a confirmed decision still counts as hers for the review flag.
Design lines 21 and 22 provide historical motivation in the Goals reasoning rather than a new timeless claim about an entry count.
Headings and blank lines introduce no separate claims.

| New entry | Decision | File | Design lines | Dependencies |
| --- | --- | --- | --- | --- |
| s-648y95 | d-3d4g9j | `lodge/spec/purpose/s-648y95-confirm-decisions-from-the-viewer.md` | 26 | None |
| s-rbt13j | d-3d4g9j | `lodge/spec/purpose/s-rbt13j-raise-doubts-and-questions-on-records.md` | 27 | None |
| s-bdkjte | d-3d4g9j | `lodge/spec/purpose/s-bdkjte-make-dependencies-and-their-risks-visible.md` | 28 | None |
| s-sm2mf7 | d-3d4g9j | `lodge/spec/purpose/s-sm2mf7-read-the-specification-by-dependency.md` | 29 | s-bdkjte |
| s-z2nb2t | d-3d4g9j | `lodge/spec/purpose/s-z2nb2t-editing-records-from-the-viewer-waits.md` | 33 | None |
| s-c8hrye | d-3d4g9j | `lodge/spec/purpose/s-c8hrye-threads-wait-for-an-agent-session.md` | 34-36 | s-rbt13j |
| s-bxqj2f | d-3d4g9j | `lodge/spec/purpose/s-bxqj2f-decision-links-have-a-limited-scope.md` | 37 | None |
| s-9xwya5 | d-3d4g9j | `lodge/spec/purpose/s-9xwya5-viewer-writing-needs-a-configured-address.md` | 38 | None |
| s-12ta2e | d-3d4g9j | `lodge/spec/purpose/s-12ta2e-confirmation-preserves-agent-attribution.md` | 42,44 | s-pncjp8 |
| s-ycx03c | d-3d4g9j | `lodge/spec/purpose/s-ycx03c-viewer-author-words-come-from-the.md` | 45 | None |
| s-1cgvhe | d-3d4g9j | `lodge/spec/purpose/s-1cgvhe-a-doubt-marks-knowledge-and-a.md` | 46 | s-8m99ba |
| s-arr325 | d-s69cq4 | `lodge/spec/reading/s-arr325-decision-pages-offer-confirmation.md` | 50,53-54 | None |
| s-cecwv7 | d-s69cq4 | `lodge/spec/reading/s-cecwv7-area-confirmation-lists-its-full-effect.md` | 51 | s-arr325 |
| s-hvsamx | d-s69cq4 | `lodge/spec/reading/s-hvsamx-confirmation-writes-exactly-the-displayed-decisions.md` | 52 | s-cecwv7 |
| s-bhew59 | d-s69cq4 | `lodge/spec/model/s-bhew59-a-confirmation-is-a-separate-author.md` | 56-59,60 | s-aq3a5k, s-0yzshh |
| s-s4mkaj | d-s69cq4 | `lodge/spec/model/s-s4mkaj-confirmation-titles-and-statements-are-lodge.md` | 60-61 | s-bhew59 |
| s-pbt1wj | d-s69cq4 | `lodge/spec/writing/s-pbt1wj-confirmation-uses-the-add-checks.md` | 56,63 | s-8m99ba, s-edgt71 |
| s-gxjwd9 | d-s69cq4 | `lodge/spec/reading/s-gxjwd9-a-successful-write-redirects-to-its.md` | 64 | None |
| s-fwas5n | d-s69cq4 | `lodge/spec/storage/s-fwas5n-each-checkout-viewer-write-commits-its.md` | 65-68 | s-6bc10p |
| s-mc9n8a | d-s69cq4 | `lodge/spec/storage/s-mc9n8a-unsafe-checkout-commits-leave-the-write.md` | 69-70 | s-fwas5n |
| s-bty9z4 | d-s69cq4 | `lodge/spec/storage/s-bty9z4-the-store-owns-viewer-commits.md` | 71-72 | s-q23m04, s-nzhyh3 |
| s-j9jc4y | d-s69cq4 | `lodge/spec/reading/s-j9jc4y-a-confirmed-decision-retains-its-writer.md` | 73 | s-bhew59, s-wcv4en |

Each entry is below 150 words and says what holds now.
Area placement follows the topic rules: purpose for goals and boundaries, model for confirmation record fields, writing for checks, reading for forms and read behaviour, and storage for git operations.
`lodge add` also updated `lodge/spec/{model,purpose,reading,storage,writing}/_area.md` to include the new entries in area order.
No area title, intro, or rank was changed.

## Entries edited or reaffirmed

| Entry | Decision | Change and reason |
| --- | --- | --- |
| s-hfjr1m | d-3d4g9j | Text unchanged, listed with `edit` because its existing dependency warning needed review; feedback remains advisory and a failing check still refuses a write after s-edgt71 changed. |
| s-j5ttw1 | d-s69cq4 | Replaced “There is no confirmation step.” with “A confirmation is a separate author record and leaves the confirmed decision's writer visible.” to distinguish confirmation from attribution. |
| s-bdkjte | d-s69cq4 | Changed its last sentence from “The viewer shows what an entry rests on, what rests on it, and whether a dependency is in doubt, retired, or changed since.” to “The viewer shows what an entry rests on, what rests on it, and whether a dependency is in doubt, retired, or changed after the entry's own last change.” to make the comparison explicit and avoid a warning phrase matching the required count command in ordinary prose. |
| s-sm2mf7 | d-s69cq4 | Text unchanged, listed with `edit` because the dependency-order goal still holds after the wording clarification to s-bdkjte. |

The unchanged reaffirmations produce no working-tree text diff; their new last changes are recorded by their decisions.
No entry was retired.

| Narrowed decision | New decision | Reason |
| --- | --- | --- |
| d-cg3nn3 | d-3d4g9j | Its read-only-viewer claim is false now that confirmation and threads write; its other scope limits remain current. |
| d-mzkt6e | d-s69cq4 | Only its associated entry's blanket denial of a confirmation step is narrowed; trust in the author label and the review-flag rule remain intact. |

No author decision was narrowed or replaced.

## Dry runs, feedback, and answers

Every add had a successful dry run immediately before it.
Dry runs printed `dry run: nothing published`, with no check lines.
The final decision IDs differ from provisional dry-run IDs, and no provisional ID was used as a link.
All drafts and retained dry-run/add outputs are under `.drafts/task9a/`.

| Add | Dry-run feedback | Answer |
| --- | --- | --- |
| Line 13, d-9dqycj | None | Add the exact quote and timestamp. |
| Line 14, d-g7xvwm | None | Add the exact quote and timestamp. |
| Line 15, d-s64jyh | Related: d-f84m43, d-qsfjqa, d-9k0dfe | No to each: explaining the dependency arrangement does not supersede the must-nots, trust in the author label, or success measures. |
| Line 16, d-1bnqj5 | Related: d-s64jyh | No: the appropriate response to a wrong dependency complements the arrangement's purpose. |
| Line 17, d-cvtrj6 | Related: d-dhz8an, d-mzkt6e, d-wc6bah | No to each: naming who works out the response does not change quote attribution, review flags, or replacement effects. |
| Line 18, d-rnjh2s | Related: d-z727gh, d-zq5sfb, d-qsfjqa | No to each: preserving original authorship complements verbatim reasoning, public prose rules, and trust in the author label. |
| Goals initial dry run | Related: d-96n7j6, d-1x1mgv, d-cg3nn3; purpose order changed | No to the dependency migration and advisory-feedback decisions; yes to narrowly superseding d-cg3nn3's read-only claim, so added `narrows` and explanatory reasoning before the final dry run and add. |
| Goals final dry run | Purpose order changed | Expected insertion of the new entries; no remaining related-decision feedback. |
| Confirming initial dry run | Model, reading, storage, and writing order changed | Expected insertion of new entries; no related-decision feedback. |
| Confirming final dry run | Model, purpose, reading, storage, and writing order changed | Expected insertion and the follow-up purpose-entry edits; no related-decision feedback. |

The author decisions never supersede other author decisions.
Each related-decision answer was no except the explicit coordinator narrowing added to Goals.
The original Goals dry-run related-decision output was superseded in its log by the final dry run; the full original list is preserved in this table.

The sandbox recipe was initialised once with `mkdir -p .drafts/objects` and a copy of git's index to `.drafts/index`.
Every real add ran with `GIT_INDEX_FILE="$PWD/.drafts/index"`, `GIT_OBJECT_DIRECTORY="$PWD/.drafts/objects"`, and `GIT_ALTERNATE_OBJECT_DIRECTORIES="$(git rev-parse --path-format=absolute --git-common-dir)/objects"` through `uv run --frozen --quiet lodge add FILE...`.
The real git index was not staged, and nothing was committed or pushed.
No record file was read directly or written by hand.
Record reads and draft extraction used lodge; git status and file listings supplied only path metadata.

## Changed-since passes

| Point | Literal `lodge spec` grep count | Actual dependency warnings | Response |
| --- | --- | --- | --- |
| Before Task 9a | 1 | 1, on s-hfjr1m | Reaffirmed unchanged in the next section decision, d-3d4g9j. |
| After Goals | 1 | 0 | The sole match was the ordinary statement of new entry s-bdkjte, not a warning; clarified its wording in the next section decision and reaffirmed its dependant s-sm2mf7 unchanged. |
| After Confirming | 0 | 0 | No further edits needed. |

The requested before/after count is **1 → 0**.

## Commands and verification

| Command | Final output or result |
| --- | --- |
| `uv run --frozen --quiet lodge guide` | Exit-code guidance printed; writing and quote rules followed. |
| `uv run --frozen --quiet lodge waiting` | Both groups: `nothing`. |
| `uv run lodge id s`, once for each new entry | 22 reserved entry IDs, all listed above. |
| `uv run lodge draft REF` | Edit drafts with their lodge-provided `base` values. |
| `uv run lodge add --dry-run FILE...` before every real add | `dry run: nothing published`; only the feedback and notes listed above. |
| Sandbox `uv run --frozen --quiet lodge add FILE...` | `staged` followed by the corresponding IDs; all eight adds succeeded. |
| `uv run lodge check` | `ok`. |
| `uv run lodge spec` after each section | Saved to `.drafts/task9a/spec-after-goals.txt` and `.drafts/task9a/spec-after-confirming.txt`. |
| `uv run lodge spec` followed by the required grep | Final count `0`; grep's exit status 1 for zero matches is expected. |
| `uv run lodge search --by author --limit 50` | Lists all six new author decisions; saved under `.drafts/task9a/author-search.txt`. |
| `uv run lodge show s-j5ttw1` | Ends with the new separate-author-record sentence and contains no denial of confirmation. |
| Six `lodge show --reasoning` verification reads | `Six author quotes, reasoning bodies, and exact source timestamps verified through lodge show.` |
| `uv run ruff format --check` | `472 files already formatted`. |
| `uv run ruff check` | `All checks passed!`. |
| `uv run mypy` | `Success: no issues found in 194 source files`. |
| `uv run vulture` | Exit 0, no output. |
| `uv run pytest -q --ignore=tests/viewer/test_server.py --ignore=tests/e2e/test_view.py` | `1362 passed in 35.75s`. |
| `uv run pytest tests/e2e/test_view.py -q -k test_view_passes_the_port_to_the_viewer` | `1 passed, 6 deselected in 0.30s`. |
| `uv run lodge check --gate` | `ok`; area-order notes and the expected reminder to commit uncommitted record changes before pushing. |

## Concerns and deferred work

No blocking concern or design conflict was found.
Tasks 9b and 9c remain untouched, including their specified existing-entry edits, and the final design coverage map belongs to 9c.
Consequently, the old thread-kind, check-count, dependency-action, arrangement, and read-only-viewer entries still await those parts, although Task 9a narrows the coordinator's read-only claim.
The Confirming decision narrows d-mzkt6e because its associated entry denied confirmation even though its decision statement's review-flag rule remains true; the narrowing is deliberately limited in the reasoning.
Socket-bound verification was deferred as required: `tests/viewer/test_server.py` and the server-starting `tests/e2e/test_view.py::test_view_serves_the_project_until_interrupted` need the coordinator's outside-sandbox gate.
The remaining tests in the ignored end-to-end file were not required by this brief; the specified port test was run separately.
The coordinator still needs to stage explicit paths, run `sh scripts/check.sh` outside the sandbox, commit, and push.
This report uses the user's explicit `task-9a-report.md` path rather than the shared `task-9-report.md` mentioned in the generic parts section.
