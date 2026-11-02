# Planner report: plan 2, the events store and the operations

Status: plan written, eleven rulings recorded; self-review pass next.

## Done

- Read the brief, plan 1 (Global Constraints, Calls made, the rest of build step 1, Settled for the later plans, the parity table), its ledger, the design, `src/lodge/app`, `tests/app`, and `tests/gitstore/test_concurrent.py`.
- Probes 1 to 8 (`probes.md`): a `text` column loses a leading U+FEFF and corrupts lone surrogates, so file texts go in `blob`s; Kysely serialises transactions on one connection; a read-then-write transaction across two connections fails, a compare-and-set first statement does not; the app's default-filling functions; an edit of a decision through `add` is refused by check 5.
- First draft: 14 tasks, lanes A (app, Tasks 2 to 6), B (store, Tasks 7 and 8), and C (core people and flags, Tasks 10 and 13).

## Rulings

d-59q4jc (asynchronous ports), d-ae1vn5 (the port's shape), d-wje1cn (events and the compare-and-set), d-vd3175 (options objects), d-t7er56 (lanes), d-rp74dr (thread fix paths), d-kj59bz (people), d-znagqe (held drafts), d-4spcem (flags per person), d-fv20kp (the check on every write), d-wx7d0f (projects); `lodge check` ok.

## Open

- A self-review pass over the plan against the brief and plan 1.

## Concerns

- The parity table marks only two app test files as changed, but four more carried files test the staged mode, commits, and the labelled gate (`tests/app/test_reads.py:149-195`, `test_confirm.py:90-178`, `test_thread_ops.py:163-181`, `test_writes.py:126-136`, `test_writes_dates.py:50-54`); the plan keeps the port's shape so they carry unchanged over the fakes (RULING-PORT).
- `tests/app/test_thread_fix_paths.py` imports the command (`lodge.cli`), which plan 3 ports; two of its tests wait for plan 3 (RULING-FIXPATHS).
