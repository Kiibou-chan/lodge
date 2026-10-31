# Recheck of the final fix wave (8308db4 to 1d798e8)

Counts: 12 closed, 0 open, 0 new Blocking, 0 new Important.

Rechecker: the `rechecker` agent; no scratch worktree was needed, probes were reads and targeted tests in the branch worktree.

## Findings

- Final I1 closed: `lodge spec` prints the new s-2bzwzv sentence (last same-area dependency, "also rests on", cross-area line); d-azeks4 reasoning names d-a3h9f3.
- 9b/9c I1 closed: `lodge show d-vme42w` and `lodge show d-x42f0x` both read "narrowed by d-azeks4"; the reasoning keeps d-2hcgav and the local, command-line, and listed-reads claims.
- 9b/9c I2 closed: `lodge spec` line 189 "The three record kinds", line 333 "the eight checks" (`lodge/spec/model/_area.md:8`, `lodge/spec/writing/_area.md:8`).
- 9b/9c I3 closed: `lodge/decisions/d-68b0j2-…md` and `d-6zyet3-…md` gain the four missing reasons (append-only messages, doubt shown where she reads, entries only rested on, link floods nothing and clears nothing).
  Both decisions are absent from `main` (`git ls-tree -r main`), so amending them through `lodge draft` is within d-38xscb.
- m2 closed: `tests/gitstore/test_commit.py:94-95` is parametrised over `rebase-merge`, `rebase-apply`, and `sequencer`; the 65 targeted tests pass.
- m3 closed: s-mc9n8a now names revert and a stopped sequence, with Call 25 in d-azeks4.
- m4 closed: s-r7c3wn separates "changed by d-xxxxxx, in doubt" from "rests on s-xxxxxx, in doubt", matching `src/lodge/core/doubts.py`.
- m5 closed: `lodge/spec/writing/s-j5ttw1-…md` has `rests_on: [s-aq3a5k]` through a `link` change in d-azeks4; `lodge check --gate` is ok and `lodge spec` has no "rests on …, changed since" mark (the two grep hits are prose of s-… on lines 247 and 560).
- m7 closed: d-3d4g9j reasoning says "built".
- m10 closed: `src/lodge/viewer/forms.py:28-33` pluralises for more than one ID; `tests/viewer/test_forms.py` pins both forms.
- m11 closed: `CLAUDE.md:8` and `CLAUDE.md:33` name both designs.
- Task 6b parked m5 closed: `src/lodge/viewer/writes.py` splits `handle_post` into `_parse_form` and `_Post` methods.

## handle_post order

The order is unchanged.
`_parse_form` runs `refuse_early` first, then the body and field checks and the token compare, all before `make_lodge()` and `_LOCK` (`writes.py:87-111`, `175-196`).
Inside the lock: confirm validates IDs, sets `back`, treats `StaleList` as a 303 with `done=stale`, and computes `done_code` before the CHECK_FAILED refusal, as before.
Threads: `ask` and `reply_or_close` keep the old order (about, back, kind, write; thread lookup before `back`, so a `NotFound` there still backs to `/`).
`back` for error replies is `post.back` once `_Post` exists, otherwise `/`, equal to the old `back` variable at each raise point.
Any non-`/confirm`, non-`/threads` path still reaches the reply/close parser and answers 404 for a bad address.

## New problems

None Blocking or Important.
Note for the record (not a finding): the `lodge check --gate` notes about area rank, order, and intro changes are differences against `main`, as the report says.
