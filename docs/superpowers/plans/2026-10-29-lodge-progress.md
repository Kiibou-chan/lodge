# Ledger: lodge 0.1, plan docs/superpowers/plans/2026-10-29-lodge.md

Spec: `docs/superpowers/specs/2026-10-29-lodge-design.md` (approved 2026-10-29 14:26; LODGE-1 to LODGE-5 answered).
Plan: reviewed from two angles, fixed, rechecked twice; plan and process approved by the author 2026-10-29 14:57 ("Approved, build").
Branch `build-0.1` from `main` c758046, worktree `.claude/worktrees/build-0.1`.
Briefs, reports, and reviews: `docs/superpowers/plans/2026-10-29-lodge/`; review packages are scratch, not committed.

## Preflight scan

| Rows | Produces / consumes | Found |
|---|---|---|
| T1-all | `tests/structure_rules.py`: core allow-list (`json`, `hashlib`, `tomllib`, `yaml`, …), front doors across packages, direct submodule imports inside a package, Ruff TID252 bans relative imports | agree: inside a package, modules import siblings absolutely (`from lodge.core.model import X`); across packages only `from lodge.<pkg> import X` |
| T3-T4 | T3 model, `parse_record`, `parse_area`; T4 `load(tree: Tree)`, `Tree` defined in T4's `snapshot.py` | agree |
| T3-T7 | T3 `Draft{kind, header, body, source}`, `record_from_draft`, `content_hash`; T7 `apply_drafts` builds records through them | agree |
| T4-T5 | T5 `check_state(s)`, `check_change(published, after, settings)` derive internally (check 6 uses `derive(published)`) | agree |
| T5-T6 | T6 `failing_ids`, `unrecorded_problems` take T5's `CheckResult` | agree |
| T6-T7 | T7 `feedback` calls T6 `related` | agree |
| T3/T5/T7-T8 | T8 uses `CoreSettings`, `check_change`, `apply_drafts`, `Applied`, `feedback`, `Filters`, view types | agree |
| T8-T9 | T8 `Store{trees, freshness, publish(base, writes, message)}`, `PublishOutcome`, `LodgeError`, `Clock`; T9 implements and raises them | agree |
| T9-T10 | T10 `main` uses `repo_root`, `load_settings`, `open_store(root, settings, clock, lock_wait_seconds=30)`, `init_store`, `data_root`, `ProjectSettings.raw` | agree |
| T10-T11 | `cli.run(…, view: Callable[[int], int], …)`; T11 `serve(make_lodge, port) -> int` | agree |
| T10-T12 | `cli.run(…, hook: Callable[[], int])`; T12 `run(stdin, stdout, context)`, `parse_hook_settings` called by `main` | agree |
| T1-T13 | `scripts/check.sh` gains `lodge check --gate` in T13 | agree |
| T1-T2, T13-T14 | tags `v0.1.0.dev0` (T1), `v0.1.0` (T13, version bumped first) | agree |
| T10 self | `test_wheel` runs `uv build`, which may fetch the build backend; CLAUDE.md says tests use no network | Ruling: `test_wheel` may use uv's cache and network, and skips with a stated reason when offline; why: packaging is otherwise first tested in a cloud child (T14); cost if wrong: one slow test that needs the network. |
| T1 self | `MAX_LINES` covers tests; Task 3's test list is long | agree: builders split test files by subject |
| each task self | tests named against the interfaces each task defines; files created before they are modified | agree |

Ruling: review packages live in the git-ignored SDD workspace, briefs, reports, and reviews in the committed folder; why: the process in `CLAUDE.md` keeps the record in the repository, and a diff copy adds nothing to git; cost if wrong: none.

## Tasks

Task 1: done b975932 (DONE_WITH_CONCERNS; check.sh green, 59 tests; tag v0.1.0.dev0 pushed).
Task 1: Ruling (builder's, adopted): `now`, `today`, `utcnow`, `fromtimestamp` are banned in `core` and `app` only as attributes of `datetime.datetime` or `datetime.date` resolved through imports, so the Clock port's `clock.now()` passes; why: the plan's literal ban on the name would reject its own port; cost if wrong: an aliased class (`d = datetime; d.now()`) slips past, while the module allow-list still keeps `time`, `os`, and `secrets` out.
Task 1: Ruling: Ruff's Markdown formatting excluded for `docs`, `README.md`, and `CLAUDE.md`; why: those files follow one sentence per line, which a formatter would rewrap; cost if wrong: none.
Task 2: started, request relayed to the first user's session.
Task 1: review: spec no (root `__init__` may import non-lodge modules), quality not approved; 0 Blocking, 3 Important (I1 root imports, I2 process spawning outside gitstore, I3 file writing unconfined), 6 Minor; all taken into fix round 1 since it touches the same files.
Task 1: fix round 1/5 (10 addressed, 0 open; recheck found O1 Important, `files('lodge.viewer').joinpath(…).read_text()` rejected though Task 11 needs it, predating the fix; N1 `webbrowser.open` read as writing; N2 `rename`, `symlink_to`, `io.FileIO(p, 'w')` pass; commits e447243..6680130).
Task 1: fix round 2/5 (3 addressed, 0 open; commits c64fdf2..3eb75ce).
Task 1: complete (commits e87a528..3eb75ce, review clean).
Task 1: minor (deferred): R1 `files(...).joinpath(p).open('w')` in viewer passes (structure_calls.py:218-224 skips the mode check for package data); fix: exempt only webbrowser there.
Task 1: minor (deferred): R2 package-data names are module-wide, so a reused name or parameter lets a plain Path read pass in viewer (structure_calls.py:71-73, :158).
Task 1: minor (deferred): R3 `files` matched by spelling (`files = Path`, `Path as files`, `def files`, `self.files(...)` pass) (structure_calls.py:148-150).
Task 1: minor (deferred): an aliased datetime class in app (`d = datetime.datetime; d.now()`) passes.
Ruling: R1 to R3 wait for the final fix wave rather than a third round; why: they are all in the viewer exemption, no later task builds on them, the task reviews read every task's diff for I/O in any case, and name-based rules cannot be complete; cost if wrong: a viewer write slips past the test until the final review.
Task 3: done 1df405a, 0615d5c (DONE_WITH_CONCERNS; check.sh green, 388 tests).
Task 3: Ruling: `record_from_draft(date=...)` given means a new decision and a draft carrying `date` is refused unless imported; `date=None` means an existing record whose draft keeps its own date; Task 8 calls it that way; why: matches the plan's calls on dates and edits; cost if wrong: Task 8 rewires one call.
Task 3: Ruling: `slug` gets a 60-character cap, cut at a word boundary; why: six long words can pass a file-name limit, and the slug is the plan's call, not the spec's; cost if wrong: none; taken in this task's fix round or the final wave.
Task 3: review: spec no (slug cap ruling not implemented), quality not approved; 0 Blocking, 2 Important (I1 deep nesting raises RecursionError instead of a Problem; I2 no slug cap, Errno 36 on long titles), 8 Minor; all into fix round 1 (same files).
Task 3: Ruling: `quote.text` may hold line breaks and tabs, written as JSON escapes; other header strings keep the control-character ban; why: her words can span lines and the JSON quoting reads them back exactly; cost if wrong: none.
Task 3: Ruling: a loaded header joins UTF-16 surrogate pairs (as `json.dumps` writes emoji by default) into the character they encode; a lone surrogate stays problem 1; why: an agent writing drafts with `json.dumps` defaults would otherwise be refused for any emoji in her words; cost if wrong: none.
Task 3: fix round 1/5 (10 addressed, 0 open; round trip held over 3,048 records; commits dba944f..1b6f314).
Task 3: complete (commits 41650f9..1b6f314, review clean).
Task 3: interface change: `Draft` gained a last field `header_text: str = ""` (M6), so draft problems carry the key's line; later tasks construct `Draft` only through `parse_draft`.
Task 3: minor (deferred): a body holding `\r\r\n` parses but cannot be rewritten (`document.py:14-15`, `normalise_newlines`); predates the fix.
Task 4: done 25c7180 (check.sh green, 433 tests).
Task 4: review (2 Blocking, 4 Important, 2 Minor) in task-4-review.md; fix round 1 takes B1, B2, I1, I2, M1.
Ruling: B2 follows the plan over the brief, so an imported decision raises the flag whatever its `decided_by`; why: the plan's "Calls made" (plan:51) governs the brief, and check 3 exempts imports from the quote, so an unflagged import is must-not 2; cost if wrong: an imported author decision gets a flag she clears with one confirm.
Ruling: I1, the flag clears only on a non-imported author decision ordered after the flagged one; why: the spec says "a later author decision" (Review flag), and imports are exempt from check 1's dates and check 3's quote; cost if wrong: an imported confirmation from the old record leaves a flag she confirms again.
Ruling: I2, `derive` orders imports by date like live decisions, and Task 5's check refuses an imported decision that changes an entry a published non-imported decision already changed; why: one snapshot cannot tell an import added after her live edit from one added before it, and flagging both flags her own imports whenever she later edits the entry (task-4-recheck-1.md, N1, probes R1 and R2), while the add-time check sees the published snapshot; cost if wrong: an old record that changes an entry she already edited live goes in as a live decision with its quote, not as an import.
Ruling: the builder's wrong-folder problem 1, the latest-earlier-change rule, dangling IDs dropped from derived maps (B1 computes the flag over all targets first), newest-first order with ties by larger ID, and `Tree.rev` in `vulture_allow.py` stand; why: each matches the spec's wording or the reviewer ran it clean (task-4-review.md, Pass 2 and 3); cost if wrong: a rename or reorder in Task 7.
Parked: Task 4 M2 (same-second decisions of one add order by random ID) for Task 7 or 8, where `apply_drafts` fills dates.
To the author: Task 4 I3 (an agent change to something she confirmed raises no flag) as LODGE-6, and I4 with recheck P12 (replacing an agent's decision leaves its retirement or its text on the entry) as LODGE-7; the build follows the spec's wording until she answers.
Task 4: fix round 1/5 4fb80cc (B1, B2, I1, I2, M1; 440 passed).
Ruling: `Derived.confirmed_by` keeps listing every author confirmer, imported or earlier-dated ones included; why: it records who confirmed, and the flag, not that list, says whether her review is outstanding (spec, Review flag); cost if wrong: a reader sees a confirmer beside a decision still flagged, and Task 9's reader filters the list.
Task 4: recheck 1 (B1, B2, I1, M1 fixed; N1 overturns the I2 fix, N2 and N3 Minor) in task-4-recheck-1.md; fix round 2 takes N1 and N3.
Parked: Task 4 N2 (a same-second confirm with the lower ID does not clear the flag) with M2 for Task 7 or 8.
Task 4: fix round 2/5 faa7aeb (N1, N3; 441 passed).
Task 4: recheck 2 clean (0 Blocking, 0 Important; M3 taken into task-5-brief.md).
Task 4: complete (commits 25c7180..faa7aeb, recheck clean).
Task 5: done ca82fc8 (check.sh green, 525 passed).
Ruling: check 7 requires the area order to list exactly the current entries, so a retirement edits the order in the same change and gives a note; why: the plan's reading of check 7 (plan, Task 5) says "exactly the current entries", and Task 7's add removes a retired entry from the order; cost if wrong: one note per retirement.
Ruling: check 5 compares a published header's `date` as the stored string, and `statement` with the other keys; why: "a published decision whose header differs in any key" (plan, Task 5, check 5) forbids a reformatted date as much as a moved one; cost if wrong: a harmless reformat is refused.
Task 5: review (1 Blocking, 2 Important, 5 Minor) in task-5-review.md; fix round 1 takes B1, I1, I2, and M1 to M5 (all in the files the round touches).
Ruling: I2, `check_change` gains a fourth parameter `now: datetime` (timezone-aware), and check 1 fails a new decision, imported or not, dated after `now`; why: one future-dated record otherwise blocks every later change to what it touches (task-5-review.md, I2, run), against "one bad record never blocks everyone", and the spec's Structure has core take the time as a parameter; cost if wrong: one parameter through Task 8, whose brief passes `clock.now()` (plan:380 omits `settings` too; Task 8's brief carries both).
Ruling: M3, a listed attachment name resolves to `lodge/attachments/<decision id>/<name>`, one form only; why: the spec's Storage layout places attachments at `lodge/attachments/<id>/` (spec:208); cost if wrong: Task 9 and the guide (Task 13) follow this form and change together.
Ruling: the builder's points 4 to 6 are overturned by B1, M1, and M3; points 1 to 3 stand (task-5-review.md accepts them).
Task 5: fix round 1/5 cdb45ca (B1, I1, I2, M1 to M5; 542 passed).
Task 5: recheck 1 clean (0 Blocking, 0 Important, 2 Minor) in task-5-recheck-1.md.
Parked, must-fix in the final fix wave: Task 5 N1, author reasoning compares by word list, so re-paragraphing her reasoning passes with no note (`check_immutable.py:24`); compare it exactly.
Carried to Task 8's brief: Task 5 N2, read `now` after the clock reading that dates the decisions, and pass `settings` and `now` to `check_change`.
Task 5: complete (commits ca82fc8..cdb45ca, recheck clean).
Task 6: done 7a51397 (check.sh green, 566 passed).
Ruling: search and `related` take words as runs of letters or digits, lower-cased, and ignore a fixed list of English function words; why: with digits as separators a query for a results number finds nothing, and with function words counted `related`'s threshold of 2 is met by "the" and "is" (task-6-report.md, concerns 1 and 3); cost if wrong: a query made only of function words falls back to the exact ID or code match.
Task 6: review (1 Blocking, 6 Important, 5 Minor) in task-6-review.md; fix round 1 takes all of them and the search-words ruling.
Ruling: B1, `Level1` gains `quote: Quote | None`, printed by `format_level1` after the statement as `quote: "<text>" (<where>, <when>)`; an entry shows the quote of its newest changing decision when that decision is the author's; why: spec:174 makes the quote at level 1 the safeguard for LODGE-2, and the spec outranks the plan's `Level1` (plan:283-286); cost if wrong: one more line per level-1 read; Tasks 8, 10, and 11 consume the new field.
Ruling: I1, `render_spec(s, d, failing, area=None)` marks an entry carrying `awaiting the author`, `imported`, or `fails check` as `## <title> (<id> · <flags>)`; why: must-not 1, the plan's format (plan:307) shows them as settled; cost if wrong: noisier headings in the rendered specification.
Ruling: I2, `level2(s, d, record_id, failing)`, and an entry whose newest changing decision fails the check carries `decision fails check`; why: must-not 1 (task-6-review.md, I2, run); cost if wrong: one more flag string for Tasks 10 and 11.
Ruling: I3, `load` files the duplicate-ID problem against both paths, so both records fail; why: mapping by path is how `failing_ids` works, and parsing paths out of messages would couple it to wording; cost if wrong: a published duplicate gives two notes instead of one.
Ruling: I4, no Task 6 change; every CLI read (Task 10) and every viewer page (Task 11) shows `unrecorded_problems` above its output, naming the files lodge cannot read; why: a file that does not parse cannot be attributed to any record, and the check refuses publishing a new one, so only a hand-edited checkout reaches this; cost if wrong: reads that are right but carry a warning line.
Ruling: I5 and the review's conditions, search lists by filters alone only when `query.strip()` is empty, a query with no searchable words returns only the exact ID or code match, and `related` drops pure-digit words; why: task-6-review.md, I5 and the ruling section; cost if wrong: a bare number finds nothing except by ID.
Ruling: I6, an entry whose newest changing decision is replaced or narrowed carries `its decision replaced by <ids>` or `its decision narrowed by <ids>` after `retired by` in the flag order; why: must-not 1, the spec is silent on this case; cost if wrong: one more flag string, renamed in one place.
Task 6: fix round 1/5 90e9af4 (B1, I1 to I3, I5, I6, M1 to M5, search words; 579 passed).
Ruling: `render_spec` puts every level-1 flag of an entry in its heading, not only the three the I1 ruling names; why: the other flags (`its decision replaced by`, `decision fails check`) are must-not 1 cases too; cost if wrong: longer headings.
Ruling: Task 4 M2 and N2 are taken in Task 7: `apply_drafts` assigns new IDs in ascending order to the decision drafts in draft order; why: dates are shared within one add and `derive` breaks ties by ID, so draft order becomes decision order without faking seconds; cost if wrong: two adds in the same second still tie by random ID, which check 1 refuses for linked decisions.
Task 6: recheck 1 clean (0 Blocking, 0 Important, 0 Minor) in task-6-recheck-1.md.
Carried to Task 10's and Task 11's briefs: the I4 ruling, with the unreadable-file lines placed above the output and a test pinning that order (a broken agent-decision file leaves her quote under the agent's text).
Task 6: complete (commits 7a51397..90e9af4, recheck clean).
Task 7: done 27beffe (check.sh green, 623 passed).
Ruling: the builder's `StaleBase` problem subclass, the refusal of an edit draft with no `base`, `imported_from` refused outside `--import` only when a draft changes a record's origin, and the number rule on decisions only stand; why: each closes a path the brief left open toward an unseen overwrite or a blocked edit (task-7-report.md, concerns 1 to 3 and "Behaviour worth knowing", the number rule); cost if wrong: one more refusal message, or Task 8 matching on a subclass.
Carried to Task 8's brief: `apply_drafts` raises `ValueError` unless `add` mints exactly one ID per decision draft without one; `StaleBase` maps to `Conflict`.
Task 7: review (0 Blocking, 2 Important, 11 Minor) in task-7-review.md; fix round 1 takes I1, the I2 wording, and M1 to M9; M10 fixed in the ledger; M11 goes to Task 8's brief.
Ruling: I2, `add` gains `dry_run: bool` (Task 8's operation, `lodge add --dry-run` in Task 10), which applies, checks, and prints feedback without publishing, and the guide (Task 13) says to dry-run before adding; the feedback messages name the remedy as a change to the draft; check 5 keeps the plan's "every header key" rule; why: feedback prints after publishing, and in branch mode check 5 then refuses the edit the feedback asks for (task-7-review.md, I2, probe2), while a dry run keeps feedback advice and never a refusal (spec, Writing); cost if wrong: one flag through Tasks 8, 10, and 13.
Carried to Task 8's brief: Task 7 M11, `feedback` gets the new decisions and every written entry, never edited decisions.
Task 7: fix round 1/5 f4bf61f (I1, I2 wording, M1 to M9; 634 passed).
Task 7: recheck 1 clean (0 Blocking, 0 Important, 1 Minor) in task-7-recheck-1.md.
Parked: Task 7 N1, the ID message always says "IDs are lower case", misleading for a lower-case ID of the other kind or an empty one (`apply.py:245-250`); next round touching `apply.py`, else the final fix wave.
Task 7: complete (commits 27beffe..f4bf61f, recheck clean).
Task 8: done f3e4ea1 (check.sh green, 674 passed).
Ruling: `app` reaches the five core names that are also core module names (`check_change`, `check_state`, `derive`, `feedback`, `search`) as `from lodge import core` and `core.<name>`, and Tasks 10 to 12 do the same; the structure rules and module names stay; why: `tests/structure_imports.py` reads `from lodge.core import derive` as the submodule, and changing that rule is the author's call (CLAUDE.md, Structure checks); cost if wrong: two import styles side by side until a rename.
Ruling: the builder's `core_settings(table)` in `lodge.app`, `tests/app/conftest.py` reusing the core test helpers, and fresh IDs on each retry stand; why: each is inside the brief's interfaces (task-8-report.md, concerns 2 to 4); cost if wrong: `Added.ids` names IDs no earlier attempt published, which is correct.
Task 8: review (0 Blocking, 1 Important, 7 Minor) in task-8-review.md; fix round 1 takes I1, M1 to M4, M6, and M7; M5 parked.
Ruling: M4, a refusal on a retry that names an area or entry absent from the first attempt's snapshot becomes `Conflict`; why: it is a race, and exit 1 tells the caller to retry (task-8-review.md, M4, probe); cost if wrong: a genuine usage error that only shows on a retry exits 1.
Ruling: M7, writes equal to the current file are dropped, and an add with nothing left publishes nothing and reports `PUBLISHED` with the note "nothing changed"; why: an empty commit in branch mode is noise in her history; cost if wrong: one note string.
Parked for the final wave: Task 8 M5, feedback when a new decision replaces a decision already replaced ("d-aaaaaa is already replaced by d-cccccc", in `core.feedback`).
Task 8: fix round 1/5 e63e09f (I1, M1 to M4, M6, M7; 684 passed).
Task 8: recheck 1 (0 Blocking, 1 Important, 2 Minor) in task-8-recheck-1.md; fix round 2 takes R1 to R3.
Task 8: fix round 2/5 eb81709, 76397bf (R1 to R3; 688 passed).
Task 8: recheck 2 clean (0 Blocking, 0 Important, 1 Minor) in task-8-recheck-2.md.
Parked for the final wave: Task 8 R4, the entry branch of `_raced` is untested; construction in task-8-recheck-2.md.
Task 8: complete (commits f3e4ea1..76397bf, recheck clean).
Task 2: complete (a cloud session ran `uv tool install git+https://github.com/Kiibou-chan/lodge@v0.1.0.dev0`, built from b975932, `lodge --version` printed `lodge 0.1.0.dev0`; auto mode blocked the install until she wrote "I allow this" in that session's chat; recorded in the spec's Constraints, and Task 14 tests whether repository instructions, a settings allow rule, or the spawning prompt authorise it).
Task 9: done db48cc7 (check.sh green, 751 passed).
Ruling: the builder's choices stand: `ProjectSettings.raw` is the whole table (Task 12's `main` passes `raw.get("hook", {})`), the stale mark after a rejected push lives in the process, attachments are never overwritten, and pushes run her pre-push hooks; why: the stale mark only shortens the next fetch wait and a push without force rejects a stale tree anyway, and her hooks are hers to keep (task-9-report.md, concerns 1 to 6); cost if wrong: a pre-push hook can refuse lodge's push, shown as a `LodgeError`.
Her answers: LODGE-6 "A: Yes, flag it" (17:17) and LODGE-7 A (17:19), recorded in the spec; Task 4 I3 and I4 and recheck P12 are built in a LODGE round on `derive`, `apply_drafts`, and `feedback` before Task 9's fix round.
Task 4: LODGE round cd7a6bf (LODGE-6, LODGE-7; 764 passed).
Ruling: for "the entry's last change", `derive` skips changes by a decision that is neither hers nor confirmed by her (LODGE-6) and that a non-imported author decision replaces, so after she replaces an agent's retirement or edit the entry's last standing change is the one before it; why: LODGE-7 A has replacing undo the change where lodge can work it out, and otherwise the next agent edit of an entry she just took back is unflagged (task-4-report.md, LODGE round, concern 2); her own replaced decisions stay counted, since correcting her own decision must not unflag the next agent edit (lodge-round-recheck.md, L1, probes H1 and H1b); cost if wrong: an agent edit after her rejection is flagged even when her own last change is older.
Task 4: LODGE round part 2 5815098 (replaced changes skipped; 767 passed).
LODGE round: recheck (1 Blocking, 1 Important, 2 Minor) in lodge-round-recheck.md; part 3 takes L1 to L4.
Ruling: L2, a decision that revives an entry by replacing its last standing retirement counts as changing that entry, so an agent reviving her retired entry shows the flag on the entry; L3, `retired by` names only standing retirements; L4, feedback says which entries a replacing decision revives; why: must-not 1, each read otherwise shows a revived or retired entry as more settled than it is (lodge-round-recheck.md, H2 to H4); cost if wrong: one more feedback line per revival.
Task 4: LODGE round part 3 be90780 (L1 to L4; 773 passed).
Task 9: review (1 Blocking, 2 Important, 7 Minor) in task-9-review.md; fix round 1 takes all of them.
Ruling: B1, checkout mode refuses any path under `lodge/` that passes through a symbolic link (checked with `lstat` per component, under the lock) and reads a link as its target text without following it, as branch mode already does; why: the probe overwrote a file outside the repository through a linked record (task-9-review.md, B1); cost if wrong: a deliberately linked record folder stops working in checkout mode.
Ruling: I1, after any failed push the store asks the remote (`ls-remote`) and returns `REJECTED` when the branch moved, so `add` retries; why: two clones pushing at once lose with "incorrect old value provided", 20 of 20 rounds (task-9-review.md, I1); cost if wrong: one extra remote call on a failed push.
Task 9: fix round 1/5 a7e666f (B1, I1, I2, M1 to M7; 791 passed).
LODGE round: recheck 2 (0 Blocking, 2 Important, 1 Minor) in lodge-round-recheck-2.md; part 4 takes N1 to N3 as its Fix lines say.
Task 4: LODGE round part 4 ba2f6a5 (N1 to N3; 795 passed); the edit-back wording is a builder's, not hers.
LODGE round: recheck 3 (0 Blocking, 1 Important, 1 Minor) in lodge-round-recheck-3.md; part 5 takes N4, N5, and a test for probe U1.
Task 4: LODGE round part 5 954a9a6 (N4, N5, U1 test; 799 passed).
Task 9: recheck 1 (1 Blocking, 1 Important, 1 Minor) in task-9-recheck-1.md; fix round 2 takes N1 to N3.
LODGE round: recheck 4 clean (0 Blocking, 0 Important, 1 Minor) in lodge-round-recheck-4.md.
Parked for the final wave: the `Derived` docstring (derive.py:19-21) does not say its maps hold known entries only.
LODGE round: complete (commits cd7a6bf..954a9a6, LODGE-6 and LODGE-7 built, Task 4 I3, I4, and P12 closed).
Task 9: fix round 2/5 b57b2e1, f440ed8 (N1 to N3; 805 passed).
Task 9: recheck 2 clean (0 Blocking, 0 Important, 1 Minor) in task-9-recheck-2.md.
Parked for the final wave: Task 9 M1, the umask is read by setting it briefly (`checkout.py:194-197`); create new files with `os.open(..., O_CREAT | O_EXCL | O_NOFOLLOW, 0o666)` instead.
Task 9: complete (commits db48cc7..f440ed8, recheck clean).
Task 10: done dfdea3c (check.sh green, 885 passed, the wheel test included).
Ruling: the builder's choices stand: `test_add_non_string_scalar_exits_2` uses a list, since every YAML scalar is text (tests/core/test_yamlio.py:6-10); `problem:` lines add `:<line>` when known; `search` takes an optional query; output streams replace undecodable characters; a failed dry run prints both lines; any `hook` argv skips parsing and exits 0; why: each is within the brief or makes its output more exact (task-10-report.md, concerns 1 to 4 and 6); cost if wrong: one line of output text.
Task 10: review (0 Blocking, 2 Important, 5 Minor) in task-10-review.md; fix round 1 takes I1, I2, and every Minor.
Ruling: I1, the `Clock` port gains `sleep(seconds: float) -> None`, and `add` waits through it until its date is after the newest decision in the current tree, so no two adds share a second; check 1 also compares a new decision with the decisions of the current state, not only the published one; why: two adds in one second credited an agent's edit of her entry to her and passed the gate in 5 of 7 runs (task-10-review.md, I1, `same_second.sh`), a breach of must-nots 1 and 2; cost if wrong: an add waits up to one second.
Ruling: I2, `lodge add --attach PATH...` copies each file into `lodge/attachments/<id>/<file name>` of the one new decision the add creates (refused when the add creates none or several), in the same publish; the decision's `attachments` must list exactly those names; files are read by `cli` (LODGE-5 lets it read files it is given) and must be UTF-8 text in 0.1, any other file refused with one sentence; why: the spec promises attachments ("expanded evidence like logs or anything else attached", Her decisions), the guide describes them, and no route existed, none at all in branch mode (task-10-review.md, I2); cost if wrong: binary evidence waits for a later version.
Task 10: fix round 1/5 58c64f4, fb9e3bd (I1, I2, M1 to M5; 916 passed).
Ruling: `--attach` is given once per file, `add` waits at most three times, and attachments keep their bytes as UTF-8; why: a greedy list would swallow the draft files, and a decision dated further ahead is check 1's to refuse (task-10-report.md, Fix round 1, concerns 1, 3, and 4); cost if wrong: one more flag per attachment.
Task 10: recheck 1 clean (0 Blocking, 0 Important, 2 Minor) in task-10-recheck-1.md.
Parked for the final wave: Task 10 N1 (the guide does not say a listed attachment name is the file's own base name) and N2 (a decision dated ahead of the local clock makes every add wait about 3 s).
Task 10: complete (commits dfdea3c..fb9e3bd, recheck clean).
Task 11: done 52ee558 (check.sh green, 948 passed; pages looked at in the browser pane, light and dark).
Task 11: review (0 Blocking, 1 Important, 4 Minor) in task-11-review.md; fix round 1 takes I1 and M1 to M4.
Ruling: I1, `core` gains `spec_view(s, d, failing, area=None)` returning the areas as structure (title, intro, `Level1` entries in order); `render_spec` formats that structure and puts a backslash before any intro or statement line starting with `#`; the app's `spec` returns the structure beside the text, and `spec_page` builds its headings from the fields, never by parsing Markdown; why: a statement starting `## ` rendered a flagged entry's text as a separate unflagged entry (task-11-review.md, I1, run), must-not 1, and the escape keeps `lodge spec` output unambiguous too; cost if wrong: one more core function and a changed `spec_page` signature.
Ruling: M4, "no record named x" is a 404: `Lodge` raises a `NotFound(LodgeError)` subclass for an unknown reference, still exit 2 in the CLI; why: a viewer link to a missing record is not a bad request; cost if wrong: one subclass.
Task 11: fix round 1/5 de95297 (I1, M1 to M4; 953 passed).
Task 11: recheck 1 clean (0 Blocking, 0 Important, 2 Minor) in task-11-recheck-1.md.
Parked for the final wave: Task 11 N1 (`render_spec` misses indented `##` lines and `---`/`===` underline headings in `lodge spec` text) and N2 (flag IDs on search, timeline, and spec rows are plain text; add a `statuses` map to `Read` and link them).
Task 11: complete (commits 52ee558..de95297, recheck clean).
Task 12: done bc73e71 (check.sh green, 991 passed).
Task 12: review (0 Blocking, 1 Important, 5 Minor) in task-12-review.md; fix round 1 takes I1 and M1 to M4.
Ruling: I1, the hook's advice is the review's text (reverse your own edit with the same tool; never `git checkout`, `git restore`, `git stash`, or `git clean` on the file; tell the author if it cannot be restored exactly); why: "undo with git" discards her uncommitted edits and records an earlier `lodge add` staged (task-12-review.md, I1); cost if wrong: none.
Ruling: M1 and M2, the hook finds the repository from the edited file's folder, not the session's, and fires only where lodge is initialised there; M3, the README states the frozen-glob syntax lodge implements, relative to the repository root (`*` does not cross `/`, `[...]` is literal); M4, the frozen-file text names `lodge guide`; M5, resolving the edited path counts as reading the hook's input (LODGE-5); why: task-12-review.md, Minors, each run; cost if wrong: one more path lookup per edit.
Task 12: fix round 1/5 6d8a183 (I1, M1 to M4; 998 passed).
Task 12: recheck 1 clean (0 Blocking, 0 Important, 2 Minor) in task-12-recheck-1.md.
Parked: Task 12 N1 (a relative path without a payload `cwd` is located differently in `context` and `respond`) for the final wave; N2 (README.md:31 still says `fnmatch`) goes to Task 13, which writes the README.
Task 12: complete (commits bc73e71..6d8a183, recheck clean).
Ruling: Task 13 builds and pushes the branch but creates no tag; `v0.1.0` is tagged after the final review and the merge, on her go; why: a tag on the public repository is a release others can install, and the code has not had its final review; cost if wrong: Task 14 waits for the tag.
Task 13: done fe01a67 (21 author decisions through `lodge add`, LODGE-1 to LODGE-7 coded; README; version 0.1.0; `lodge check --gate` in check.sh; 998 passed; no tag).
Dogfooding found: `lodge search` stops at 20 results without saying so (`core/search.py:46`); "looks related" feedback fires on shared common words; `--dry-run` mints a different ID than the real add.
Task 13: review (0 Blocking, 3 Important, 4 Minor) in task-13-review.md; fix round 1 takes I2, I3, and the Minors that change no record file; I1 (four of her records state things she did not say) goes to her as LODGE-8, since fixing it means either changing record files outside `lodge add` (CLAUDE.md, Hard rules) or replacing her records with agent decisions.
Task 13: fix round 1/5 bf7ef0b (I2 search names what it left out, --limit; I3 related needs two shared uncommon words; M1 report wording; 1005 passed). I1 awaits her LODGE-8 answer.
Task 13: recheck 1: 0 Blocking, 1 Important (R1 common-word filter untested), 2 Minor (m1 --limit help text, m2 limit test passes on old source); fix round 2 to the builder.
Task 13: fix round 2/5 3146305..b73c1d8 (R1 common-word test fails without the filter, m1 help text, m2 limit message; 1005 passed).
Task 13: recheck 2 clean (R1: test_related_ignores_a_word_most_decisions_carry fails with `_COMMON_FROM = 10**9`, passes at 5; m1 help reads "up to --limit"; m2 asserts the message; 19 search tests pass).
Ruling: the coordinator rechecked fix round 2 itself instead of resuming the rechecker; why: a 4 KB diff over three files, and its one load-bearing claim (R1) settled by a mutation run in a scratch copy; cost if wrong: a missed Minor in six changed lines, still covered by the final review.
Task 13: code complete; I1 (four author records) awaits her LODGE-8 answer before `Task 13: complete`.
Ruling: the final whole-branch review runs before Task 14, not after; why: Task 14 installs the v0.1.0 tag, and the tag comes only after the final review and the merge, on her go (Task 13 ruling); cost if wrong: none to the code, Task 14 runs later than the plan orders.
Final review 1 (correctness, git store safety) at 72d31fa: 0 Blocking, 5 Important (R1 decided_by spellings, G1 lock left on SIGTERM, C1 checkout gate checks the working tree, C2 missing base passes the gate, G4 rewritten lodge branch accepted), 5 Minor (G2, G3, C3, A1, H1); review 2 next, then one fix wave.
Final review 2 (design, must-nots) at 72d31fa: 0 Blocking, 4 Important (D1, D2, D12, D13), 9 Minor (D3 to D11).
Ruling: D1 (reads run checks 4 to 6) and D13 (personal paths in the spec and the brainstorm, on main) go to the author; why: D1 changes the spec's sentence on which checks reads run, and the spec and the brainstorm are her text; cost if wrong: a delay only.
Ruling: D12, the four review files' scratch paths are replaced with "the reviewer's scratch directory", and the pushed history keeps them; why: rewriting a pushed public branch is destructive and needs her go, and the path names only the account already public as the GitHub identity; cost if wrong: the path stays readable in the branch history until she rules.
Ruling: C1, the checkout gate checks both HEAD's tree and the working tree and fails if either fails; why: HEAD alone stops checking staged records before a commit, the working tree alone misses a partial commit; cost if wrong: a gate run with uncommitted, broken records fails before the commit, which is the earlier and cheaper place.
Ruling: G1, a branch-mode read that cannot take the lock serves the cached ref and says so; why: the plan's offline rule already serves the cache on a failed fetch, and a read never needs the lock to be correct; cost if wrong: a read during another add shows a state at most one add old, labelled.
Ruling: R1, check 3 refuses a decided_by that contains "author" in any spelling but is not exactly "author"; why: a lookalike reads as hers with no quote (must-not 1, LODGE-2); cost if wrong: an agent role spelt with "author" in it, such as "co-author", is refused and must be renamed.
Ruling: the final wave runs as Part A (Important and must-fix) then Part B (minors), each with a fresh builder and one recheck, brief in final-wave-brief.md; why: thirty items overflow one builder's context; cost if wrong: one extra recheck.
Final wave A: aecd456..125231f (items 1 to 7; 1035 passed); concerns in final-wave-a-report.md: an add after a rewrite builds on the fetched tip, so the rewrite notice ends with the next commit.
Final wave A: recheck 1 in final-wave-a-recheck.md: C1, C2, G1, R1, D2, Task 5 N1 closed; G4 open (an add after a rewrite, or a plain git fetch before lodge's, lets the rewrite through); new Minors N1 (SIGTERM kills a running git, which can leave index.lock) and N2 (a cache read over an old lock no longer says it may be left over).
Ruling: G4, lodge keeps its own ref `refs/lodge/accepted`, the last lodge tip it accepted, moved only by lodge (forward on a read whose fetched tip contains it, and after its own push; set on first use); every read compares it with the remote-tracking tip, a rewrite stands until acknowledged, reads say so, `check --gate` compares the accepted tip with the new one, and `add` refuses while that comparison has problems; the acknowledgement is deleting the ref with the git command the message names, not a new flag; why: git's own fetch moves the remote-tracking ref, so only a ref lodge alone moves can see a rewrite, and a git command keeps the CLI the spec describes; cost if wrong: a stranger has to run one git command to accept a rewrite they meant.
Ruling: N1, the signal handler defers the exit while a git child runs and exits when it returns; why: killing git mid-write leaves index.lock, which blocks the user's own git; cost if wrong: a SIGTERM waits for at most one git call.
Final wave A: fix round 1/5 fc4b4ce (G4 refs/lodge/accepted, N1, N2; 1041 passed); an add refused over a rewrite prints check 5 lines without naming the rewrite.
Final wave A: recheck 2 in final-wave-a-recheck-2.md: G4, N1, N2 closed; 0 Blocking, 0 Important; Minors M1 (deferred exit blocks the viewer's SIGTERM), M2 (rewrite test fails open on a git error), M3 (refused add does not name the rewrite) go to Part B as items 21 to 23.
Final wave A: complete.
Ruling: Part B runs in two dispatches, B1 (items 1 to 10 and 21 to 23) and B2 (items 11 to 20), each with a fresh builder and one recheck; why: the Part A builder reached about 220k tokens on seven items; cost if wrong: one extra recheck.
Final wave B1: de788ee, 2c6b62b (items 1 to 10, 21 to 23; 1050 passed); check 5 and 6 tests moved to tests/core/test_check_immutable.py for the 300-line rule.
Ruling: recheck B1 (fresh Sonnet rechecker on a scratch copy of 2c6b62b) and build B2 run at the same time; why: the rechecker never writes to the worktree, and any B1 fix folds into the B2 recheck round; cost if wrong: a B1 fix lands after B2 and needs one more small recheck.
Final wave B1: recheck 1 in final-wave-b1-recheck.md: 0 Blocking, 0 Important, all 13 items closed (eleven by reverting the fix and seeing the test fail); Minors m1 (viewer SIGTERM during a locked request leaves lodge.lock) and m2 (a dry run check line names an unmarked provisional ID) go to the B2 fix round.
Final wave B1: complete.
Final wave B2: daca72c..da49d8c (items 11 to 20; 1061 passed); item 11 narrows test_record_page_flags_and_both_link_directions to the entry header, its deciding decisions now render as result rows.
Final wave B2: recheck 1 in final-wave-b2-recheck.md: 0 Blocking, 0 Important, items 11 to 20 closed; Minors n1 (no test pins the flag on an entry's deciding decisions in the viewer) and n2 (guide.md:50 wording); one closing round takes B1 m1, m2 and B2 n1, n2.
Final wave B2: closing round 3bafd60 (B1 m1, m2; B2 n1, n2; 1063 passed), read by the coordinator: each fix has its test, the provisional mark applies only in a dry run.
Final wave: complete. `sh scripts/check.sh` on build-0.1 merged with origin/main (c758046, the merge base, so the merge is a fast-forward) in a scratch clone: 1063 passed, gate ok.
Waiting on the author: LODGE-8 (four author records, then `Task 13: complete`), D1 (reads run checks 4 to 6), D13 (personal paths in the spec and brainstorm on main), then the merge go, the v0.1.0 tag go, and Task 14.
History rewrite (author, 2026-10-29 22:12, "Remove them completely"; repository deleted and recreated by the author): private details were removed from the tree, and the history was squashed into two commits, main (design, plan, process files) and build-0.1 (the build on top). Commit hashes cited above refer to the history before the rewrite, kept only on the author's machine.
Ruling: every author record's reasoning is its quote's text and nothing else (21 records re-added through `lodge add`, checked by script: 0 differ); why: the author ruled that nothing but her quotes is her text (22:12), so agent wording under `decided_by: author` is a must-not 1 failure; cost if wrong: author records read less fluently, and her words can be added to them later.
Task 13: I1 closed by the re-add above, which settles LODGE-8.
Task 13: complete.
Author: LODGE-10 (22:46), reasoning of every published decision is immutable, a shorter reasoning is a new decision that replaces it; spec check 5 and Her decisions edited; code (check_immutable shrink note, guide) waits to batch with LODGE-9.
