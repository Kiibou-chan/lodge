# Task 10 review: the command line, the guide, and the composition root

Reviewed: dfdea3c against BASE dcc5c0c, worktree build-0.1, read-only.
Probes ran in a scratch copy (`git archive dfdea3c`) under `scratchpad/probes-t10/`, with git only in temporary directories, `GIT_CONFIG_GLOBAL` an empty file, and `GIT_CONFIG_NOSYSTEM=1`.

Counts: 0 Blocking, 2 Important, 5 Minor.

Verdicts: spec compliance yes, with the gaps in I1 and I2 (both reached through this task's wiring, neither caused by its code alone); task quality not approved until I1 and I2 have a ruling.

## What I ran

- `uv run pytest -q -m "not slow"` in the scratch copy: 884 passed, 1 deselected (the wheel test, not rerun).
- Fresh-agent walk (`w1/`, checkout mode): from `lodge guide` alone, `lodge init`, `lodge id s`, an author decision with a quote, a new entry, and a new area, `lodge add --dry-run`, then `lodge add`, then `search`, `show --reasoning --provenance` on both records, `check`, and `check --gate`.
- `same_second.sh checkout|branch`: an author decision creating an entry, then in the same shell `lodge draft` of the entry, a text edit, and an agent decision editing it, started at the top of a wall-clock second; 3 runs in branch mode, 7 in checkout mode.
- Error paths (`w3/`): outside a repository, before init, malformed and invalid `.lodge.toml`, branch mode with no remote, bad YAML, no header, non-UTF-8 draft, a directory as a draft, a missing draft, unknown refs and areas, `view`, odd `hook` argv, an unwritable `lodge/decisions`, and `init` in an unwritable checkout.
- A hand-broken entry file in `w1/`, then `search`, `show`, `spec`, `waiting`, `check`, and `draft`.
- Attachments in both modes (`ss-checkout/`, `ss-branch/`): a decision draft with an `id` from `lodge id d`, then the route of adding first and attaching through `lodge draft`.

## Correctness

### I1 (Important): two adds in one second silently credit an agent's edit to the author in checkout mode, and refuse without a remedy in branch mode

Handles: `src/lodge/app/writes.py:64` (the date is `now.isoformat(timespec="seconds")`), `src/lodge/core/derive.py:17` (decisions ordered by date, ties by ID), `src/lodge/core/check_change.py:56-81` (dates compared only with the published state).
Scenario, checkout mode (`same_second.sh checkout`): an author decision creates an entry, and within the same second an agent decision edits it.
In 5 of 7 runs the agent's decision sorted before hers, and then `lodge show <entry>` printed `s-… · current · author · 2026-10-29 · storage`, the agent's text (`stored whole, compressed`), and her quote under it; `lodge waiting` printed `nothing waits for the author`; `lodge check --gate` printed `ok`, exit 0.
That is must-not 1 (wrong information, more settled than it is) and must-not 2 (a quiet rewrite of her entry), and the gate does not catch it, because both decisions are new against the published state, so `_dates` never compares them.
Scenario, branch mode (`same_second.sh branch`, 3 of 3 runs): the first add publishes, the second is refused with `check 1: d-…: dated 2026-10-29T18:04:51+01:00, no later than d-…, which shares s-… with it` and exit 1.
The agent cannot act on that message: `date` is filled by lodge, the guide (`guide.md:26`) says so, and the guide reads exit 1 as "check failed", not "add again".
Reach: both need two adds inside one wall-clock second, which a scripted chain in one Bash call gives (my probe did it with `lodge add`, `lodge draft | sed`, `lodge add`).
An interactive agent making each step a separate tool call is seconds apart and does not hit it; I could not measure tool-call latency here, so that part is inferred, not run.
So the builder's concern 5 and the ledger ruling's "Real use is not affected" hold for interactive use only; scripted use reaches both failures, and the checkout one is silent.
Why not Blocking: it needs sub-second chaining of two writes on the same entry.
Fix: in `Lodge.add` (app), read the clock until its second is later than the newest decision date in the current state (at most one second of waiting, through the clock port), so every add is dated strictly after every decision before it and neither mode ties; and extend `_dates` to compare a new decision with the decisions of the current state it links to or shares an entry with, so a tie that still arrives (an import, a hand edit) is a check failure rather than a coin toss.
Tests: a fake clock returning the same second twice, then the next; an add after an add in that second is dated one second later; checkout-mode `waiting` lists the agent decision.
Owner: the app (Task 8's code), exposed now that `main` wires the real clock; a ruling for the integrator.

### I2 (Important): the guide's attachment rule cannot be followed on a first try, and not at all in branch mode

Handles: `src/lodge/cli/guide.md:44`, `src/lodge/core/apply.py:100` (`a new decision draft carries no id`), `src/lodge/core/check_state.py:101-105` (check 2: the file must exist at `lodge/attachments/<id>/<name>`), `src/lodge/core/check_immutable` via check 5 (`attachments of a published decision was changed`).
Scenario: an agent wants a log beside its decision, as the guide describes.
It cannot know the decision ID before the add: a draft with an `id` minted by `lodge id d` is refused with exit 2 in both modes, so `lodge id d` mints IDs no draft can use.
A draft listing `attachments: [run.log]` without the file fails check 2.
Checkout mode works only by adding first, writing the file by hand into `lodge/attachments/<id>/`, and re-adding the still unpublished decision from `lodge draft` with `attachments:` added (run, exit 0); the guide says none of this.
Branch mode has no route: the add publishes, the file cannot reach the `lodge` branch through any command, and the re-add fails checks 2 and 5 (run, exit 1).
Branch mode is the first user's mode (LODGE-1), and attachments are her provenance rule ("where applicable for eval purposes there can be expanded evidence like logs").
Fix: a plan change, not this task's alone: `lodge add --attach PATH` (the CLI reads files it is given, as LODGE-5 allows; `gitstore` writes them to `lodge/attachments/<new decision id>/<basename>` in the same publish), or let a new decision draft carry an ID from `lodge id d` and give the store a write path for attachments; then the guide's line 44 names the route.
Until then the guide should not describe a route that does not exist; say attachments are not yet supported in branch mode.
Owner: integrator ruling (Task 5 M3 set the path, nothing set the write route).

### M1 (Minor): `lodge init` in an unwritable checkout prints a traceback and exits 1

Handle: `src/lodge/gitstore/setup.py:47-49` (bare `mkdir` and `write_bytes`), `src/lodge/main.py:55` (catches `LodgeError` only).
Run: `chmod -w` on a fresh repository, `lodge init`: `PermissionError: [Errno 13] Permission denied: '…/lodge'`, traceback through `main.py:54`, exit 1.
Every other error path I ran ended in one `lodge: …` line with exit 2 (or 1 for a check), including an unwritable `lodge/decisions` on `add`.
Fix: wrap `OSError` in `init_store` as `LodgeError(f"cannot create {path}: {error.strerror}")`, as `checkout.py` already does for writes; one test with an unwritable root.

## Practice

### M2 (Minor): the guide calls the author "her" and "she" seven times

Handle: `src/lodge/cli/guide.md:14,16,49-52`.
The guide ships in the wheel to any project's agents, and the spec's Constraints ask for documentation "written for a reader who knows neither her nor the first user"; another project's author need not be "her".
Fix: "the author", "the author's words", "the author's confirmation".

### M3 (Minor): the guide does not say what `staged` means

Handle: `src/lodge/cli/guide.md:26`.
Scenario: in checkout mode `lodge add` prints `staged d-… s-…` and leaves the files in the index; the guide never says the agent commits them with its work, nor that branch mode publishes at once.
Fix: one line after step 5: "In checkout mode `add` stages the files, so commit them with your work; in branch mode it publishes them."

### M4 (Minor): "`--reasoning` adds level 2, the why" is not what an entry shows

Handle: `src/lodge/cli/guide.md:14`.
Run: `lodge show s-jzze60 --reasoning` printed the changing decision's level-1 block, not its reasoning ("A summary loses the words she used." appeared only under `lodge show d-gwrvnt --reasoning`).
That matches the spec (an entry's reasoning is the decisions that changed it), but an agent reading the guide expects the why.
Fix: "for an entry, the decisions that changed it; show one with `--reasoning` for its why."

### M5 (Minor): the guide does not show that `replaces` and `narrows` are lists

Handle: `src/lodge/cli/guide.md:42`.
Run: `replaces: d-gwrvnt` exits 2 with `replaces must be a list`, a clear one-line error, so this costs a retry, not a wrong record.
Fix: "`replaces: [d-…]` or `narrows: [d-…]`", as line 52 does for `confirms`.

## Design

No findings beyond I1 and I2.
`parse` returning `Command | int`, the typed command dataclasses, and lazy `make_lodge`/`init` callables keep `--version`, `guide`, and `hook` free of the repository (run: all three exit 0 outside one).
Every module is under 300 lines (`parser.py` 197).

## The four focus questions

1. Guide: 54 lines, British English, no em-dashes, one sentence per line, Oxford commas where lists have three items.
   From the guide alone I wrote a correct author decision, a new entry, and a new area on the first try (`w1/`, dry run exit 0, add exit 0, gate `ok`); it covers dry run first, verbatim quotes with where and when, `lodge draft` for edits, and never editing record files.
   Where it misled me: attachments (I2), what `staged` asks of me (M3), what `--reasoning` gives on an entry (M4); it is silent on the `when` format, but an unquoted `2026-10-29 10:00` was accepted.
2. Error paths: one sentence and the right code everywhere I ran but `init` in an unwritable checkout (M1); branch mode with no remote prints git's own `fatal:` sentence after `lodge:`, which reads acceptably.
   A conflict raises `Conflict` (exit 1, `src/lodge/app/errors.py:14-17`) and prints through `main.py:56`; I did not race two clones to see it.
3. Reads: `problem:` lines come first on `search`, `show`, `spec`, `waiting`, and `check` (run with a hand-broken entry); in branch mode the freshness line `lodge@…, fetched 1 s ago` precedes them (run on `waiting` and `show`).
4. Same second: see I1; a scripted chain hits it, an interactive agent with separate tool calls should not.

## Ledger ruling (Task 10)

The ruling's items (concerns 1 to 4 and 6) stand; I saw the `:<line>` suffix and the `hook` bypass in my runs; the list-scalar test I took from its handle, not a run.
It leaves concern 5 out, so the report's "Real use is not affected" stands unruled; I1 shows it holds for interactive use only and asks for a ruling.

## Files read

Read: `.claude/agents/reviewer.md`, the brief, the report, the spec's Must nots to Reading, Storage, and Her decisions, the ledger's Task 10 lines and rulings at lines 90, 97, 103, `src/lodge/main.py`, `src/lodge/cli/{__init__,commands,output,parser}.py`, `src/lodge/cli/guide.md`, `tests/e2e/{conftest,support}.py`, `tests/e2e/test_outside_repository_one_sentence_exit_2.py`, `test_broken_agent_decision_warns_above_show.py`, `test_add_dry_run.py`, `test_add_branch_mode_publishes.py`, and excerpts of `core/derive.py`, `core/check_change.py`, `gitstore/setup.py`, `app/results.py`, `app/errors.py`.
Not read: the review package diff as a whole, the remaining e2e tests, `tests/test_wheel.py`, `pyproject.toml`, the plan's Global Constraints and Review Focus text (taken from the brief and dispatch), and `CLAUDE.md` beyond what the dispatch carried.
