# Task 8 report

Status: BLOCKED.
The first area dry run failed check 4, so work stopped as the brief requires.
No `lodge add` ran, no record files changed, and no decisions were created.

## Changes per file

- This report records the proposed links, validation, and blocker.
- `.drafts/waiting-before.txt` holds the initial waiting output.
- `.drafts/spec-NAME.txt` holds each area read through `lodge spec --area NAME`.
- `.drafts/task8/AREA/s-ID.md` holds 31 entry drafts made with `lodge draft`, each with only a `rests_on` header line added.
- `.drafts/task8/AREA/decision.md` holds one proposed coordinator decision for each of the ten areas.
- `.drafts/task8/constraints/dry-run.txt` holds the failing dry-run output.
- `.drafts/task8/links.json` and the Python helpers under `.drafts/` hold the proposed mapping and reproducible preparation.
- `.drafts/index` and `.drafts/objects/` were prepared using the required sandbox recipe but never used for an add.

## Proposed links

These are proposals only: all decision IDs are pending, and the count of entries changed is zero.
The drafts propose 41 links on 31 entries across ten areas.

| Area | Entry | Rests on | Reason | Decision ID |
| --- | --- | --- | --- | --- |
| constraints | s-qkcp0s | s-9n7han | checks installation from the required public tag. | Pending, not added |
| constraints | s-7m3smc | s-9n7han | states the authorisation needed for the required install. | Pending, not added |
| hook | s-h12s8w | s-4nq741 | qualifies the behaviour of the hook introduced there. | Pending, not added |
| levels | s-fehz74 | s-wcv4en | sets guidance for the three defined reading levels. | Pending, not added |
| model | s-q10vh5 | s-a67fqm | defines the statuses of the specification entry introduced there. | Pending, not added |
| model | s-fmwe04 | s-s3z6ea | defines the statuses of the decision introduced there. | Pending, not added |
| purpose | s-m83kjq | s-3ht96p | names its viewer speed measure explicitly. | Pending, not added |
| purpose | s-582qav | s-dm37qr | names its read-only viewer rule explicitly. | Pending, not added |
| purpose | s-4ykcm0 | s-3ht96p | uses its upkeep cost success measure. | Pending, not added |
| reading | s-dm37qr | s-3n0ndk | names its search filters explicitly. | Pending, not added |
| reading | s-dm37qr | s-wcv4en | uses its definitions of reading levels. | Pending, not added |
| reading | s-dm37qr | s-8f6scf | shows the two directions of its stored links. | Pending, not added |
| reading | s-dm37qr | s-v022r0 | shows the specification rendered by its rule. | Pending, not added |
| reading | s-dm37qr | s-0s9m2d | shows the awaiting-author list defined by its review rule. | Pending, not added |
| reading | s-gg9chm | s-q4s548 | applies its shared parser and check rule to the viewer. | Pending, not added |
| rollout | s-awc4kb | s-5gmxyx | details the evaluation step of its rollout. | Pending, not added |
| rollout | s-awc4kb | s-3ht96p | measures its cost and speed success criteria. | Pending, not added |
| rollout | s-awc4kb | s-ph9z0t | measures its correctness and use success criteria. | Pending, not added |
| rollout | s-t7qz74 | s-awc4kb | specifies the evidence used for its measurement. | Pending, not added |
| rollout | s-yrz8fz | s-fehz74 | leaves the values of its length guidance open. | Pending, not added |
| rollout | s-x84e3h | s-yhppm5 | specifies the imported-record exemption to its quote check. | Pending, not added |
| rollout | s-x84e3h | s-kvwrqw | specifies the imported-record exemption to its entry check. | Pending, not added |
| storage | s-evv024 | s-z1zvb4 | specifies the paths for its Markdown records in git. | Pending, not added |
| storage | s-6bc10p | s-z1zvb4 | implements its replaceable storage interface with git. | Pending, not added |
| storage | s-hjf8cc | s-6bc10p | chooses its named-branch storage mode for the first user. | Pending, not added |
| structure | s-165qfh | s-ctywm6 | checks its import and front-door rules. | Pending, not added |
| structure | s-165qfh | s-t9zd7a | checks its prohibition on impure core operations. | Pending, not added |
| writing | s-hfjr1m | s-edgt71 | names its refusal rule explicitly. | Pending, not added |
| writing | s-hfjr1m | s-fehz74 | flags breaches of its length guidance. | Pending, not added |
| writing | s-qzk2yb | s-j70a0k | states one of its seven publication checks. | Pending, not added |
| writing | s-g2jwha | s-j70a0k | states one of its seven publication checks. | Pending, not added |
| writing | s-yhppm5 | s-j70a0k | states one of its seven publication checks. | Pending, not added |
| writing | s-kvwrqw | s-j70a0k | states one of its seven publication checks. | Pending, not added |
| writing | s-ms14fq | s-j70a0k | states one of its seven publication checks. | Pending, not added |
| writing | s-aw5a1j | s-j70a0k | states one of its seven publication checks. | Pending, not added |
| writing | s-s27z33 | s-j70a0k | states one of its seven publication checks. | Pending, not added |
| writing | s-edgt71 | s-j70a0k | applies its seven checks to reads and publication. | Pending, not added |
| writing | s-edgt71 | s-zv83s7 | uses its definition of the published-state comparison. | Pending, not added |
| writing | s-01k42c | s-pncjp8 | implements its flag for agent changes to author decisions. | Pending, not added |
| writing | s-0s9m2d | s-01k42c | defines the display and clearing of its review flag. | Pending, not added |
| writing | s-dfejrb | s-01k42c | specifies when decisions carrying its review flag take effect. | Pending, not added |

Areas without proposed links: none.
Areas with actual added links: none.

## Dry-run feedback and answers

Only constraints reached dry run.
No other area was dry-run or added after the check line.

```text
feedback: d-4wrvjz (provisional): it replaces and narrows nothing, but these current decisions look related: d-jj72ps (lodge runs as a command-line tool installed from a public tag in each session), d-4dp4gm (Task 5: check 7 requires the area order to list exactly the current entries), d-6q3aga (Task 6: the rendered specification marks flagged entries in their headings); does d-4wrvjz replace or narrow any of them? If so, set replaces or narrows in the draft before adding it
note: area constraints: added
note: area hook: added
note: area levels: added
note: area model: added
note: area purpose: added
note: area reading: added
note: area rollout: added
note: area storage: added
note: area structure: added
note: area writing: added
check 4: d-4wrvjz (provisional): lists link for s-7m3smc, which is new; list it with action create
check 4: d-4wrvjz (provisional): lists link for s-qkcp0s, which is new; list it with action create
not published: the check failed
dry run: nothing published
```

- Related-decision feedback: no replacement or narrowing is intended, because the proposed decisions add dependency metadata only and leave every existing statement intact.
- Each of the ten `note: area NAME: added` lines: unexpected, because this checkout already presents all ten areas through `lodge spec`; these notes accompany the failed dry run and published nothing.
- `check 4` for s-7m3smc: blocked, because the brief requires action `link`, while the comparison treats the existing entry as new and asks for `create`.
- `check 4` for s-qkcp0s: blocked for the same reason.
- `not published: the check failed`: honoured; no add was attempted.
- `dry run: nothing published`: expected and confirmed by the dry-run result.

## Commands and results

| Command | Result or last line |
| --- | --- |
| `cat docs/superpowers/plans/2026-10-31-lodge-viewer/task-8-brief.md` | Read the task requirements. |
| `cat CLAUDE.md` | Read repository instructions. |
| `rg --files -g AGENTS.md -g "!lodge/**" -g "!uv.lock"` | No matching instruction files. |
| `uv run --frozen --quiet lodge --help` | `Agents: start with lodge guide.` |
| `mkdir -p .drafts/objects` | Exit 0. |
| `uv run --frozen --quiet lodge waiting > .drafts/waiting-before.txt` | Exit 0, snapshot saved. |
| `uv run --frozen --quiet lodge spec` | Exit 0, read every entry. |
| `uv run --frozen --quiet lodge guide` | Exit 0, guide read. |
| `uv run --frozen --quiet lodge spec --help` | `only this area` |
| `git status --short` | Only the supplied task brief was untracked initially. |
| `rg --files lodge/spec` with path filtering | Listed the ten area names without reading record files. |
| `uv run --frozen --quiet lodge spec --area NAME > .drafts/spec-NAME.txt` for all ten areas | Exit 0 for each. |
| `uv run --frozen --quiet lodge draft s-dm37qr` | Printed the editable draft. |
| `uv run --frozen --quiet lodge show s-j70a0k --provenance` | `changed by: d-3epcjd (current)` |
| `uv run --frozen --quiet python .drafts/prepare_task8.py` | `Prepared 31 entry drafts across 10 areas; 41 links.` |
| Sandbox index copy from the Global Constraints | Exit 0. |
| `uv run --frozen --quiet python .drafts/add_task8.py` | Exit 1; `dry run: nothing published`. |
| `uv run --frozen --quiet python .drafts/report_task8.py` | Wrote this report. |

The add helper first ran `uv run --frozen --quiet lodge add --dry-run .drafts/task8/constraints/decision.md .drafts/task8/constraints/s-7m3smc.md .drafts/task8/constraints/s-qkcp0s.md`.
It stopped immediately on failure, before executing its sandbox-environment add command.

## Tests and verification

No tests were added, because this task changes records only and requires no code.
There is therefore no new-test first failing output; the first failing validation is the dry run reproduced above.
The builder gate and final check, link count, and waiting comparison were not run after the mandatory stop.
The socket-bound suites are `tests/viewer/test_server.py` and `tests/e2e/test_view.py`, with the brief excluding the latter file's socket-free `test_view_passes_the_port_to_the_viewer` from that limitation.
No tests were run in this blocked task.

## Concerns and coordinator follow-up

The current-versus-published comparison appears to regard existing areas and entries as new.
The coordinator needs to resolve that baseline issue before these link-only changes can pass check 4.
Changing the actions to `create` would violate the brief, so the drafts retain `link`.
The remaining proposed links have not reached validation and need review against the dependency rule, particularly the interpretation of whole-rule cases and defined terms.
The four named-reference entries have prepared drafts, but their missing-link feedback has not been verified as cleared.
No commit or push was attempted.
