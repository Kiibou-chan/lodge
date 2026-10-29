# Final whole-branch review: design, and the spec's must-nots

Reviewer: second final reviewer (design angle), at `72d31fa` on `build-0.1`, in a detached scratch worktree.
Probes ran in scratch repositories under the session scratchpad with `GIT_CONFIG_GLOBAL=/dev/null` and `GIT_CONFIG_NOSYSTEM=1`; the viewer was run on 127.0.0.1 and read with `curl`.
Not repeated: the first final review's findings (R1, G1 to G4, C1 to C3, A1, H1), and the content of the records under `lodge/`.

## Area 1, the must-nots

**Important D1. A hand edit of the author's published decision reads as hers, `current`, unflagged, in `lodge show`, `lodge search`, the viewer, and `lodge check` (`ok`); only `lodge check --gate` sees it.**
Handle: `src/lodge/app/state.py:191-204` runs only `core.check_state` on every read, although `store.trees()` at `:193` already hands it the published tree; `src/lodge/app/reads.py:69-78` runs `check_change` only for `--gate`.
Scenario, run: in a checkout-mode repository with the author decision `ITEM-1` committed on `main`, `sed -i` its statement to "Transcripts are deleted after a day." (a Bash edit, which the hook does not see, README "The hook").
`lodge show ITEM-1` prints `current · author` with the new statement above her quote "keep them whole"; `lodge check` prints `ok` and exits 0; the viewer's `/r/ITEM-1` and `/problems` (`ok`) agree; `lodge check --gate` prints `check 5: d-767yg8: statement of a published decision was changed`.
This is must-not 2 (an agent quietly rewrites her decision) shown as must-not 1 (her quote under words she did not say), and the spec's own answer to must-not 1 ("a record failing the check is shown as failing") does not hold for checks 4 to 6.
The spec says reads run checks 1, 2, 3, and 7 because 4 to 6 "need two states" (spec, The check); the store already reads both on every read, so the reason no longer holds.
Fix: in `read_state`, run `check_change(load(published), snapshot, settings, now)` as well and fold its record problems into `failing`, so the record carries `fails check` at level 1 and in the viewer; `lodge check` without `--gate` keeps its exit code but prints these as problems.
This changes the spec's sentence on which checks reads run, so it goes to the author.

**Important D2. An author decision whose entry an agent has since changed reads as plainly current, with her statement and quote, while the specification says something else.**
Handle: `src/lodge/core/derive.py:58-63` files a flagged decision only against what it replaces, narrows, or changes, so the author decision behind the entry's previous change is never "touched"; `src/lodge/core/views.py:158-188` gives such a decision no flag.
Scenario, run: author decision `ITEM-1` creates entry `s-a29fw5` ("kept whole"); a coordinator decision edits the entry to "thirty days" without `replaces` or `narrows` (the related-decision feedback asks, and is advice).
`lodge show ITEM-1`, `lodge search`, and the viewer's `/r/ITEM-1` show `ITEM-1 · current · author` with "Transcripts are kept whole." and her quote, no flag; its provenance says `changes (create): s-a29fw5 (current)`, and only opening the entry shows `awaiting the author on d-0bg4j3`.
The spec has the flag show "on the decision or entry it touched" (Review flag); a reader who searches for her decision, the common path, meets her words as the standing rule.
Fix: in `derive`, also file a flagged decision against the decision behind each entry's previous standing change when that decision is hers or confirmed by her, so `ITEM-1` carries `awaiting the author on d-0bg4j3`; a test beside `test_level1_status_who_flags`.

**Minor D3. An add that changes nothing prints `published` in checkout mode, where `add` never publishes.**
Handle: `src/lodge/app/writes.py:106-107` returns `AddOutcome.PUBLISHED` for the no-op case whatever the mode; `src/lodge/cli/output.py:51`.
Scenario, run: `lodge draft area:core > a.md; lodge add a.md` in checkout mode prints `note: nothing changed` then `published`, exit 0; every other checkout-mode add says `staged`, and the README says checkout mode stages.
An agent reading `published` takes the change as already shared.
Fix: a fourth outcome, `UNCHANGED`, printed as `nothing changed`, and the note dropped.

**Minor D4. The viewer's timeline silently stops at 50 decisions.**
Handle: `src/lodge/app/reads.py:53-57` cuts at `limit` and returns `Listed` with `more=0`; `src/lodge/app/lodge.py:26` defaults to 50; `src/lodge/viewer/pages.py:42-44` says nothing, while `search_page` (`:16-17`) says "N of M shown".
Scenario: a project with hundreds of decisions; the timeline shows 50 and reads as the whole history.
Fix: return `more` from `timeline` as `search_records` does and print "50 of 400 shown" on the page, or page the timeline.

## Area 2, a stranger's first hour

Walked: `lodge --help`, every subcommand's `--help`, `lodge guide`, the README, then `init`, `id`, `search`, `spec`, `waiting`, `check`, `show`, `draft`, `add` (dry run and real, area, entry, author and agent decisions), and the error cases below, in a fresh repository.
Most messages say what to do next (before `init`, outside a repository, a bad scope with file and line, feedback lines naming the remedy).
Text rules: no em-dash in tracked text outside a test that asserts its absence; no American spellings in user-facing text (`color` occurs only as CSS properties); no list missing an Oxford comma found by pattern; README and guide hold one sentence per line.

**Minor D5. Check messages say what is wrong but not what to do, unlike feedback.**
Handle: `src/lodge/core/check_immutable.py` (`"{name} of a published decision was changed"`), `src/lodge/core/check_state.py` (`"decided_by is author, but there is no quote"`, `"lists attachment {name}, which does not exist"`), `src/lodge/core/check_change.py` (`"{verb}, but no new decision in this change lists it with action {action}"`).
Scenario, run: `lodge draft ITEM-1`, change the statement, `lodge add --dry-run`: `check 5: d-767yg8: statement of a published decision was changed`, then `not published: the check failed`; nothing names `replaces`.
Feedback lines already end with the remedy (`src/lodge/core/feedback.py:148`), so the two kinds read differently.
Fix: append the remedy to the four commonest: check 5 "write a new decision that replaces or narrows it"; check 3 "add quote: {text, where, when} with the author's words, or record it under your own role"; check 4 "list it in the decision's changes"; the attachment check "pass the file with --attach".

**Minor D6. `lodge draft` hands out a published decision as a file "to edit and add", which check 5 always refuses except for an agent's shortened reasoning.**
Handle: `src/lodge/cli/parser.py` (the `draft` help, "print the file of a record to edit and add"), `src/lodge/app/reads.py:81-93`; README "To edit, start from `lodge draft REF`".
Scenario: as D5; a stranger follows the README's step 2 for a decision and meets check 5.
Fix: for a decision, print a first comment line or a stderr note "decisions are immutable; to change one, write a new decision with replaces or narrows", and say so in the `draft` help.

**Minor D7. The dry run prints IDs that the real add does not use.**
Handle: `src/lodge/app/writes.py` mints fresh IDs on every `add`; README step 3.
Scenario, run: `lodge add --dry-run` gave feedback on `d-9frhwf`; the following `lodge add` of the same drafts published `d-767yg8`.
An agent that writes the dry run's ID into another draft (say a `confirms`) names a record that never exists, and check 2 catches it only on that later add.
Fix: in a dry run, print new IDs as `new decision 1` or mark them `(provisional)` in each feedback line.

**Minor D8. Smaller first-hour gaps.**
`lodge spec` on an empty store prints one blank line (run), where the viewer says "Nothing is recorded yet." (`src/lodge/viewer/pages.py:39`); print the same sentence.
`lodge init` prints `created lodge/decisions and lodge/spec, staged` and stops; add "next: `lodge guide`" as `--help`'s epilogue does.
`lodge view` on a busy port says `cannot listen on port 18787: Address already in use` (run) without naming `--port`.

## Area 3, design across tasks

**Minor D9. The level-1 header is built twice, once in `core` and once in the viewer, so the README's "cannot disagree" rests on two copies.**
Handle: `src/lodge/core/views.py:149-155` (`_head`: ID and code, status, `decided_by or "no decision"`, day, scope or area) and `src/lodge/viewer/html.py:51-60` (`meta`, the same rules).
Scenario: a later change to who is shown for an entry with no decision, or to how the date is cut, lands in one and not the other.
Fix: a `core` function returning the header's parts as a tuple, used by `_head` and by `meta`, which adds only the markup.

**Minor D10. The attachment path rule `lodge/attachments/<id>/<name>` is spelt in five places.**
Handle: `src/lodge/core/check_state.py:104`, `src/lodge/core/snapshot.py:15`, `src/lodge/app/writes.py:31`, `src/lodge/gitstore/trees.py:11`, `src/lodge/viewer/pages.py:106-107`.
The Task 5 ruling M3 says this form and its users "change together"; nothing makes them.
Fix: `core.attachment_path(decision_id, name)` and `core.ATTACHMENTS`, used by all five (gitstore may keep `DATA` for the root).

**Minor D11. The viewer renders an entry's level 2 by linking IDs inside the CLI text, so each line shows the status twice.**
Handle: `src/lodge/viewer/pages.py:27-28` passes `level2` text through `paragraphs(..., known)`, and `linked` (`src/lodge/viewer/html.py:29-39`) puts the status beside each ID, before the text's own `· current`.
Scenario, run: `/r/s-a29fw5` shows `d-0bg4j3 current · current · coordinator · …`.
Fix: have `level2` of an entry return the `Level1` views (or the app pass them) and render them with `_results`, as the timeline does.

Checked and clean: the front doors and the allowed-import table in `tests/structure_tables.py` match the spec; `main.py` is the only place adapters meet; `app` reads the time only through `Clock` (`reads.py:76`, `writes.py`), entropy only through `IdSource`; the viewer takes everything from `lodge.app` and `lodge.core` and never from `gitstore`.

## Area 4, the viewer

Ran `lodge view` on 127.0.0.1 over the scratch repository and fetched each route.
Escaping holds for a statement and reasoning holding `<script>` and `<b>`, a reference `/r/%3Cscript%3Ex` (404, escaped), an area `?area=%3Cb%3E` (404, escaped), and a query `"><x` echoed into the form (escaped).
`/r/a/b`, `/r/`, `/r/ITEM-1/`, and `/style.css/` are 404; `?status=bogus` is 400 naming the allowed values; a busy port is one sentence, exit 2.
The Content-Security-Policy forbids scripts outright (`server.py:17`), so an escaping slip would still not run.
What the viewer shows and the CLI does not: the timeline (D4); what the CLI shows and the viewer does not: nothing found.
Both share D1 and D2.

## Area 5, public repository hygiene

**Important D12. Four review files on the build branch, already pushed to the public repository, carry a local scratch path with the user's account name.**
Handle: `docs/superpowers/plans/done/2026-10-29-lodge/task-4-review.md:22`, `task-9-review.md:4`, `task-9-recheck-1.md:4`, `task-9-recheck-2.md:4`, each naming a scratch path under the temporary directory.
CLAUDE.md, Hard rules: "no personal paths, machine names, … in code, tests, or docs"; merging puts them on `main`.
Fix: replace each with "the reviewer's scratch directory"; the branch history keeps them, which is the author's call (rewrite or accept).

**Important D13. On `main` already: the spec and the brainstorm record hold personal paths and another project's file paths.**
Handle: the spec's Constraints (another project's mailbox file names, and a path into the author's home directory) and the brainstorm record's paths into the author's configuration folder.
These predate the build (`git grep` at `c758046` finds them), so they are not the branch's doing, but they break the same rule; the spec is the author's text, so the edit is hers to approve.
Fix: replace the paths with plain words ("its own repository", "the author's machine-wide configuration"), and decide whether the brainstorm record, which quotes another project's numbers and file sizes, belongs in a public repository at all.

Checked and clean: `src`, `tests`, `README.md`, `scripts`, `pyproject.toml`, `.lodge.toml`, and the guide hold no `/home/`, `~/`, user or machine name, or specifics of the first user; the only project-named identifier in tests is a constant in `tests/core/derivation.py:7`, whose content is synthetic (rename to `IMPORTED` for tidiness); `lodge/` records name another project only in her quote, which is record content and not reviewed here.
`Kiibou-chan` in the README install line and the author's name in `CLAUDE.md` and the agent files are the public GitHub identity, as the commits carry it.

## Summary

0 Blocking, 4 Important (D1, D2, D12, D13), 9 Minor (D3 to D11).
D1 and D13 change what the spec says, so they go to the author; D2 follows the spec's own Review flag wording and can be fixed in the wave.

Files read: `CLAUDE.md`; the spec; the plan's Global Constraints, Process, Calls made, Review Focus, and Tasks 6 and 10 to 14; the ledger's ruling and minor lines; the first final review's headings; `README.md`; `src/lodge/cli/guide.md`; `.lodge.toml`; `src/lodge/main.py`; `src/lodge/app/{ports,lodge,reads,results,state}.py`; `src/lodge/viewer/{server,pages,html}.py`; `src/lodge/core/views.py:130-205`, `src/lodge/core/derive.py:37-75` and `:180-202`, `src/lodge/core/feedback.py:90-115`; `tests/structure_rules.py`, `tests/structure_tables.py`; the check messages by grep.
Not read in full: `src/lodge/app/writes.py`, `src/lodge/core/{apply,check_*,fields,headers,fileformat,search,words,render,drafts,yamlio,settings,snapshot,model,document}.py`, `src/lodge/gitstore/*`, `src/lodge/hook/*`, `src/lodge/cli/{parser,commands,output}.py`, the tests other than the structure files, the task briefs, reports, and reviews, and the records under `lodge/`.
