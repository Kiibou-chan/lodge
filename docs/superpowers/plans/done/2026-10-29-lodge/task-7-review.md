# Task 7 review: feedback on writes, and applying drafts

Commit 27beffe on `build-0.1` (base dd908a1).
Reviewer: `reviewer`, three passes (correctness, practice, design).

## Verdicts

- Spec compliance: yes against the brief, the spec's writing section, and the carried Task 4 and 5 items; one gap against the plan's Global Constraints (I1, a traceback from a draft).
- Task quality: not approved, 0 Blocking, 2 Important, 11 Minor.

## What I ran

- `git archive 27beffe` into `scratchpad/probes-t7/src27`, `uv sync`, `sh scripts/check.sh`: green, 623 passed.
- Every test the brief and the carried section name exists (grep over `tests/core/*.py`, none missing).
- `scratchpad/probes-t7/probe.py` (output `probe.out`): 40 drafts an agent would plausibly write, each through `apply_drafts`, then `load`, and `check_change(published, after, settings, now)`.
- `scratchpad/probes-t7/probe2.py` (`probe2.out`): feedback on number tokens, related wording, an edited old decision, and the follow-up edit an agent makes after feedback, in branch and checkout mode.
- `scratchpad/probes-t7/probe3.py` (`probe3.out`): header values of the wrong shape that `parse_draft` lets through, and an unreadable area file.
- `scratchpad/probes-t7/probe4.py` (`probe4.out`): area intros that might not read back (none failed).

### The write-safety question, answered by the probes

Every write the check would refuse is refused, by `apply_drafts` or by the check, with a message naming the record and field; none was written silently.

- Stale base on an entry: `StaleBase` naming both hashes and the path. Missing base on a decision edit and on an area edit: refused, naming `lodge draft <ref>`.
- Her decision edited: statement, quote, `decided_by`, and date changes, and a shortened reasoning, are each refused by check 5 by field; a dropped `date` is refused by `apply_drafts` (problem 1).
- Agent decision edits: shrunk reasoning passes with the note; a same-length rewrite, an added `numbers`, an added `replaces`, and an added retirement are refused by check 5.
- Retirement by a new decision: the area order loses the entry and the check passes; with an area draft that still lists it, the entry is removed and the check passes; retiring an unknown entry is refused by check 2.
- An entry moved by its draft is refused by `apply_drafts` ("entries do not move areas").
- Area names `../x`, `a/b`, and `Storage` are refused by `read_area_name`; titles `../../etc/passwd` and `日本語` give safe paths (`s-ffffff-etc-passwd.md`, `s-ffffff.md`).
- Imports outside `--import`: a new decision, an edit adding `imported_from`, and an edit dropping it are refused; an edit of an imported entry keeping its origin but without a decision is refused by check 4, so the ruling on report concern 3 opens no path.
- Several decisions in one add take the IDs in draft order and pass the check.
- Known and parked, reconfirmed: her reasoning re-paragraphed passes the check (Task 5 N1, `check_immutable.py:24`, must-fix in the final wave); no new finding.

## Pass 1: correctness

### I1 (Important): a non-string area `name` crashes `apply_drafts` with a traceback

- Handle: `src/lodge/core/apply.py:58`, `names = {d.header["name"] for d in drafts if ...}`.
- Failure: `parse_draft` checks key names only, so an area draft with `name: [storage]` or `name: {a: b}` reaches line 58, and building the set raises `TypeError: unhashable type: 'list'` (probe3, "area name as list" and "as mapping").
  Task 8's `add` maps problems to `LodgeError`, not a `TypeError`, so the user sees a traceback, against the Global Constraints ("no traceback reaches the user") and the shape of Review Focus 2 (a value of the wrong type names the file and key, exit 2).
- Fix: collect only string names, `{n for d in drafts if d.kind == "area" and isinstance(n := d.header.get("name"), str)}`, so the draft goes on to `record_from_draft`, whose `read_str` reports problem 1 naming `name`; test `test_area_name_not_a_string_is_problem` asserting a problem on the draft's source.

### I2 (Important): two feedback messages ask for an edit that the check refuses once the decision is published

- Handles: `src/lodge/core/feedback.py:97-99` (numbers: "add one giving each number's source"), `src/lodge/core/feedback.py:87-89` (related: "does it replace or narrow it?").
- Failure: feedback is printed after the add has published (plan, Task 8, `add`), and in branch mode, the first user's mode (spec:215), current equals published right after it.
  The agent's natural follow-up, an edit draft adding `numbers` or `replaces` to the decision just added, is refused by check 5: probe2 gives `ok = False ['d-hhhhhh: numbers of a published decision was changed']` in branch mode and `ok = True` in checkout mode; probe.py gives the same refusal for an added `replaces`.
  So an agent reading these two messages does not know what to do next, and the only accepted remedy, a second decision replacing the first to carry a handle or a link, doubles records, which is the upkeep must-not 3 guards against.
- Fix, for the coordinator's ruling since it touches Tasks 8 and 10: give `lodge add` a `--dry-run` that applies, checks, and prints feedback without publishing, and have the guide (Task 13) say to dry-run before adding; feedback stays advice, never a refusal, so the spec's "never a refusal at write time" holds.
  Separately, check 5 could accept `numbers` added to a published decision that had none, since the spec's check 5 lists only "statement, quote, `decided_by`, or links" (spec:160) and "every header key" is the plan's call (plan:53).
  At the least, within Task 7, word both messages so the remedy they name is one the check accepts in both modes, with a test per message.

### Minor

- M1. `src/lodge/core/feedback.py:15`, `_CODE` hides every letters-hyphen-digits token, so `top-10`, `Python-3`, `COVID-19`, and the `1` of `3-to-1` are never flagged (probe2).
  Fix: hide only codes that exist in `after`, compared case-insensitively (`feedback` already has `after`); test with `top-10` flagged and `ITEM-1` not.
- M2. `src/lodge/core/apply.py:203`, an entry created and retired in the same add is appended to its area's order, and check 7 then refuses with "order lists s-ffffff, which is not a current entry", an order the agent never wrote (probe, "create and retire in one add").
  Fix: `if i not in order and i not in add.retired`.
- M3. `src/lodge/core/apply.py:53` and `:84`, a `base` key on a new decision (or on an entry draft whose ID does not exist) is dropped silently; a `lodge draft d-…` print with its `id` and `date` lines deleted becomes a new duplicate decision that passes the check (probe, "new decision with base key").
  Fix: refuse `base` on a draft that creates a record ("base is for edits; no record <id> exists to edit").

## Pass 2: practice

### Minor

- M4. `src/lodge/core/feedback.py:87-89`, with one related decision the question reads "does it replace or narrow it?", two pronouns with different referents.
  Fix: name both IDs, "does d-cccccc replace or narrow d-aaaaaa?", and in the plural "does d-cccccc replace or narrow any of them?".
- M5. `src/lodge/core/feedback.py:98-99`, "a record or a runnable command" drops the spec's "a record and key" (spec:103), and the message never shows the key's shape.
  Fix: "…without a numbers handle; give each one as `numbers: [{value: "…", handle: "…"}]`, the handle a record and key or a runnable command".
- M6. `src/lodge/core/apply.py:184-187`, the stale-base message says to print the draft again but not to redo the change on it; an agent that adds the fresh print unchanged writes nothing new and believes its edit landed.
  Fix: "…, so print it again with lodge draft <ref>, make the change on that, and add it".
- M7. `src/lodge/core/apply.py:99-100` and `:137-142`, an edit that drops or alters `imported_from` gets "add with --import to bring in imported records" (probe, "edit removes imported_from"), though the agent is not importing.
  Fix: a separate message for edits, "this draft changes imported_from of <id>; keep it as lodge draft printed it".
- M8. `src/lodge/core/apply.py:110-133`, values of the wrong shape get messages about absence: `area: [storage]` gives "needs an area key", an edit with `id: S-BBBBBB` gives "needs an area key", and `id:` empty gives "the decision  does not exist" with a double space (probe, probe3).
  Fix: tell a missing `area` from a non-string one, and check `is_id` before looking the ID up ("id S-BBBBBB is not a lodge ID; IDs are lower case").
- M9. `tests/core/test_feedback.py:217`, the trailing `assert isinstance(d, Decision)` tests the builder, not feedback; drop it.
- M10. `docs/superpowers/plans/done/2026-10-29-lodge-progress.md:100`, the ruling cites "task-7-report.md, concerns 2 to 4 and 6", but the report lists five concerns and the decisions-only number rule sits under "Behaviour worth knowing".
  Fix: cite "concerns 1 to 3 and Behaviour worth knowing, the number rule"; I concur with the ruling's substance (probes above: the narrowed `imported_from` rule still leaves imported-entry edits to check 4).

## Pass 3: design

- Boundaries hold: `apply.py` imports `drafts`, `fileformat`, `model`, and `snapshot`; `feedback.py` imports `derive`, `model`, `search`, `settings`, and `snapshot`; both under 300 lines (217, 107); no clock or randomness; `StaleBase` exported for Task 8's `Conflict`.
- Serialising goes through `write_record` and `write_area`, so the round-trip guard covers every file `apply_drafts` produces.

### Minor

- M11. `src/lodge/core/feedback.py:26-34` runs every rule on every record it is given, and `Applied.ids` includes edited records (report concern 5); if Task 8 feeds feedback from `Applied.ids`, a reasoning-shrink edit of an old decision is asked whether it replaces newer decisions (probe2, "feedback on an edit of an old decision": `d-cccccc` asked about `d-gggggg`, dated later).
  Fix: carry to Task 8's brief that `feedback` gets the new decisions and every written entry, not edited decisions.
- Noted, no finding: an area draft for an area whose `_area.md` does not parse is written without a base (probe3), since the snapshot lacks the area; the check passes because the published problem disappears.
  This only reaches hand-edited files, which the I4 ruling of Task 6 already reports on every read.

## Files read

`.claude/agents/reviewer.md`; `CLAUDE.md`; the brief and report for Task 7; the review package's file list; `src/lodge/core/apply.py`, `feedback.py`, `drafts.py`, `__init__.py`, `check_entries.py`, the path helpers of `fileformat.py`, the header builders of `headers.py`, `related` in `search.py`, the signature of `check_change`; `tests/core/test_apply.py` (lines 1-60, 100-242), `test_apply_refusals.py`, `test_feedback.py`, `applying.py`, `builders.py`, `document` in `samples.py`; the spec's Must nots, Levels, Writing, and Storage; the plan's Global Constraints, Calls made, Review Focus, Tasks 3 to 8; every `Ruling:` line of the ledger.

## Files not read

`check_state.py`, `check_immutable.py`, `check_areas.py`, `derive.py`, `views.py`, `render.py`, `document.py`, `fields.py`, `yamlio.py`, `model.py`, `settings.py`, `words.py`; `tests/core/test_apply.py` lines 60-100; the rest of `samples.py`; the diff file itself beyond its stat (the commit's files were read whole instead).
