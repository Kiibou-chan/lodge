# knip and the entry list

Run in this folder after `bun install`, with `knip.json` set to each of the four configurations below (`project` always `["src/**/*.ts", "tests/**/*.ts"]`), then `bun --bun x knip --no-progress`.
`src/core/confirmation.ts` exists only for C and D; for A and B, delete it and its line in `src/core/index.ts`.

- A: `entry` `["tests/**/*.test.ts"]`.
- B: `entry` `["tests/**/*.test.ts", "src/core/derive.ts", "tests/core/helpers.ts"]`.
- C: `entry` `["tests/**/*.test.ts", "tests/core/helpers.ts"]`.
- D: `entry` `["tests/**/*.test.ts"]`.
