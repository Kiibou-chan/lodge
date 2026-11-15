# Recheck brief: Task 9 fix round 1 of `docs/superpowers/plans/2026-11-02-lodge-server-import.md`

Read-only recheck of fix commit `404b926` (range `d122542..404b926`) on `server-import-hook` in `/var/tmp/lodge-import-hook`; read `CLAUDE.md`, `task-9-fix-1-brief.md`, `task-9-fix-1-report.md`.
Check each finding is answered, mutating a disposable copy under `mkdtemp`, never the lane: I-1 (`lodge hook -h` and `lodge hook x -h` byte for byte against `uv run --frozen --quiet lodge hook -h` and `lodge hook x -h`, stdout, stderr, exit code; compare with the TS `bun run ts/src/main.ts hook -h`); I-2 (replacing `readExact` in `hook-context.ts` with a lenient read fails a test); M-a (`lodge -h` and `lodge nosuch` ordering against lodge 0.2); M-b (identity `resolvePath` or `null` cwd in `main.ts` fails a test); M-c; M-e (the `table()` reuse and the moved-advice assertion with the reversal warning removed).
Report any new defect the round introduced (Important or Minor with file, line, probe). Edit nothing in the lane.
Final message: findings, or "0 Important, 0 Minor".
