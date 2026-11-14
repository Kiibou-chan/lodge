# Task 12b fix round 1 report

Completed I-1 and M-1 to M-5. M-6 and M-7 remain for plan 3.

The payload test holds an add carrying an attachment, checks the stored attachments,
importing flag and message, then approves it and checks the published attachment
path, text and message. It runs with importing both false and true. The expected
message comes from publishing the same drafts directly as ada.

Added coverage for two holds in ascending seq order, the literal HELD wire value,
bo declining with a blank reason receiving Forbidden, and a person drafter being
recorded as bo. The retry test settles the hold after the first rejected publish
and asserts NotFound with exactly one publish attempt.

Approval now uses the already authorised wiring. Each retry still checks that the
hold is open, but no longer re-parses immutable drafts or rebuilds the request.
Removed the unreachable approval clause from the UNCHANGED guard.

## Mutation evidence

Tests were added before the production changes. Each mutation was applied alone,
the relevant test was observed failing, and the production file was restored.
All eight were repeated against the final changes before the full gate.

| Mutation | Observed failing assertion |
| --- | --- |
| M16: store attachments as [] | Held payload differs from the supplied attachment pairs, both importing cases |
| M17: store importing as false | Held importing differs from true |
| M18: store message as empty | Held message differs from the direct publication message |
| M26: reverse held() | Seq list differs from insertion order |
| M30: change HELD to "held" | Literal differs from "held for approval" |
| N03: validate reason before authorisation | Wrong person's blank decline raises LodgeError instead of Forbidden |
| N05: record every drafter as agent | Person drafter differs from bo |
| M15: remove the per-attempt open-check | Publish attempts are 3 instead of 1 |

M-4 and M-5 remove equivalent or unreachable code and need no new tests.

## Validation

`sh scripts/check-ts.sh` passed: Biome, TypeScript, dependency-cruiser, knip,
and 1271 passing tests, 2 todo, 0 failures. The initial gate caught formatting
and a nullable test expectation; these were corrected before the successful run.
`git diff --check` passed. Changed TypeScript modules are at most 254 lines.
No dependency was added. New text uses British English and contains no em-dashes.
