# Recheck of the LODGE-9 and LODGE-10 fix round (1b958d6..5fa6e60)

Verdict: 0 Blocking, 0 Important, 1 Minor.
Probes ran in a clone of the build worktree at 5fa6e60 in the scratch directory; the build worktree was not touched.

## 1. D1 scenario: answered

Checkout-mode repository (`GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_NOSYSTEM=1`, `git init -b main`), author decision ITEM-1 committed on `main`, then `sed` of its statement on branch `work`:
- `lodge show ITEM-1`: `current · author · … · fails check`, edited statement above her quote.
- `lodge search transcripts`: both the decision and its entry flagged (`fails check`, `decision fails check`).
- `lodge check`: `check 5: d-x0t21d: statement of a published decision was changed; a correction or a shorter reasoning is a new decision that replaces it`, exit 1.
- `lodge view --port 18793`, `curl /r/ITEM-1`: `fails check`; `/problems`: the same check 5 line; `/` (search): both rows flagged.
- `lodge check --gate`: exit 1, `check 5: working tree: …`, as before.
- A repository with no commits: `search`, `check`, `waiting` all fine (`published` empty, no crash).
- The post-tool-use hook does not use the read path; unaffected.

## 2. LODGE-10: answered

Agent decision `d-xez8gy` committed on `main`, then edited on a branch; `lodge check` exit 1 with `reasoning of a published agent decision was changed; a correction or a shorter reasoning is a new decision that replaces it` for a shrink, a grow, and a whitespace reflow (the old code accepted the shrink with a note).
The author decision's reasoning shrunk: `reasoning of a published author decision was changed; …`, exit 1.
Unedited state reads `ok`.
The remedy reads well for reasoning; see M1 for the statement case.
`src/lodge/core/check_immutable.py:11-28` compares every field but `id`; the shrink note and its plumbing in `check_change.py` are gone.

## 3. Revert-and-run: answered

- Read path reverted (`read_checked` returns `read_state` at once): 7 tests fail, among them `tests/viewer/test_pages.py::test_hand_edited_published_decision_fails_on_its_page_and_in_problems` (fails at `assert "fails check" in pages.record_page(...)`, `test_pages.py:236`), so that test does test the fix although the builder never saw it fail.
  The others: `test_reads.py::test_check_gate_compares_with_the_published_state`, four in `test_reads_published.py`, `e2e/test_check_and_gate.py::test_check_and_gate`.
- `check_immutable.py` and `check_change.py` reverted to 1b958d6: 24 failures across `tests/core/test_check_immutable.py`, `test_apply.py`, `app/test_writes.py`, `app/test_reads_published.py::test_a_shrunk_agent_reasoning_fails_on_a_read`.

## 4. `test_feedback_skips_edited_decisions_which_the_check_refuses`: point kept

Mutation: dropping `and record_id not in before.decisions` from `_written` (`src/lodge/app/writes.py:205`) makes the test fail (`d-cccccc` appears in the feedback), so it still tests that feedback skips an edited decision.
The over-length statement of `d-cccccc` (100 words against 80) is what would be noted, and the edited reasoning is applied before the check refuses it.
The assertions `CHECK_FAILED` and `[5]` are correct for the new rule.
The name states the new fact.

## 5. `sh scripts/check.sh`

Exit 0 in my clone: 1071 passed, `lodge check --gate` `ok`.

## Findings

**M1 Minor.** The remedy text for non-reasoning fields mentions reasoning.
Handle: `src/lodge/core/check_immutable.py:12` (`REMEDY`), appended to every check 5 message.
Scenario: a hand-edited statement prints `statement of a published decision was changed; a correction or a shorter reasoning is a new decision that replaces it`; "a shorter reasoning" has no bearing on a statement, quote, or link edit.
Fix: keep the spec's wording (spec, The check item 5 uses it) but add it only to the reasoning message, with `; a correction is a new decision that replaces it` for the other fields; `tests/core/checks.py` `REMEDY_CHECK_5` then needs two values.
Optional: the spec text itself puts the phrase in the item, so leaving the code as is is defensible.

## Noted, not findings

- `_written`'s "edited decision is left out" branch is now reachable only on a refused add, because any edit of a decision either fails check 5 or changes nothing (`AddOutcome.UNCHANGED`); the guard and its test are harmless.
- Branch-mode reads after a rewrite are not covered by an e2e test (the builder said so); not probed here, out of scope for the two decisions.
