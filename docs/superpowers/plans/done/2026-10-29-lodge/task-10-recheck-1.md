# Task 10 recheck 1: fix round 1 (58c64f4, fb9e3bd)

Rechecked: the diff 8d690cb..fb9e3bd against task-10-review.md and the Task 10 `Ruling:` lines in the ledger.
Counts: 0 Blocking, 0 Important, 2 Minor (both new, both optional).
Verdict: every finding answered; the recheck is clean.

## What I ran

- A fresh copy of fb9e3bd (`git archive`, `probes-t10/fix/`), `sh scripts/check.sh` with `GIT_CONFIG_GLOBAL` empty and `GIT_CONFIG_NOSYSTEM=1`: green, 916 passed, the wheel test included.
- The new tests on the 8d690cb source with fb9e3bd's `tests/` (`probes-t10/old/`): every new test fails or errors.
  `test_same_second.py` errors at setup there, since its fixture patches `lodge.main.sleep`, so I also ran it on fb9e3bd with `_WAITS = 0` (`probes-t10/nowait/`): both e2e tests and 4 of 5 in `tests/app/test_writes_dates.py` fail; the one that passes is the far-future refusal, which needs no wait.
- `same_second.sh` against the fixed build: branch mode 3 of 3 runs published both adds, flagged the agent decision, and the gate said `ok`; checkout mode 5 of 5 runs flagged the agent decision (`s-… · current · coordinator · … · awaiting the author on d-…`), with `waiting` listing it and the gate passing; before the fix it was 5 of 7 runs credited to the author and 3 of 3 refused.
- The guide walk with an attachment, in both modes (`walk-checkout/`, `walk-branch/`), from the revised guide alone: a dry run with `--attach` wrote nothing, the add placed `lodge/attachments/<id>/runs.log` (staged in checkout mode, on the remote `lodge` branch in branch mode), its bytes kept exactly (a CRLF line survived), `show --provenance` printed `attachments: runs.log`, and the gate passed.
- Refusals, each one `lodge:` line with exit 2: a listing that does not match the attached names, the same file attached twice, a non-UTF-8 file, a directory; listing without `--attach` fails check 2 with exit 1.
- `lodge init` in an unwritable repository: `lodge: cannot create lodge/decisions/.gitkeep: Permission denied`, exit 2.
- A regression probe on the new date wait: an imported decision with a bare day, then a normal add, then a second import, on dfdea3c and fb9e3bd (`imp/`): all exit 0, since a bare day is stored as `2026-01-05T00:00:00+00:00`, so the aware comparison in `_after_newest` cannot meet a naive date.

## Findings

- I1: answered, `src/lodge/app/writes.py:141-154` (`_after_newest`, called once per attempt at line 81, so a retry after a rejected push waits against the fresh tree), `src/lodge/core/check_change.py:63-91` (new decisions dated after the decisions of `current` they link to or share an entry with), `src/lodge/main.py` `_Clock.sleep`.
- I2: answered, `src/lodge/app/writes.py:92-96, 115-138`, `src/lodge/cli/commands.py` `_read_attachments`, `src/lodge/cli/parser.py` `--attach` (append, one per file), `src/lodge/cli/guide.md:46-47`.
- M1: answered, `src/lodge/gitstore/setup.py:49-53`.
- M2: answered, `guide.md:52-55`, pinned by `test_guide_names_the_author_not_a_person`.
- M3: answered, `guide.md:28`.
- M4: answered, `guide.md:14`.
- M5: answered, `guide.md:44`.
- Test diff: one line removed (the `FixedClock` docstring, rewritten); no assertion weakened.

## The builder's concern 2: a standalone `check --gate` compares new decisions only with the published state

Adequate as built.
Every record file is written through `lodge add`, which now waits past the newest decision of the tree it starts from and checks new decisions against that tree, so no add can tie with anything it can see.
A tie the gate would miss needs two decisions, both new against the published state, that share a link or an entry and were added without either seeing the other.
A link needs the other's ID, so the second add saw the first and waited.
A shared entry needs two branches that edit the same entry file, and merging them conflicts in git on that file, so a person resolves it by hand, outside what the gate promises.
Cost if wrong: one more comparison among the new decisions in `_dates` (each new decision against the other new ones it shares an entry with), cheap to add later if the pilot shows a tie.

## New Minors (optional, park for the next round touching these files)

### N1 (Minor): the guide does not say the listed name is the attached file's base name

Handle: `src/lodge/cli/guide.md:46-47`, `src/lodge/cli/commands.py` `_read_attachments` (`Path(path).name`).
Scenario: an agent lists `attachments: [log]` and runs `--attach ../out/run-3.log`; it is refused with `the new decision lists [log] in attachments, but the attached files are [run-3.log]`, one sentence and exit 2, so it costs one retry.
Fix: "list each file's own name, as in `attachments: [runs.log]` for `--attach ../out/runs.log`".

### N2 (Minor): a decision dated ahead of the local clock makes every add wait about three seconds

Handle: `src/lodge/app/writes.py:147-153` (the newest decision of the whole tree, not only the related ones).
Scenario: in branch mode another machine whose clock runs ahead publishes a decision; until local time passes it, every add on this machine sleeps three times before going on, even an add unrelated to that decision.
Not run (I did not skew a clock); read from the loop.
Nothing goes wrong, since check 1 still refuses only a related decision that is not later; the cost is latency.
Fix, if the pilot shows it: wait only past the newest decision that the drafts link to or share an entry with, which is what check 1 needs.

## Files read

Read: `.claude/agents/rechecker.md`, the ledger's Task 10 rulings, the report's "Fix round 1", the source diff of `app/{writes,lodge,ports}.py`, `cli/{commands,parser}.py`, `core/check_change.py`, `gitstore/setup.py`, and `main.py`, all of `app/writes.py` at fb9e3bd, `guide.md:18-57` at fb9e3bd, `tests/e2e/test_same_second.py`, and the diff of `tests/e2e/{conftest,test_guide,test_init}.py`, `tests/app/fakes.py`, `tests/gitstore/repos.py`.
Not read: `tests/app/test_writes_{dates,attach}.py`, `tests/core/test_check_current.py`, and `tests/e2e/test_add_attach.py` beyond running them on both sources.
