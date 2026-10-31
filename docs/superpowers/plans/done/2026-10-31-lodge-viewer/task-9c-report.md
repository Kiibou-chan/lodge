# Task 9c report

DONE_WITH_CONCERNS.
Arrangement and Security are recorded through `lodge add`, with no code changes, commit, push, or real-index staging.
No author records or messages were added, and no author decision was narrowed.
Task 9b's corrections of s-dm37qr and s-582qav are retained without repeating their text edits.
The final dependency-warning count is 0, and the builder gate is green.

## Records and files

| New entry | Decision | Design lines | Claim and dependencies |
| --- | --- | --- | --- |
| s-eb9kn7 | d-7n4jyj | 118 | Optional area ranks, name ties, unranked areas last, and shared-rank feedback; independent. |
| s-2bzwzv | d-7n4jyj | 118-121 | Written and dependency views, initial dependency view, indentation, extra dependency lines, and stored order retained for check 7; rests on s-v022r0 and s-m4esa0. |
| s-rh08jw | d-7n4jyj | 122 | Entry-page dependency trees to roots and one level of dependants; rests on s-m4esa0. |
| s-q42qd7 | d-h3v99q | 128 | POST writes with a startup token and constant-time comparison; independent. |
| s-704ssg | d-h3v99q | 129 | Whole-header allowed hosts and explicit proxy ports, without machine names in code or committed settings; independent. |
| s-rpn77e | d-h3v99q | 128,130 | Required allowed HTTP or HTTPS Origin; rests on s-704ssg. |
| s-bet2rj | d-h3v99q | 131 | Only confirmations and threads, with no existing decision, entry, or area edits; rests on s-bhew59 and s-yj4r17. |
| s-nnp7y3 | d-h3v99q | 132 | Reachability grants the existing author-label trust, requiring configured names; rests on s-704ssg. |

The eight entry files are under `lodge/spec/` in the areas in the table's claims: model for the rank field, reading for views, trees, hosts, and viewer writes, writing for token and Origin checks, and purpose for the trust boundary.
Each is below 150 words.
The two new decision files are `lodge/decisions/d-7n4jyj-read-ranked-areas-and-dependency-arrangements.md` and `lodge/decisions/d-h3v99q-restrict-viewer-writes-to-trusted-requests.md`.
Both are coordinator product decisions, identify coordinator calls, and name d-7w5aq0 for advisor claims.
Arrangement names d-a3h9f3 and records its rule verbatim: "dependants follow what they rest on, siblings in the area's order".
It names d-g7xvwm and d-s64jyh as author authority without presenting agent prose as her words.
Security records the writable viewer's trust-boundary reason and the browser Origin reason.

| Edited entry | Decision | Sentence changed |
| --- | --- | --- |
| s-v022r0 | d-7n4jyj | Replace the first sentence with: The readable specification is rendered from the entries with each entry's ID, areas by rank and then name, unranked areas last, and entries after what they rest on within their area. |
| s-nzhyh3 | d-h3v99q | In the adapter sentence, replace `the read-only web viewer` with `the web viewer that writes author confirmations and threads only`. |

The remaining sentences of both entries are unchanged.
`lodge add` updates the model, purpose, reading, and writing `_area.md` files to insert the new entries in their stored orders.
No existing area title, intro, or rank is changed.
The brief's other two Security edits, s-dm37qr and s-582qav, were already done in 9b and still hold.

## Reaffirmations, feedback, and narrowings

After Arrangement, s-dm37qr was the sole entry marked with an actual dependency warning.
The next section decision, d-h3v99q, lists it with `edit`, unchanged, and explains that ranked dependency rendering changes its displayed order rather than its local operation, write scope, or read features.
That decision also reaffirms its dependant s-582qav unchanged: other edits still belong to sessions.
It reaffirms s-bty9z4 unchanged after the s-nzhyh3 correction: the Store still owns commits and branch-mode publication.
All three have their own reasoning lines and lodge-generated edit drafts.
This includes the downstream entries in the same decision to avoid another warning cascade.

No decisions were narrowed.
The current statements of d-c08bdw and d-fkndvh remain true: rendering stays on demand, and layering and adapter responsibilities remain intact.
Their related entry wording is corrected without narrowing a statement that still holds.
Arrangement feedback on d-c08bdw, d-qbfdqt, and d-4dp4gm is answered no, with reasons in the decision: on-demand rendering, read checks, and the stored-order check survive.
Security feedback on d-m4ky49, d-6zyet3, and d-ejdyds is answered no: reconciliation, eight checks, and reading-area dependency links survive.
Numeric feedback on the design-line references was resolved with explicit source-line handles before the final dry run.
Area-order notes are expected insertions.
No dry run emitted a check line.

All drafts, preparation scripts, dry runs, add outputs, and specification snapshots are under `.drafts/task9c/`.
Record reads and draft extraction used lodge only.
The sandbox recipe was initialised once by copying the real index to `.drafts/index` and creating `.drafts/objects`.
Both real adds used `GIT_INDEX_FILE`, `GIT_OBJECT_DIRECTORY`, and `GIT_ALTERNATE_OBJECT_DIRECTORIES` exactly as specified, through `uv run --frozen --quiet lodge add`.
Each add was preceded by a successful matching dry run.
The add outputs' `staged` refers to the alternate index.

## Verification

No tests were added because this task changes records only.

| Command | Result |
| --- | --- |
| `uv run --frozen --quiet lodge waiting` | Both groups empty. |
| `uv run --frozen --quiet lodge id s`, once per new entry | Eight IDs, listed above. |
| `uv run --frozen --quiet lodge draft REF` | Five existing-entry drafts, retaining their base values. |
| Arrangement dry run and sandbox add | Successful; d-7n4jyj and four entries staged in the alternate index. |
| Security dry run and sandbox add | Successful; d-h3v99q and nine entries staged in the alternate index. |
| `uv run --frozen --quiet lodge check` | `ok`. |
| `uv run --frozen --quiet lodge spec --area reading` | Names the viewer's confirmation and thread writes, plus the new write limits and arrangement claims. |
| `uv run --frozen --quiet lodge spec` after each section | Snapshots `spec-after-arrangement.txt` and `spec-final.txt`. |
| `uv run --frozen --quiet lodge spec` followed by `grep -c ', changed since)'` | Final count `0`; grep exit 1 is expected for no matches. |
| `uv run pytest tests/e2e/test_view.py -q -k test_view_passes_the_port_to_the_viewer` | `1 passed, 6 deselected in 0.30s`. |
| `uv run ruff format --check` | `507 files already formatted`. |
| `uv run ruff check` | `All checks passed!`. |
| `uv run mypy` | `Success: no issues found in 194 source files`. |
| `uv run vulture` | Exit 0, no output. |
| `uv run pytest -q --ignore=tests/viewer/test_server.py --ignore=tests/e2e/test_view.py` | `1366 passed, 1 skipped in 45.48s`. |
| `uv run lodge check --gate` | `ok`, with expected area-order and uncommitted-record notes. |
| `git diff --check` | Exit 0. |

Warning counts are **0 before, 1 after Arrangement, 0 after Security**.
Use the actual warning suffix `, changed since)` when counting: existing entries s-7wbv0e and s-kba448 mention the words in explanatory prose, which is not a warning.
No remaining dependency mark is waived.

The socket-bound `tests/viewer/test_server.py` and server-starting cases in `tests/e2e/test_view.py` remain for the coordinator's outside-sandbox gate, as the brief requires.
The installed-wheel test was the single network-related skip.
A focused diagnostic run, `uv run pytest tests/test_wheel.py -q -rs`, reported `1 skipped in 10.66s`: `uv pip install` could not fetch PyYAML from PyPI because DNS resolution was unavailable.
This is a sandbox verification limit, alongside the deliberately excluded socket tests.
There is no blocking concern or unresolved design conflict.
The specific report path requested by the user takes precedence over the generic shared-report path in the brief.

## Complete design coverage, lines 21 to 141

This map includes the records from 9a and 9b without adding them again.
Blank lines and headings are explicitly omitted as non-claims.
Historical counts and one-off rollout instructions are not turned into permanent product requirements.
The advisor's sibling-order clarification d-a3h9f3 applies to line 118, and d-na1eg7's same-change exception applies to line 106, as already implemented in 9b.

| Design line or lines | Entry, or omission and reason |
| --- | --- |
| 21-22 | Left out as timeless entries: historical motivation and the then-current entry count; retained as motivation in d-3d4g9j. |
| 23-25 | Left out: blank lines and Goals heading. |
| 26 | s-648y95. |
| 27 | s-rbt13j. |
| 28 | s-bdkjte. |
| 29 | s-sm2mf7. |
| 30-32 | Left out: blank lines and Non-goals heading. |
| 33 | s-z2nb2t. |
| 34-36 | s-c8hrye; the live-agent security cost is reasoning in d-3d4g9j. |
| 37 | s-bxqj2f. |
| 38 | s-9xwya5. |
| 39-41 | Left out: blank lines and Must nots heading. |
| 42 | s-12ta2e and the existing purpose safeguards; introductory continuity with the first design adds no separate new rule. |
| 43 | Left out: blank line. |
| 44 | s-12ta2e, s-bhew59, and s-s4mkaj. |
| 45 | s-ycx03c. |
| 46 | s-1cgvhe. |
| 47-49 | Left out: blank lines and Confirming heading. |
| 50 | s-arr325. |
| 51 | s-cecwv7. |
| 52 | s-hvsamx. |
| 53-54 | s-arr325. |
| 55 | Left out: blank line. |
| 56 | s-bhew59 and s-pbt1wj. |
| 57 | Left out: blank line. |
| 58-59 | s-bhew59. |
| 60 | s-bhew59 and s-s4mkaj. |
| 61 | s-s4mkaj. |
| 62 | Left out: blank line. |
| 63 | s-pbt1wj. |
| 64 | s-gxjwd9. |
| 65-68 | s-fwas5n; staging and worktree costs are reasoning in d-s69cq4. |
| 69-70 | s-mc9n8a. |
| 71-72 | s-bty9z4. |
| 73 | s-j9jc4y. |
| 74-76 | Left out: blank lines and Doubts and questions heading. |
| 77 | s-yj4r17, s-a67fqm, and s-evv024. |
| 78-79 | s-yj4r17. |
| 80 | s-yj4r17 and s-ms14fq. |
| 81 | s-77krr7. |
| 82 | Left out: blank line. |
| 83 | s-ejjpek. |
| 84 | s-ejjpek and s-4wna3s. |
| 85 | s-4wna3s, following d-a3h9f3's empty closing text and writer attribution. |
| 86-87 | s-77krr7. |
| 88-89 | s-nda0br and s-0s9m2d. |
| 90 | s-ejjpek. |
| 91 | Left out: blank line. |
| 92-94 | s-r7c3wn and s-wcv4en. |
| 95 | Left out: blank line. |
| 96-98 | s-nxakwv. |
| 99 | Left out: blank line. |
| 100 | s-3e6zp3 and s-ms14fq. |
| 101-103 | Left out: blank lines and Rests on heading. |
| 104-105 | s-m4esa0 and s-8f6scf. |
| 106 | s-7wbv0e and s-0yzshh, including d-na1eg7's same-change edit or create exception. |
| 107 | s-7wbv0e and s-01k42c. |
| 108 | s-wvza5q, s-j70a0k, and s-edgt71. |
| 109 | s-wvza5q and s-aw5a1j. |
| 110 | s-63mwy2. |
| 111 | Left out: blank line. |
| 112 | s-kba448 and s-wcv4en. |
| 113 | s-sjqg5k; followed by the reaffirmations in all three parts. |
| 114 | s-kba448. |
| 115-117 | Left out: blank lines and Arrangement heading. |
| 118 | s-eb9kn7, s-v022r0, and s-2bzwzv, with d-a3h9f3's sibling-order clarification. |
| 119-121 | s-2bzwzv. |
| 122 | s-rh08jw. |
| 123-125 | Left out: blank lines and Security heading. |
| 126 | Left out as a separate entry: security motivation, recorded in d-h3v99q's reasoning. |
| 127 | Left out: blank line. |
| 128 | s-q42qd7 and s-rpn77e. |
| 129 | s-704ssg. |
| 130 | s-rpn77e, with the browser reason in d-h3v99q. |
| 131 | s-bet2rj and s-nzhyh3; s-dm37qr and s-582qav already corrected in 9b. |
| 132 | s-nnp7y3. |
| 133-135 | Left out: blank lines and Process consequences heading. |
| 136 | Left out: rollout introduction, not a lasting product claim. |
| 137 | Left out: blank line. |
| 138 | s-c8hrye and s-nda0br; the instruction to update the guide and project instructions is a build-process step, not another product entry. |
| 139 | s-m4esa0 gives the lasting dependency rule; the historical count and per-area migration procedure are left out as rollout instructions, with migration already recorded by per-area decisions such as d-ejdyds and d-en18e8. |
| 140 | s-bet2rj, s-dm37qr, s-582qav, and s-nzhyh3 hold the lasting viewer limits; transferring this design into lodge is this task's rollout work, not a separate product claim. |
| 141 | s-dm37qr, s-582qav, s-nzhyh3, s-j5ttw1, s-a67fqm, s-evv024, s-0yzshh, s-01k42c, s-j70a0k, s-edgt71, and s-0s9m2d, all corrected across 9a, 9b, and 9c; the historical inventory itself is left out as a separate entry. |
