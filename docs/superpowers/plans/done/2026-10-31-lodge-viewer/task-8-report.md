# Task 8 report

Status: DONE.
Added 27 rests-on links on 20 entries through seven coordinator decisions.
Reviewed all 41 previous proposals against the counterfactual dependency rule and dropped 14 that only mention, elaborate on, or independently restate another entry.
The published baseline blocker is resolved by ruling d-mkstz5.

## Final links

| Area | Entry | Rests on | Reason | Decision ID |
| --- | --- | --- | --- | --- |
| hook | s-h12s8w | s-4nq741 | qualifies the behaviour of the hook introduced there. | d-r64643 |
| levels | s-fehz74 | s-wcv4en | sets guidance for the three defined reading levels. | d-ke9sgb |
| purpose | s-m83kjq | s-3ht96p | names its viewer speed measure explicitly. | d-en18e8 |
| purpose | s-582qav | s-dm37qr | names its read-only viewer rule explicitly. | d-en18e8 |
| reading | s-dm37qr | s-3n0ndk | names its search filters explicitly. | d-mcx8tx |
| reading | s-dm37qr | s-wcv4en | uses its definitions of reading levels. | d-mcx8tx |
| reading | s-dm37qr | s-0s9m2d | shows the awaiting-author list defined by its review rule. | d-mcx8tx |
| rollout | s-awc4kb | s-3ht96p | measures its cost and speed success criteria. | d-0my06b |
| rollout | s-awc4kb | s-ph9z0t | measures its correctness and use success criteria. | d-0my06b |
| rollout | s-yrz8fz | s-fehz74 | leaves the values of its length guidance open. | d-0my06b |
| rollout | s-x84e3h | s-yhppm5 | specifies the imported-record exemption to its quote check. | d-0my06b |
| rollout | s-x84e3h | s-kvwrqw | specifies the imported-record exemption to its entry check. | d-0my06b |
| structure | s-165qfh | s-ctywm6 | checks its import and front-door rules. | d-j9d4va |
| structure | s-165qfh | s-t9zd7a | checks its prohibition on impure core operations. | d-j9d4va |
| writing | s-hfjr1m | s-edgt71 | names its refusal rule explicitly. | d-96n7j6 |
| writing | s-hfjr1m | s-fehz74 | flags breaches of its length guidance. | d-96n7j6 |
| writing | s-qzk2yb | s-j70a0k | states one of its seven publication checks. | d-96n7j6 |
| writing | s-g2jwha | s-j70a0k | states one of its seven publication checks. | d-96n7j6 |
| writing | s-yhppm5 | s-j70a0k | states one of its seven publication checks. | d-96n7j6 |
| writing | s-kvwrqw | s-j70a0k | states one of its seven publication checks. | d-96n7j6 |
| writing | s-ms14fq | s-j70a0k | states one of its seven publication checks. | d-96n7j6 |
| writing | s-aw5a1j | s-j70a0k | states one of its seven publication checks. | d-96n7j6 |
| writing | s-s27z33 | s-j70a0k | states one of its seven publication checks. | d-96n7j6 |
| writing | s-edgt71 | s-j70a0k | applies its seven checks to reads and publication. | d-96n7j6 |
| writing | s-edgt71 | s-zv83s7 | uses its definition of the published-state comparison. | d-96n7j6 |
| writing | s-0s9m2d | s-01k42c | defines the display and clearing of its review flag. | d-96n7j6 |
| writing | s-dfejrb | s-01k42c | specifies when decisions carrying its review flag take effect. | d-96n7j6 |

Areas without links: constraints, model, and storage.

## Proposals dropped

| Area | Entry | Proposed target | Review |
| --- | --- | --- | --- |
| constraints | s-qkcp0s | s-9n7han | Installation evidence or authorisation remains true independently of the installation policy. |
| constraints | s-7m3smc | s-9n7han | Installation evidence or authorisation remains true independently of the installation policy. |
| model | s-q10vh5 | s-a67fqm | Status behaviour elaborates the record model and does not require the other statement to hold. |
| model | s-fmwe04 | s-s3z6ea | Status behaviour elaborates the record model and does not require the other statement to hold. |
| purpose | s-4ykcm0 | s-3ht96p | The upkeep prohibition states its own criterion without requiring the pilot measure. |
| reading | s-dm37qr | s-8f6scf | The viewer feature or shared-parser rule independently states its requirement. |
| reading | s-dm37qr | s-v022r0 | The viewer feature or shared-parser rule independently states its requirement. |
| reading | s-gg9chm | s-q4s548 | The viewer feature or shared-parser rule independently states its requirement. |
| rollout | s-awc4kb | s-5gmxyx | The evaluation or evidence rule stands independently of the rollout sequence or evaluation statement. |
| rollout | s-t7qz74 | s-awc4kb | The evaluation or evidence rule stands independently of the rollout sequence or evaluation statement. |
| storage | s-evv024 | s-z1zvb4 | Paths and storage choices remain coherent independently of the other storage statement. |
| storage | s-6bc10p | s-z1zvb4 | Paths and storage choices remain coherent independently of the other storage statement. |
| storage | s-hjf8cc | s-6bc10p | Paths and storage choices remain coherent independently of the other storage statement. |
| writing | s-01k42c | s-pncjp8 | The review-flag trigger elaborates the general protection principle and independently states its rule. |

Retained links include the four explicit ID references, the seven individual publication checks, structure checks of their governing rules, pilot measures of the defined success criteria, imported-record cases of the checks, and uses of defined levels, length guidance, published-state comparison, and review flags.
No entry statement changed; drafts were regenerated with `lodge draft`, adding only `rests_on`.
No cycle was accepted by validation.

## Dry-run feedback and answers

### hook

```text
feedback: d-t6s8nm (provisional): it replaces and narrows nothing, but these current decisions look related: d-s6mq0f (lodge ships a hook that gives feedback on hand edits), d-4dp4gm (Task 5: check 7 requires the area order to list exactly the current entries), d-6q3aga (Task 6: the rendered specification marks flagged entries in their headings); does d-t6s8nm replace or narrow any of them? If so, set replaces or narrows in the draft before adding it
dry run: nothing published
```

Answer to the related-decision question: no listed decision is replaced or narrowed.
This decision adds dependency metadata and leaves all existing statements and decisions intact.
Answer to `dry run: nothing published`: expected; the following sandbox add succeeded.

### levels

```text
feedback: d-m29cxg (provisional): it replaces and narrows nothing, but these current decisions look related: d-92t2m8 (Length guidance is soft, per level, and tuned in the pilot), d-r64643 (Rests-on links in area hook), d-4dp4gm (Task 5: check 7 requires the area order to list exactly the current entries); does d-m29cxg replace or narrow any of them? If so, set replaces or narrows in the draft before adding it
dry run: nothing published
```

Answer to the related-decision question: no listed decision is replaced or narrowed.
This decision adds dependency metadata and leaves all existing statements and decisions intact.
Answer to `dry run: nothing published`: expected; the following sandbox add succeeded.

### purpose

```text
feedback: d-tfhy79 (provisional): it replaces and narrows nothing, but these current decisions look related: d-vme42w (The viewer non-goal says editing from the viewer comes later), d-cg3nn3 (lodge's non-goals for now: no server, no MCP server, limited scope, soft limits, read-only viewer), d-5mhgpp (lodge's intent, goals, and success measures); does d-tfhy79 replace or narrow any of them? If so, set replaces or narrows in the draft before adding it
dry run: nothing published
```

Answer to the related-decision question: no listed decision is replaced or narrowed.
This decision adds dependency metadata and leaves all existing statements and decisions intact.
Answer to `dry run: nothing published`: expected; the following sandbox add succeeded.

### reading

```text
feedback: d-0hv4j7 (provisional): it replaces and narrows nothing, but these current decisions look related: d-x42f0x (The viewer is a local, read-only web page on the same parser as the command line), d-en18e8 (Rests-on links in area purpose), d-ke9sgb (Rests-on links in area levels); does d-0hv4j7 replace or narrow any of them? If so, set replaces or narrows in the draft before adding it
dry run: nothing published
```

Answer to the related-decision question: no listed decision is replaced or narrowed.
This decision adds dependency metadata and leaves all existing statements and decisions intact.
Answer to `dry run: nothing published`: expected; the following sandbox add succeeded.

### rollout

```text
feedback: d-m6j1bv (provisional): it replaces and narrows nothing, but these current decisions look related: d-zh00c5 (Open questions: the licence, a second project, and the length guidance values), d-bz7bav (lodge is rolled out in five steps, evaluated on the first user's past before a pilot), d-mcx8tx (Rests-on links in area reading); does d-m6j1bv replace or narrow any of them? If so, set replaces or narrows in the draft before adding it
dry run: nothing published
```

Answer to the related-decision question: no listed decision is replaced or narrowed.
This decision adds dependency metadata and leaves all existing statements and decisions intact.
Answer to `dry run: nothing published`: expected; the following sandbox add succeeded.

### structure

```text
feedback: d-yqg63f (provisional): it replaces and narrows nothing, but these current decisions look related: d-jxwj8m (Tests and tools enforce the structure from the first commit), d-0my06b (Rests-on links in area rollout), d-mcx8tx (Rests-on links in area reading); does d-yqg63f replace or narrow any of them? If so, set replaces or narrows in the draft before adding it
dry run: nothing published
```

Answer to the related-decision question: no listed decision is replaced or narrowed.
This decision adds dependency metadata and leaves all existing statements and decisions intact.
Answer to `dry run: nothing published`: expected; the following sandbox add succeeded.

### writing

```text
feedback: d-c5kbrq (provisional): it replaces and narrows nothing, but these current decisions look related: d-mzkt6e (An agent change to what the author decided raises a derived review flag), d-4032xv (The checks compare the last published state with the state about to be published), d-3epcjd (The check has seven checks and gates publication); does d-c5kbrq replace or narrow any of them? If so, set replaces or narrows in the draft before adding it
dry run: nothing published
```

Answer to the related-decision question: no listed decision is replaced or narrowed.
This decision adds dependency metadata and leaves all existing statements and decisions intact.
Answer to `dry run: nothing published`: expected; the following sandbox add succeeded.

There were no check lines, area-added notes, or missing-link questions for s-dm37qr, s-hfjr1m, s-m83kjq, or s-582qav in the final dry runs.
The former constraints check 4 failure no longer applies: the baseline now contains the entries, and the constraints proposals were dropped on semantic review.

## Waiting before and after

Before (`.drafts/waiting-before.txt`):

```text
waiting for an agent
nothing

waiting for the author
nothing
```

After (`.drafts/waiting-after.txt`):

```text
waiting for an agent
nothing

waiting for the author
nothing
```

`diff .drafts/waiting-before.txt .drafts/waiting-after.txt` exited 0 and printed nothing.

## Changes and commands

- `lodge/spec/`: 20 entry files gained only the approved dependency lists through `lodge add`.
- `lodge/decisions/`: seven coordinator decisions record the links and one-clause reasons.
- This report records the final links, rejected proposals, feedback, and verification.
- `.drafts/task8/` retains the final drafts, mapping, rejected proposals, and each dry-run and add output.
- Read `CLAUDE.md`, the brief, the earlier report, `lodge guide`, and ruling d-mkstz5.
- Read all ten areas with `uv run --frozen --quiet lodge spec --area NAME`.
- Captured `uv run --frozen --quiet lodge waiting` before and after.
- Regenerated each changed entry with `uv run --frozen --quiet lodge draft ID`.
- Copied the real index to `.drafts/index` and prepared `.drafts/objects` once for this resumed task.
- Each area ran `uv run --frozen --quiet lodge add --dry-run FILE...`, followed by the sandbox add with `GIT_INDEX_FILE`, `GIT_OBJECT_DIRECTORY`, and `GIT_ALTERNATE_OBJECT_DIRECTORIES` exactly as prescribed in the Global Constraints.
- All seven dry runs and seven adds exited 0; add output and actual decision IDs are retained in `.drafts/task8/AREA/add.txt`.
- `uv run lodge check`: `ok`.
- `grep -l '^rests_on:' lodge/spec/*/*.md | wc -l`: `20`, matching the table.

## Tests and concerns

No tests were added because this task changes records only, so no new-test first failing output applies.
The socket-bound suites `tests/viewer/test_server.py` and `tests/e2e/test_view.py` are excluded from the sandbox gate.
The socket-free port-passing test is run separately.
No commit or push was attempted; coordinator staging, full outside-sandbox gate, commit, and push remain the coordinator step.

Final validation results:

| Command | Result or last line |
| --- | --- |
| `uv run ruff format --check` | `442 files already formatted` |
| `uv run ruff check` | `All checks passed!` |
| `uv run mypy` | `Success: no issues found in 194 source files` |
| `uv run vulture` | Exit 0, no output. |
| `uv run pytest -q --ignore=tests/viewer/test_server.py --ignore=tests/e2e/test_view.py` | `1361 passed, 1 skipped in 41.06s` |
| `uv run pytest tests/e2e/test_view.py -q -k test_view_passes_the_port_to_the_viewer` | `1 passed, 6 deselected in 0.31s` |
| `uv run lodge check --gate` | `ok`, followed by `note: uncommitted record changes in lodge/; commit them before you push` |
| `git diff --check` | Exit 0, no output. |

Answer to the gate note: the coordinator will stage and commit the record changes as required by the brief.
No remaining concern was found in validation.


## Fix round 1

Status: DONE_WITH_CONCERNS.
I1 is fixed, M1 to M3 are addressed, and I2 has one pending link blocked by check 4 against the published baseline.
No commit, push, real-index staging, area edit, or entry statement change was made.
Task 9a's committed statements remain intact.

### Code and failing-first evidence

`tests/core/test_views_links.py` adds `test_same_second_change_does_not_mark_changed_since`, with two decisions dated at the same second and the target's ID sorting later.
Before the fix, its isolated run failed:

```text
E AssertionError: assert 'rests on s-bbbbbb, changed since' not in ('rests on s-bbbbbb, changed since',)
FAILED tests/core/test_views_links.py::test_same_second_change_does_not_mark_changed_since
1 failed in 0.18s
```

`src/lodge/core/views.py` now compares the datetime components of `order_key` for staleness, so only a strictly later instant marks an entry.
`derive.order_key` and its deterministic ordering remain unchanged.
The focused suite then reported `7 passed in 0.08s`, including existing tests for genuinely later changes, unchanged-text acknowledgements, and links that do not clear staleness.

### Added links

Read the current model, writing, reading, rollout, storage, and levels areas through `lodge spec`, and checked the Store definition through `lodge show s-q23m04`.
Each row below satisfies the brief's rule because its source uses the target's field or rule definition.
Existing rests-on targets were preserved in every draft.

| Area | Entry | Rests on | Reason | Decision ID |
| --- | --- | --- | --- | --- |
| model | s-fmwe04 | s-0yzshh | uses the replaces field defined there to derive decision status. | d-mmv96b |
| model | s-q10vh5 | s-0yzshh | uses the changes field defined there to derive entry retirement. | d-mmv96b |
| writing | s-hfjr1m | s-f859z1 | requires the numbers handles defined there for numeric feedback. | d-a16d4m |
| writing | s-hfjr1m | s-0s9m2d | advises about the derived review flag defined there. | d-a16d4m |
| writing | s-0s9m2d | s-0yzshh | uses its confirms and replaces fields to clear the review flag. | d-a16d4m |
| writing | s-edgt71 | s-q23m04 | requires its Store port to supply both snapshots for checking. | d-a16d4m |
| rollout | s-x84e3h | s-f859z1 | requires its imported_from field to identify converted records. | d-k76ycc |
| storage | s-sgprxs | s-aq3a5k | uses its work_item field to identify the implementation branch. | d-yepmqg |
| reading | s-dm37qr | s-v022r0 | displays the specification rendering defined there. | d-ejdyds |
| reading | s-dm37qr | s-8f6scf | displays both directions under its stored-once link rule. | d-ejdyds |

Ten links were added on eight entries through six link-only coordinator decisions.
The levels decision d-knfmh8 adds no edge: it restates the existing s-fehz74 to s-wcv4en link with a stronger reason for M3, using an unchanged draft and action `link`.
Areas gaining links are model, writing, rollout, storage, and reading.
The current tree has 36 entries with rests-on lists, including Task 9a's links; constraints remains without links.

M1 is fixed by the two reading links above, superseding the earlier report's dropped-proposal explanations for those edges.
M2 is fixed by the glossary policy line in the progress ledger: the first user and the pilot alone do not create a dependency; operational fields and rule definitions do.
M3 is fixed through new immutable decisions: d-ejdyds explains that s-dm37qr requires the waiting-list membership definition from s-0s9m2d; d-knfmh8 explains that the length guidance assigns limits to statement and reasoning content defined by s-wcv4en; d-a16d4m explains that the identities of checks 4, 5, and 6 come from s-j70a0k's numbered order.
No existing decision was edited.

### Remaining I2 link and check 4

The proposed s-j5ttw1 to s-aq3a5k link is valid: its author attribution and required quote use fields defined by s-aq3a5k.
However, its dry run failed before any writing-area add:

```text
check 4: d-chdsxc (provisional): lists link for s-j5ttw1, which changes more than rests_on; list it with action edit
not published: the check failed
```

Task 9a edited s-j5ttw1 after the published baseline, and check 4 compares the current entry to that baseline rather than to the committed Task 9a tree.
Changing the draft action to `edit` would violate the requested link-only operation for this addition.
The pending draft is retained under `.drafts/task8-fix1/deferred/`; retry its link through a writing-area decision after the published baseline includes Task 9a.
The failed area batch published nothing; the final successful writing batch excludes that entry.
The existing baseline and check were preserved.

### Keeping changed since at zero

The added s-edgt71 to s-q23m04 edge exposed a real timestamp difference: the Store definition d-fkndvh is later than the check definition d-4032xv.
The statements remain compatible: the Store supplies exactly the current and published snapshots required by the check.
Following `lodge guide`, separate coordinator decision d-76nt3b uses unchanged-text `edit` actions for s-edgt71 and its direct dependants s-hfjr1m and s-pbt1wj, acknowledging their continued validity together.
This is an additional acknowledgement decision beyond the brief's link-only batches, necessary to retain the required edge and return the requested staleness count to zero.
The drafts came from `lodge draft`, with no statement or metadata changes in that acknowledgement.
Final `lodge spec` contains zero occurrences of `changed since`.

### Dry runs, adds, and feedback

Prepared `.drafts/index` and `.drafts/objects` once, then used the Global Constraints' `GIT_INDEX_FILE`, `GIT_OBJECT_DIRECTORY`, and `GIT_ALTERNATE_OBJECT_DIRECTORIES` recipe for every real add.
Each successful add had a preceding successful dry run, with no check line.
Drafts and complete dry-run and add outputs are retained under `.drafts/task8-fix1/AREA/`.
The following are the final dry-run outputs, with each class of feedback answered below.

#### model

```text
feedback: d-hvjqwx (provisional): it replaces and narrows nothing, but these current decisions look related: d-z57dy1 (A decision records a change, with fields for who, what, and the evidence), d-6cyjdh (A specification entry says what holds now and has no reasoning of its own), d-96n7j6 (Rests-on links in area writing); does d-hvjqwx replace or narrow any of them? If so, set replaces or narrows in the draft before adding it
note: area model: order changed
note: area purpose: order changed
note: area reading: order changed
note: area storage: order changed
note: area writing: order changed
dry run: nothing published
```

#### writing

```text
feedback: d-103w8b (provisional): it replaces and narrows nothing, but these current decisions look related: d-3d4g9j (Viewer goals, boundaries, and attribution safeguards), d-96n7j6 (Rests-on links in area writing), d-mzkt6e (An agent change to what the author decided raises a derived review flag); does d-103w8b replace or narrow any of them? If so, set replaces or narrows in the draft before adding it
note: area model: order changed
note: area purpose: order changed
note: area reading: order changed
note: area storage: order changed
note: area writing: order changed
dry run: nothing published
```

#### rollout

```text
feedback: d-k1ebx1 (provisional): it replaces and narrows nothing, but these current decisions look related: d-0my06b (Rests-on links in area rollout), d-bz7bav (lodge is rolled out in five steps, evaluated on the first user's past before a pilot), d-a16d4m (Rests-on links in area writing); does d-k1ebx1 replace or narrow any of them? If so, set replaces or narrows in the draft before adding it
note: area model: order changed
note: area purpose: order changed
note: area reading: order changed
note: area storage: order changed
note: area writing: order changed
dry run: nothing published
```

#### storage

```text
feedback: d-6w57yg (provisional): it replaces and narrows nothing, but these current decisions look related: d-knqtc2 (The git adapter reads a checkout or a branch, and the first user's records live on a branch), d-k76ycc (Rests-on links in area rollout), d-a16d4m (Rests-on links in area writing); does d-6w57yg replace or narrow any of them? If so, set replaces or narrows in the draft before adding it
note: area model: order changed
note: area purpose: order changed
note: area reading: order changed
note: area storage: order changed
note: area writing: order changed
dry run: nothing published
```

#### reading

```text
feedback: d-3wd5dv (provisional): it replaces and narrows nothing, but these current decisions look related: d-mcx8tx (Rests-on links in area reading), d-x42f0x (The viewer is a local, read-only web page on the same parser as the command line), d-yepmqg (Rests-on links in area storage); does d-3wd5dv replace or narrow any of them? If so, set replaces or narrows in the draft before adding it
note: area model: order changed
note: area purpose: order changed
note: area reading: order changed
note: area storage: order changed
note: area writing: order changed
dry run: nothing published
```

#### levels

```text
feedback: d-4y18nw (provisional): it replaces and narrows nothing, but these current decisions look related: d-ke9sgb (Rests-on links in area levels), d-92t2m8 (Length guidance is soft, per level, and tuned in the pilot), d-ejdyds (Rests-on links in area reading); does d-4y18nw replace or narrow any of them? If so, set replaces or narrows in the draft before adding it
note: area model: order changed
note: area purpose: order changed
note: area reading: order changed
note: area storage: order changed
note: area writing: order changed
dry run: nothing published
```

#### acknowledgement

```text
feedback: d-chn399 (provisional): it replaces and narrows nothing, but these current decisions look related: d-a16d4m (Rests-on links in area writing), d-s69cq4 (Confirm from the viewer with separate author records and explicit commits), d-3d4g9j (Viewer goals, boundaries, and attribution safeguards); does d-chn399 replace or narrow any of them? If so, set replaces or narrows in the draft before adding it
note: area model: order changed
note: area purpose: order changed
note: area reading: order changed
note: area storage: order changed
note: area writing: order changed
dry run: nothing published
```

Answers to every related-decision question: none of the listed decisions is replaced or narrowed; these decisions add dependency metadata, strengthen link explanations, or acknowledge unchanged statements.
The `order changed` notes compare the branch's existing area orders to the published baseline; no area files were written by this round, as verified by `git diff --name-only`.
Every `dry run: nothing published` line is expected; the corresponding sandbox add succeeded.
The earlier rejected writing dry run also advised that its reasoning used numbers 4, 5, and 6 without handles; the successful writing draft includes handles to `lodge show s-j70a0k` for all three.
The initial acknowledgement dry run advised about the task and round digits; those labels were written as words before the successful dry run and add.
The final gate's uncommitted-record note is expected because the user explicitly requested no commit.

### Validation

| Command | Final result |
| --- | --- |
| `uv run ruff format --check` | `473 files already formatted` |
| `uv run ruff check` | `All checks passed!` |
| `uv run mypy` | `Success: no issues found in 194 source files` |
| `uv run vulture` | Exit 0, no output. |
| `uv run pytest -q --ignore=tests/viewer/test_server.py --ignore=tests/e2e/test_view.py` | `1363 passed in 35.84s` |
| `uv run pytest tests/e2e/test_view.py -q -k test_view_passes_the_port_to_the_viewer` | `1 passed, 6 deselected in 0.30s` |
| `uv run --frozen --quiet lodge check --gate` | `ok`, existing area-order notes, and expected uncommitted-record note. |
| `lodge spec` occurrence count for `changed since` | `0` |
| `grep -l '^rests_on:' lodge/spec/*/*.md` count | `36` |
| Before/after `lodge waiting` diff | Exit 0, no output; nothing waits in either group. |
| `git diff --check` | Exit 0, no output. |

Socket-bound suites `tests/viewer/test_server.py` and the remaining `tests/e2e/test_view.py` tests were excluded as required by the sandbox brief.
The coordinator still needs to run the whole outside-sandbox gate.
The only unresolved review item is the s-j5ttw1 link described above.
