# Task 8 review (Sonnet checkpoint, range `372b49d..65030ce`)

0 Blocking, 1 Important, 3 Minor.

## Important

- I-1: a statement-level `/** @public */` tag on a re-export block masks every name in it (`ts/src/core/index.ts:4,27,50,59,75`, `ts/src/api/index.ts:4`).
  Probe: `export const ZZZ_UNREAD` added to `confirmation.ts` and listed in the tagged block at `index.ts:4`; `bunx knip` exited 0 and reported nothing, so d-amxk94's removal of an unread export is no longer enforced for those blocks (nor for `issueSetupCode`, `ServerIo`, `serverCommand` in the `#api` block).
  Fix: tag only the specifier (`/** @public */` on its own line before `MINUTE_FORMAT,` inside the block); probed: `ZZZ_UNREAD` was then reported and `MINUTE_FORMAT` stayed silent.

## Minor

- M-1: double tagging (`confirmation.ts:14`, `views.ts:138`, `model.ts:7,26,31`, `order.ts:6`, `render.ts:8`, `setup.ts:5`); with all definition tags removed knip reports only `THREADS`, `Files`, `HeldMessage`, so the other eight definition tags do nothing.
- M-2: `listen` has no force path (`ts/src/api/serve.ts:18-30`); with a 3 s in-flight request, SIGTERM then SIGINT resolved after 2914 ms, the second signal swallowed. Fix: on a repeated signal call `server.stop(true)`.
- M-3: `listen` throws synchronously on EADDRINUSE (`serve.ts:7`) although typed `Promise<void>`; the compiled binary printed `serving ...` then a Bun stack trace, exit 1; an unopenable `--data` path does the same; `main.ts` has no catch and the plan did not require one.

## Sound

`environment.test.ts` fails under both mutations; `bunx knip` exits 0; `main.ts` awaits `openDatabase`, `ApiOptions` carries the real clock, `crypto.getRandomValues`, the version, `log: err`; build script verbatim; `knip.json`, parity rows; binary `--version` gives `lodge 0.3.0`, setup and serve work, SIGTERM exits 0; handlers return to 0 after shutdown; every tagged name justified; removed names not imported by `origin/server-import`; no socket in the gate; binary test inherits `PATH` alone and leaves no temporary folder; `.gitignore` line redundant (existing `dist/`).
