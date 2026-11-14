# Task 12c, fix round 1 report

Implemented I-1, I-2 and M-1 through M-5.

- Added the relayed-close approval test. It checks the held close operation, null text, thread ID and about, the open state before approval, and the closed state, empty message, preserved place and cleared waiting afterwards.
- Asserted reply and close held IDs and about, plus one provisional q- ID and about for a held ask.
- Removed the top-of-loop open-hold read. The last-rejection test retains the NotFound behaviour and asserts four reads: authorisation and one for each of three rejected attempts.
- Narrowed authorisation by the expected hold kind, removing the unreachable add-refresh throw.
- Extracted holdMessage. threads.ts is 242 lines and held.ts is 62 lines.
- Replaced the waiting-test loop with two plain tests, replaced the setup boolean with the opening speaker, and made relay return held as a number. Approval now exercises mail as well as chat.

## Test-first evidence

Before the production refactors, each of M1, M2, M3, M14 and M25 failed the new close test. M5 and M6 failed the reply, ask and close answer assertions. Each mutation was applied separately and restored after its failing run.

The changed approval-place assertions also failed M10 and M17 when the respective place was replaced with the constant chat. Restoring the redundant top-of-loop read failed the strengthened last-rejection test. The two waiting tests retain the previous behavioural assertions as separate tests.

## Conditional findings

M-6: title-style refs are unsupported. core/search.ts resolve accepts record IDs and exact record codes, not titles. A trial using the existing entry title, Transcripts are kept, returned NotFound. The final ask test retains the supported ID ref and asserts that the hold stores that resolved ID.

M-7: no existing message fixture was found where the check passes at hold time and fails at approval. The existing held-add approval fixture retires an entry required by a new dependent spec; approving a message does not introduce that dependency. No new fixture was introduced, as requested. This conditional coverage gap remains.

## Validation

sh scripts/check-ts.sh passed: Biome, TypeScript, dependency-cruiser and knip clean; 1286 tests passed, 2 todo, 0 failed. No dependency added.
