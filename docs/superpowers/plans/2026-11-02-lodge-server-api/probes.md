# Probes for the server-api plan

Run on 2026-11-02 with Bun 1.3.14, in scratch folders holding the files in `probes/` (with `bun install`), or in a scratch copy of `ts/` at `a73a148` with `bun install --frozen-lockfile`; outputs are quoted as printed.
The plan cites them as "probe N"; "plan 1, probe N" is an item of `../done/2026-11-02-lodge-server-core/probes.md`, where plan 1's folder is once plan 1 has merged.

1. `bun toml.ts` (`probes/toml.ts`, smol-toml 1.9.1 with `integersAsBigInt: true` beside `Bun.TOML.parse`), each case as the text, then what each parser gives:
   `title_chars = 80.0` under `[length]`: Bun.TOML `number 80`, smol-toml `number 80`;
   `title_chars = 80`: Bun.TOML `number 80`, smol-toml `80n` (a `bigint`);
   `title_chars = 0x50`: Bun.TOML `number 80`, smol-toml `80n`;
   `8e1`, `length = {title_chars = 80.0}`, and `length.title_chars = 80.0`: `number 80` from both;
   `title_chars = 99999999999999999999`: Bun.TOML `number 100000000000000000000`, smol-toml `99999999999999999999n`;
   `title_chars = inf`: Bun.TOML the text `"inf"`, smol-toml `number Infinity`;
   `[store` with no closing bracket: Bun.TOML `{"store":{}}`, smol-toml `error: Invalid TOML document: illegal character in key` (its first line; the message goes on over several lines).
   So with `integersAsBigInt`, smol-toml gives every TOML integer as a `bigint` and every TOML float as a `number`, and Bun.TOML.parse accepts a table header with no closing bracket.
2. The same cases under lodge 0.2 (`uv run --frozen python`, `tomllib`): `80.0` and `inf` are `float`, `99999999999999999999` is `int`, and `[store` raises `Expected ']' at the end of a table declaration (at line 1, column 7)`; in a fresh repository whose `.lodge.toml` is `[length]` and `title_chars = 80.0`, `lodge search x` prints `lodge: .lodge.toml: length.title_chars must be a positive whole number` and exits 2.
3. Text imports through the gate (`probes/text-import/`, copied into the scratch copy of `ts/` with `"#api": "./src/api/index.ts"` added to `package.json`'s `imports`):
   `import bundle from "./page.html" with { type: "text" }` is typed `HTMLBundle` by `bun-types` (`node_modules/bun-types/extensions.d.ts` declares `*.html`), so `tsc` reports `TS2322: Type 'HTMLBundle' is not assignable to type 'string'` until the value is cast (`bundle as unknown as string`), and a declaration of my own for `*.html` collides with Bun's (`TS2309`);
   `import script from "./page.js" with { type: "text" }` type-checks with `declare module "*/page.js" { const text: string; export default text; }` in `src/api/text.d.ts`;
   with both, `biome check --error-on-warnings`, `tsc --noEmit`, `depcruise src tests` (`no dependency violations found (64 modules, 145 dependencies cruised)`), `knip`, and `bun test tests/api-probe.test.ts` (`2 expect() calls`, 0 fail) pass;
   Biome lints the HTML file (`useHtmlLang` failed until `<html lang="en-GB">`) and the script;
   a binary from `bun build --compile` of a file printing the two texts prints `string 160 95` after `page.html` is moved away.
4. knip 6.42.0 with `--include-entry-exports` on the scratch copy of `ts/` at `a73a148`: `Unused exports (8)`, among them `LookupError` of `src/core/errors.ts` and `THREADS` of `src/core/threads.ts`, and `Unused exported types (3)`; with `/** @public */` above `export class LookupError`, `Unused exports (7)` and `LookupError` is no longer named.
5. `bun build --compile client.ts --outfile client-bin` (`probes/client.ts`, a `fetch` of `POST /api/v1/echo` printing the status, a header, and the body): 0.25 seconds by `date` before and after, 94,582,912 bytes.
   `bun serve-binary.ts` (`probes/serve-binary.ts`: `Bun.serve` on `127.0.0.1` port 0, then the binary run with `Bun.spawn` and `env` holding only `PATH`): `async spawn: 0 200 0.3.0 {"a":"é😀"}`.
   The same binary run with `Bun.spawnSync` from the process that serves never returns (killed by `timeout 20`), since the synchronous spawn blocks the loop the server answers on.
6. lodge 0.2's usage errors, run in a scratch repository (`uv run --frozen --quiet lodge …`), each exiting 2:
   `lodge search x --status gone` prints the usage, then `lodge search: error: argument --status: invalid choice: 'gone' (choose from current, replaced, retired, any)`;
   `lodge id x` prints `usage: lodge id [-h] {d,s}`, then `lodge id: error: argument prefix: invalid choice: 'x' (choose from d, s)`;
   `lodge add` prints `usage: lodge add [-h] [--import] [--dry-run] [--attach PATH] FILE [FILE ...]`, then `lodge add: error: the following arguments are required: FILE`;
   `lodge` alone prints `usage: lodge [-h] [--version] COMMAND ...`, then `lodge: error: the following arguments are required: COMMAND`;
   `lodge search x --limit 0` prints the usage, then `lodge search: error: argument --limit: '0' is not a positive whole number`.
7. Publication dates on npm (`npm view <package> time`), for the rule that a pinned version is at least two weeks old (d-4psbdv): smol-toml 1.9.1 2026-10-09, @simplewebauthn/server 14.0.3 2026-09-25 (plan 1, probe 11).
8. lodge 0.2 on a hand-written decision by `author` with no quote (fix round 1), in a scratch repository (`git init -b main`, `lodge init`, then the seed of `tests/e2e/support.py` added and committed):
   writing `lodge/decisions/<id>-unquoted.md` with `id`, `kind: decision`, `title: Unquoted`, `scope: product`, `decided_by: author`, `date: 2026-10-29T12:00:00+01:00`, and the body `Unquoted statement.`, then `lodge check` prints `check 3: <id>: decided_by is author, but there is no quote; add quote: {text, where, when} with the author's words, or record it under your own role` and exits 1, and `lodge show <id>`'s first line ends `· fails check`;
   with that file committed to `main`, so that the published state holds it as the server's does, `lodge check --gate` prints `ok`, then `note: already published, check 3: lodge/decisions/<id>-unquoted.md: <id>: decided_by is author, but there is no quote; …`, and exits 0.
   Editing the seeded decision's `decided_by` instead, uncommitted, gives `check 3: ` and then `check 5: <id>: decided_by of a published decision was changed; …`, and the gate fails on both; on the server check 5 cannot fire and the store refuses the rewrite (d-pmaw3a).
