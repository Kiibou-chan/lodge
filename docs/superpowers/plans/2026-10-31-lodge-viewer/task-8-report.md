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
