# Task 9b report

Step 1: DONE.
Step 2: DONE_WITH_CONCERNS.
Coordinator ruling d-na1eg7 is implemented, and Task 9b records are added in the working tree through the sandbox index and object recipe.
The final dependency-warning count is 0, and `lodge check --gate` prints `ok`.
No real-index staging, commit, or push ran.

## Code change and failing tests

`src/lodge/core/check_entries.py` now exempts a link from its whole-entry comparison only when another new decision of this change lists the same entry with `edit` or `create`.
A published decision, a decision about another entry, or a link alone cannot supply that exemption.
The existing checks still require the appropriate create or edit action for the entry itself.
The rejection text now tells the writer to list the entry with edit or create in another decision of this change.
`src/lodge/cli/guide.md` states the same exception within its existing link-action sentence, retaining the 60-line limit.

`tests/core/test_check_links.py` adds two parametrised tests:

- `test_link_with_another_decision_accounting_for_text_passes`: a changed existing entry with a separate edit decision, and a new entry with a separate create decision.
- `test_link_without_another_decision_accounting_for_text_fails`: statement and title changes with only a link on that entry, plus an edit decision about a different entry; both must retain check 4 and the explanatory diagnostic.

Both tests were written and run before the implementation.
The first run reported `4 failed, 11 passed`; both acceptance cases failed, and both rejection cases failed on the newly specified diagnostic, since refusal already worked.
The create fixture initially also exposed an unrelated missing area-order failure; its area order was corrected and both tests were rerun against the original implementation before restoring the fix.
That captured baseline, including existing diagnostic assertions updated for the new wording, reports `6 failed, 9 passed` in `.drafts/task9b/code-first-failure.txt`.
After the implementation the focused file reports `15 passed`.
Existing assertions changed only to match the revised error text.

The first full gate caught the guide growing to 61 lines, with `2 failed, 1365 passed`.
The additional sentence was folded into the existing action sentence; no guide test was relaxed.
Ruff also caught an overlong diagnostic literal and import order, and mypy caught the dynamic replacement dictionary in the new test; these were corrected before the final gate.

## Records added

Three coordinator product decisions were added:

- d-68b0j2, Doubts and questions on decisions and entries.
- d-6zyet3, Entry dependencies and eight publication checks.
- d-m4ky49, Reconcile dependencies after threads and entry links.

The first two carry the design sections' claims, advisor attribution to d-7w5aq0, and the coordinator's calls.
The thread reasoning names d-a3h9f3 for empty closing messages and the s-7ah5n7 exception, and d-9dqycj for the author's entry-focused words.
The dependency reasoning names d-na1eg7 for the same-change link exception.
The final decision corrects an obsolete viewer claim and reaffirms affected entries and their dependants.

| New entry | Decision | Design lines | Claim |
| --- | --- | --- | --- |
| s-m4esa0 | d-6zyet3 | 104-105 | Entries store the dependencies they require |
| s-7wbv0e | d-6zyet3 | 106-107 | Link changes preserve freshness and review state |
| s-wvza5q | d-6zyet3 | 108-109 | Dependency checks reject invalid targets and cycles |
| s-63mwy2 | d-6zyet3 | 110 | Mentioned entries prompt dependency feedback |
| s-kba448 | d-6zyet3 | 112,114 | Reads show dependency risks and reverse links |
| s-sjqg5k | d-6zyet3 | 113 | Reaffirm an entry after its dependency changes |
| s-yj4r17 | d-68b0j2 | 76-81 | Threads record doubts and questions |
| s-ejjpek | d-68b0j2 | 83-84,90 | Open and read threads on a record |
| s-4wna3s | d-68b0j2 | 84-85 | Thread commands append replies and closing messages |
| s-77krr7 | d-68b0j2 | 81,86-87 | Author messages retain verbatim words and provenance |
| s-nda0br | d-68b0j2 | 88-89 | Waiting separates agent and author work |
| s-r7c3wn | d-68b0j2 | 92-94 | Doubts propagate while questions mark their record |
| s-nxakwv | d-68b0j2 | 96-98 | Acting on a thread requires a decision |
| s-3e6zp3 | d-68b0j2 | 100 | Open threads do not fail the gate |

## Statement edits

All edits were submitted as drafts through `lodge add`.
No record file was opened or edited directly.

| Entry | Decision | Sentence change |
| --- | --- | --- |
| s-a67fqm | d-68b0j2 | Replace two kinds with three: specification entries, decisions, and threads. |
| s-evv024 | d-68b0j2 | Add: Threads live under `lodge/threads/`, with the ID prefix `q-`. |
| s-0s9m2d | d-68b0j2 | Add the two waiting groups, distinguished by the last message's writer. |
| s-ms14fq | d-68b0j2 | Add check 5's published-thread message, target, kind, and closure restrictions. |
| s-wcv4en | d-68b0j2 | Add doubt, question, and dependency marks to Level 1 alongside the review flag. |
| s-7ah5n7 | d-68b0j2 | Insert after the first sentence: A thread, a doubt or question on a decision or entry with its messages, is not such a kind: it holds no claim of its own, and what it settles enters lodge as a decision. |
| s-0yzshh | d-6zyet3 | Add `link` to the actions, and say other alterations require another decision in the change listing edit or create. |
| s-01k42c | d-6zyet3 | Add: A `link` change raises no review flag. |
| s-j70a0k | d-6zyet3 | Replace seven with eight and add a cycle of `rests_on` links to the check list. |
| s-edgt71 | d-6zyet3 | Reads run all eight checks; check 5 includes an altered thread. |
| s-8f6scf | d-6zyet3 | Decision links stay on the decision; `rests_on` is stored on the entry and reverse links are derived. |
| s-aw5a1j | d-6zyet3 | Add: Check 6 also refuses an entry edited in this change that newly rests on a retired entry. |
| s-dm37qr | d-6zyet3 | Replace the read-only sentence with: The viewer is local and started from the command line; a separate sentence says it writes author confirmations and threads. |
| s-582qav | d-m4ky49 | Replace both obsolete read-only and later-editing sentences with: The viewer writes author confirmations and threads, as s-dm37qr states; other decisions and entry edits reach lodge through a session. |

The titles of s-dm37qr and s-582qav were updated to describe the viewer's confirmation and thread writes.
The s-7ah5n7 statement otherwise stays unchanged.

## Narrowings and feedback

Only d-6zyet3 narrows decisions:

- d-zerbz9: its claim that links are stored on decisions only is false once entries store `rests_on`; identifier and derived reverse-link rules remain valid.
- d-3epcjd: its seven-check claim becomes eight; the existing checks remain valid.
- d-4032xv: reads run eight checks, while its published-state comparison and refusal rules remain valid.

No author decision was narrowed.
The thread add's related-decision prompts for d-a16d4m, d-96n7j6, and d-a3e8kb are answered no: dependency migration and Markdown storage remain valid.
The reconciliation prompts for d-6zyet3, d-68b0j2, and d-76nt3b are answered no: the section rules and Store-port checks remain valid.
The numeric prompts were resolved before adding with explicit handles to the design's named sections.
Area-order notes are expected insertions.
No resumed dry run emitted a check line.

## Changed since reconciliation

Count actual warning suffixes with `lodge spec | grep -c ', changed since)'`, rather than explanatory prose.
The snapshots are `.drafts/task9b/spec-after-threads.txt`, `spec-after-rests.txt`, and `spec-final.txt`.
The count started at 0, then four entries were marked after d-68b0j2.
The next section, d-6zyet3, lists all four with edit: s-fehz74, s-dm37qr, s-j9jc4y, and s-hfjr1m.
Length guidance, confirmation attribution, and advisory feedback retain their text with an individual reason; the viewer's obsolete read-only sentence is corrected.
After d-6zyet3, fifteen entries were marked.
The follow-up includes all fifteen and their transitive dependants, avoiding another cascade of warnings.
Each entry has its own reason in d-m4ky49; only s-582qav changes text in that decision.
The 22 entries are:

- s-0s9m2d: The review flag and the two waiting groups remain valid; links are exempt from raising that flag.
- s-3e6zp3: Open threads still do not fail the gate because reaffirming check immutability does not introduce an open-thread prohibition.
- s-582qav: The earlier read-only and later-editing sentences no longer hold; confirming and threads are now the viewer writes, while other edits stay in sessions.
- s-bhew59: A confirmation remains a separate author decision; link support does not alter its identity.
- s-dfejrb: Flagged changes still take effect immediately; the link exemption does not delay them.
- s-dm37qr: The corrected local viewer claim still holds after the waiting and level-mark reaffirmations; its writes remain confirmations and threads.
- s-fmwe04: Decision status still derives from replacement and narrowing, independent of entry links.
- s-g2jwha: Identifier resolution and uniqueness still apply with eight checks.
- s-hfjr1m: Feedback remains advisory after the waiting-list reaffirmation; checks still alone refuse publication.
- s-j9jc4y: Writer and confirmation labels remain visible after reaffirming the level-mark rules.
- s-kvwrqw: Entry changes still need a same-change decision, including the ruled link exception.
- s-ms14fq: Decision and thread immutability still apply with eight checks.
- s-nda0br: The two waiting groups still follow the last message writer after the review-flag reaffirmation.
- s-nxakwv: Thread responses still require decisions and replies; links raising no flag does not exempt other changes.
- s-pbt1wj: Confirmations continue to use the shared add path now running all eight checks.
- s-q10vh5: Entry status still derives from retirement decisions; the link action does not retire an entry.
- s-qzk2yb: Header parse and required-field checks remain necessary with eight checks.
- s-s27z33: Area ordering still applies with eight checks.
- s-s4mkaj: Generated confirmation titles and statements remain lodge text after reaffirming the separate author-decision rule.
- s-x84e3h: Import exemptions and provenance remain as written after reaffirming the author-quote and entry-change checks.
- s-yhppm5: Author attribution still requires verbatim provenance with eight checks.
- s-yrz8fz: The length values remain open for pilot tuning after the level-mark extension.

The final warning count is 0.
As expected, grep returns exit 1 when it prints 0 matches.

## Commands and verification

Every add was preceded by its matching dry run.
Logs are `.drafts/task9b/threads-resume-dry.txt`, `threads-add.txt`, `rests-dry.txt`, `rests-add.txt`, `refresh-dry.txt`, and `refresh-add.txt`.
The earlier blocked attempt remains historical evidence in `threads-dry.txt`; it was not reused as an add result.
The sandbox index was copied once, and all three real adds used `GIT_INDEX_FILE`, `GIT_OBJECT_DIRECTORY`, and `GIT_ALTERNATE_OBJECT_DIRECTORIES` exactly as in the Global Constraints.
The word `staged` in add output refers to that alternate index, not the real index.

Final builder gate:

- `uv run ruff format --check`: 497 files already formatted.
- `uv run ruff check`: all checks passed.
- `uv run mypy`: no issues found in 194 source files.
- `uv run vulture`: exit 0.
- `uv run pytest -q --ignore=tests/viewer/test_server.py --ignore=tests/e2e/test_view.py`: `1367 passed in 35.92s`.
- `uv run lodge check --gate`: `ok`, with expected area-order and uncommitted-record notes.
- `uv run pytest tests/e2e/test_view.py -q -k test_view_passes_the_port_to_the_viewer`: `1 passed, 6 deselected`.
- `uv run --frozen --quiet lodge check`: `ok`.
- `uv run --frozen --quiet lodge spec | grep -c ', changed since)'`: `0`.

The socket-bound `tests/viewer/test_server.py` and server-starting cases in `tests/e2e/test_view.py` remain for the coordinator's outside-sandbox gate.

## Concern and Task 9c handoff

The required changed-since pass found that s-dm37qr and s-582qav no longer held.
They were corrected now rather than reaffirmed as read-only, bringing two viewer edits forward from Task 9c under the brief's explicit rule for false claims.
Task 9c should start from their current drafts and still handle s-nzhyh3, Arrangement, Security reasoning, and the final design-line coverage map.
The coordinator still needs to stage explicit paths and run the full outside-sandbox gate before any commit.
