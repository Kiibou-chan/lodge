# Final whole-branch review: correctness and the git store's safety

Branch `build-0.1` at 72d31fa; probes in a detached worktree `.claude/worktrees/final-review-correctness`.
`sh scripts/check.sh` at 72d31fa: green, 1005 passed, `lodge check --gate` ok.

Read: CLAUDE.md, spec, plan (Global Constraints, Calls made, Review Focus, Task 9), ledger, `src/lodge/gitstore/*`, `src/lodge/app/{ports,state,writes,reads,lodge}.py`, `src/lodge/main.py`, `scripts/check.sh`, `src/lodge/core/{check_change,check_state,check_immutable,check_areas,check_entries,derive,headers}.py`, `src/lodge/hook/post_tool_use.py`.

## Findings

### Area 1, the git store (branch mode end to end)

Run (probe `b1`): branch-mode `init` and two `add`s in a clone with a staged change and an untracked file; the index file's hash, `HEAD`, and `git status` were identical before and after, only `refs/remotes/origin/lodge` and `.git/lodge-fetched` changed.

### Area 3, the review flag

**Important R1. `decided_by` accepts any spelling, so `Author` reads as hers at level 1 with no quote.**
Handle: `src/lodge/core/headers.py:53` (`read_str`, no rule on the value) and `src/lodge/core/derive.py:33-34` (`is_author` is `== "author"`).
Scenario (run, probe `b1`): a decision with `decided_by: Author` and no `quote` is accepted; `lodge show` prints `d-0p554n · current · Author · 2026-10-29 · product`, and the entry it edited prints `· Author ·` as who last decided.
It is treated as an agent role (flagged here only because it edited her entry), so a new entry under `decided_by: Author`, `the author`, or `author (relayed)` is unflagged, unquoted, and reads as hers: must-not 1, and it defeats LODGE-2's safeguard (the quote at level 1 is what makes a wrong attribution visible).
Fix: refuse in `headers.py` a `decided_by` that is not `author` and whose casefolded, stripped form contains `author` (or restrict roles to `[a-z][a-z0-9-]*` and refuse `author`-lookalikes), with a test; one sentence in the guide.

### Area 1, the git store (continued)

**Important G1. A `lodge add` ended by SIGTERM leaves `lodge.lock`, and in branch mode every read then fails for ten minutes and after that until someone deletes the file.**
Handle: `src/lodge/gitstore/lock.py:34-39` (release only in `finally`), `src/lodge/main.py:83-92` (no SIGTERM or SIGHUP handler, so Python's default action skips `finally`), `src/lodge/gitstore/branch.py:39-42` (a read that needs a fetch takes the lock and does not fall back to the cache).
Scenario (run, probe `b1`): a `pre-push` hook sleeping 5 s, `lodge add` sent SIGTERM at 3 s, exit 143, `.git/lodge.lock` stays; the push itself still landed (git's child outlives lodge, and git's own push updated `refs/remotes/origin/lodge`).
With the fetch stamp older than `max_staleness_seconds`, `lodge search logs` then took 30.2 s and exited 2 with "another lodge is working in this repository", which is false; after ten minutes the message becomes "delete it", for reads too.
A Claude Code Bash timeout or a cloud session being stopped sends exactly this signal, and a push through the session proxy is the slow step held under the lock.
Fix: in `main`, turn SIGTERM and SIGHUP into `SystemExit` (`signal.signal(SIGTERM, lambda *_: sys.exit(143))`) so the `finally` runs; in `BranchStore.trees`, when the lock cannot be had within the wait, serve the cached ref with freshness "not fetched: another lodge holds <path>" instead of failing (the plan's offline rule, "a failed fetch serves the cached state"); optionally write host and PID in the lock and call a lock whose PID is gone on this host left over.
In checkout mode the same kill between `mkstemp` and `os.replace` leaves a `.<name>.<random>.lodge-tmp` file under `lodge/` (`checkout.py:170-186`), which `load` reports as a stray file, so every later add fails check 1 until someone deletes it; the signal handler covers that too.
The plan's "reported as stale rather than broken" ruling stands; this fix only makes the normal kill path release it and keeps reads answering.

**Minor G2. `update-ref` after a push has no old value, so it can rewind the remote-tracking ref past a newer fetch.**
Handle: `src/lodge/gitstore/branch.py:74`.
Scenario (reasoned, not run): between lodge's push and its `update-ref`, the user's own `git fetch` (not under lodge's lock) moves `refs/remotes/origin/lodge` to a later commit; lodge then sets it back to its own commit, and reads show the older state, labelled "fetched n s ago", until the next fetch.
Fix: `update-ref <ref> <commit> <tip>` and ignore its failure, since a failure means the ref already moved forward.

**Minor G3. A push whose report is lost and that another clone builds on before `ls-remote` is read as a lost race, and the retry publishes the decision a second time under a new ID.**
Handle: `src/lodge/gitstore/plumbing.py:78-81` (`tip != parent` returns False without asking whether `commit` is an ancestor of `tip`) and `src/lodge/app/writes.py:83-84` (fresh IDs on every attempt, ruled for the normal case).
Scenario (reasoned, not run; the window is a dropped connection after the remote updated its ref): attempt 1's commit C lands, the client sees an error, clone B pushes C' on C, `ls-remote` returns C', `push` returns False, `add` re-fetches and re-applies a decision-only draft with a fresh ID on C', so two decisions say the same thing.
Fix: when `tip` is neither `commit` nor `parent`, fetch and return True if `git merge-base --is-ancestor <commit> <tip>` holds.

### Area 2, the check and `lodge check --gate`

**Important C1. In checkout mode the gate checks the working tree, not what is committed, so a partial commit publishes a state that fails check 4 while the gate says `ok`.**
Handle: `src/lodge/app/reads.py:69-78` (`check_change(load(state.published), state.snapshot, …)`, where `state.snapshot` is `disk_tree`, `src/lodge/gitstore/checkout.py:30-34`); `scripts/check.sh:8`.
Scenario (run, probe `c1`): on a work branch, `lodge add` of an area, an entry, and its decision (staged), then `git commit -- lodge/spec` (CLAUDE.md asks for commits "with explicit paths", so leaving one out is the likely slip); `lodge check --gate` prints `ok`, exit 0; with the uncommitted decision set aside, the committed tree gives `check 4: s-4wpa9n: created, but no new decision in this change lists it with action create`, exit 1.
Once that commit reaches `main`, the problem is "already published" and becomes a note for ever, so the gate never catches it again.
The spec's "the state about to be published" is the commit that goes out, not the files on disk.
Fix: in checkout mode give the gate `HEAD`'s tree as the state to check (it is what a push or merge publishes), and fail, or at least print a problem, when the working tree's `lodge/` differs from `HEAD`'s ("uncommitted record changes: commit them or the gate is not checking what you publish"); keep reads on the working tree.

**Important C2. When the base branch cannot be found, checkout mode's published state is empty, so the gate passes an edited published decision without a word.**
Handle: `src/lodge/gitstore/checkout.py:57-67` (empty tree when neither `<remote>/<base>` nor `<base>` resolves, or `merge-base` fails, as in a shallow clone); `src/lodge/gitstore/checkout.py:36-37` (`freshness` is None, so no line says so).
Scenario (run, probe `c1`): records pushed to `main`, a branch hand-edits a published decision's title; with `origin/main` present the gate reports `check 5: d-wqyjkv: title of a published decision was changed`, exit 1; after removing `refs/remotes/origin/main` and `main` (as in a single-branch clone, a `--depth 1` clone where the merge base is missing, or any project whose trunk is `master` without `base` set), the same tree gives `ok`, exit 0.
That is must-not 2 passing the gate, and a default (`base = "main"`) is enough to reach it.
Fix: distinguish "no history" (unborn `HEAD`, or no commit holds `lodge/`) from "base not found"; in the second case make `check --gate` exit 2 with one sentence naming the refs it tried, and have `freshness` (or a note) say what the published state is.

**Important G4. Branch mode accepts a rewritten `lodge` branch without a word: the forced fetch replaces the history, and her decision's new text shows as hers with the gate `ok`.**
Handle: `src/lodge/gitstore/branch.py:94-103` (`+refs/heads/<branch>:…`, the old tip neither kept nor compared); `src/lodge/app/reads.py:76-77` with `branch.py:43-48` (published and current are the same tree, so check 5 has nothing to compare).
Scenario (run, probe `b1`): a second clone checks out `lodge`, changes the statement of the author decision `d-4tyrfq`, amends the last commit, and `git push --force`; in the first clone, the next read fetches and `lodge show d-4tyrfq` prints `current · author` with the new statement "Transcripts are deleted at once." under her quote "keep them"; `lodge check --gate` prints `ok`, exit 0.
This is must-not 2 ("quietly rewrite a decision she made") and must-not 1 at once; an agent that "cleans up" the branch with a rebase reaches it without meaning to.
lodge holds the old tip at the moment it fetches, so it is the one place that can see the rewrite.
Fix: in `_fetch`, read the tracking ref before fetching; when the new tip does not contain the old one (`merge-base --is-ancestor old new` fails), keep the old tip under `refs/lodge/rewritten/<time>`, run `check_change(load(old), load(new), …)` in the app on the next read (the Store port can expose the previous tip as the published tree), and print its problems with a line "the branch was rewritten since the last fetch"; at least say it in `freshness`.

**Minor C3. In branch mode `lodge check --gate` compares the branch with itself, so it can never fail checks 4 to 6, and nothing says so.**
Handle: `src/lodge/gitstore/branch.py:48` (`return tree, tree`), `src/lodge/app/reads.py:76-77`.
Scenario (reasoned from the code, consistent with the G4 run): the spec has the gate "before every push to `lodge`"; in branch mode that gate is `lodge add`'s own `check_change`, and a hand `git push` to `lodge` is not gated by anything.
Fix: in branch mode `check --gate` prints a note that the gate runs inside `lodge add`, and the guide says pushing to the branch by hand skips it; G4's fix gives `--gate` a real published state after a rewrite.

### Area 4, `lodge add` end to end

Read `src/lodge/app/writes.py` and the CLI's `_add` and `_read_attachments` (`src/lodge/cli/commands.py:78-117`); no defect found beyond G3.
The date wait (`writes.py:141-154`) is recomputed on every retry, so a retry after a rejected push re-dates on the fetched tree; attachments are placed only under the one new decision's ID, refused unless listed exactly, and never overwrite (`plumbing.py:24-25`); a dry run returns before `publish`.
Minor A1: an add whose drafts change nothing reports `PUBLISHED` with "nothing changed" in checkout mode too (`writes.py:105-107`), where the outcome of a real write would be `STAGED`; harmless, wording only.

### Area 5, the hook

**Minor H1. The frozen-file text tells the agent to reverse an edit even when the author asked for it in this session.**
Handle: `src/lodge/hook/post_tool_use.py:14-19, 26-31`.
Scenario (reasoned): she asks a session to fix a typo in a frozen `verdicts.md`; the hook's additionalContext says "Reverse your own edit now", and an agent that obeys discards the change she asked for.
The record-file text is safe (records are written only through `lodge add`, and her hand edit would be the thing to reverse), and the reversal advice itself never touches her uncommitted work: Edit and MultiEdit reverse only the agent's replacement, and Write requires a prior Read, so the agent holds the old text.
Fix: in `FROZEN_TEXT`, "If the author asked for this edit, tell her the file is frozen and ask before reversing it."

## Summary

0 Blocking, 5 Important (R1, G1, C1, C2, G4), 5 Minor (G2, G3, C3, A1, H1).
No ledger ruling is reopened; G1 keeps the plan's "reported, not broken" lock rule and only adds release on SIGTERM and a read fallback.
Branch mode never touched the index, the working tree, or `HEAD` in the probes; every write path is confined to `lodge/` by `check_writes` and, in checkout mode, `_refuse_links` under the lock; the review flag in `derive.py` matches the spec, LODGE-6, and LODGE-7 on every path traced (agent edits after a flagged agent edit, replacement of a flagged decision, confirmation of an earlier agent decision, imported decisions).

Not read: `src/lodge/core/{apply,drafts,feedback,views,search,render,snapshot,fileformat,document,words,yamlio,model,settings,ids}.py` beyond the lines quoted, `src/lodge/viewer/*` beyond `serve`, `src/lodge/cli/{parser,output}.py`, and the tests.
Probe worktree `.claude/worktrees/final-review-correctness` removed; probe repositories under the scratchpad `probes/` folder.
