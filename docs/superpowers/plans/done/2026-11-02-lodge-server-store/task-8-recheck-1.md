# Task 8 recheck 1

Fix diff `11806a5..5d15e60`, run in a scratch worktree at `5d15e60` (removed).
`sh scripts/check-ts.sh` there: green, 1129 pass, 0 fail.

1. Answered: `ts/tests/app/fakes.ts:60` filters on `ATTACHMENTS`; `ts/tests/store/interleaving.test.ts:46` guards the fake; the SQLite probe at `interleaving.test.ts:54-64` asserts the attachment is absent from `trees().files` and present in `files()` and `attachmentTexts()`. Mutation reruns: dropping `attachmentTexts()` from `Interleaving.files()` (`interleaving.ts:63`) gives 1 fail; forwarding an empty map (`interleaving.ts:13`) gives 2 fail.
2. Answered differently but adequately: `wal.test.ts:47` drives the throw at `schema.ts:65` through `openDatabase("")`; deleting the throw gives 1 fail. It does not cover a contended open past the timeout, which was the review's scenario, but the branch is now guarded.
3. Answered: `interleaving.test.ts:68` expects the rejection; removing the throw at `interleaving.ts:68` gives 1 fail.
4. Answered: `knip.json` entry removed, gate green.
5. Open as a Minor, not a block: the plan (`2026-11-02-lodge-server-store.md:390`, the only WAL mention) says the store sets WAL and does not require refusing other paths; the refusal is the brief's own m-2 fix and stays reasonable. The new test pins `openDatabase("")` as refused, which now makes that policy a tested contract; if a later task wants a temporary database it must change that test.

New problems: none Blocking or Important.

Verdict: 0 Blocking, 0 Important, 1 Minor
