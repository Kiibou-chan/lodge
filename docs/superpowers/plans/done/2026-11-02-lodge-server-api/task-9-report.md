# Task 9 report

Implemented the person's page and its script, served directly through the handler without opening a socket.

## Files

- `ts/src/api/page.html`: added the en-GB page, its title, its single deferred external script, sign-in and registration controls, and signed-in sections for passkeys, tokens, and held approvals.
- `ts/src/api/page.js`: added JSON POST calls for the thirteen specified API operations, passkey buffer conversion in both directions, token issuance and revocation, and per-project held items.
  Held adds show parsed drafts, quotes, area introductions, or problems with raw text; held messages show their operation, reference, text, provenance, and time.
  Approval shows the published IDs, and declining requires a reason.
  Server content uses `textContent` and DOM elements.
- `ts/src/api/page.ts`: imported the two assets as text and exposed `PAGE` and `SCRIPT` inside the API package.
- `ts/src/api/text.d.ts`: added the plan's declaration for `*/page.js`.
- `ts/src/api/http.ts`: added only the GET routes for `/` and `/page.js`, with the plan's exact content types, no-store, nosniff, no-referrer, and content security policy.
- `ts/tests/api/page.test.ts`: added the seven specified tests, using the handler and an in-memory database.
- `ts/tests/api/handler.test.ts`: changed the obsolete GET `/` not-found fixture to `/missing`, with the coordinator's authorisation.
- This report records the changes, failures, mutations, and deviations.

The API front door gained no export.
The CLI, main, plan 4 files, and earlier briefs, reports, and reviews were not edited.

## Test-first evidence

Ran `cd ts && bun test tests/api/page.test.ts` before adding any page implementation.
It exited 1 with six failures and one pass.
Each first failing output is recorded below without local stack paths.

| Test | First failing output |
|---|---|
| `page_is_served_with_its_policy` | `expect(received).toBe(expected)`: expected `200`, received `404`. |
| `script_is_served_as_javascript` | `expect(received).toBe(expected)`: expected `200`, received `404`. |
| `other_paths_are_not_found` | Existing behaviour initially passed; before implementation, temporarily returned 200 for `/missing`: `expect(received).toBe(expected)`: expected `404`, received `200`. |
| `page_loads_only_its_script` | `expect(received).toHaveLength(expected)`: expected length `1`, received length `0`. |
| `script_writes_no_html` | `expect(received).toContain(expected)`: expected `textContent`, received the JSON not-found error. |
| `script_calls_only_the_api` | `expect(received).toBeGreaterThan(expected)`: expected `> 0`, received `0` fetch calls. |
| `every_operation_the_script_names_exists` | `expect(received).toEqual(expected)`: expected the thirteen operation names, received `[]`. |

The temporary not-found mutation was restored before implementation.
After implementation, the seven tests passed with 61 assertions.

## Required mutations

Each mutation ran its named test in isolation, exited 1, and was restored immediately afterwards.

| Mutation | Test and failing output |
|---|---|
| Changed the root GET route match to `/disabled`. | `page_is_served_with_its_policy`: expected `200`, received `404`. |
| Changed the script GET route match to `/disabled.js`. | `script_is_served_as_javascript`: expected `200`, received `404`. |
| Inserted a `document.body.innerHTML` assignment into the script. | `script_writes_no_html`: `expect(received).not.toMatch(expected)` failed against the prohibited HTML-writing pattern. |
| Changed the `me` fetch path to `/outside`. | `script_calls_only_the_api`: `expect(received).toMatch(expected)` failed because the fetch argument did not begin with a literal `/api/v1/<operation>` path. |

## Validation

`sh scripts/check-ts.sh` exited 0 after the mutations were restored.
Biome checked the HTML and JavaScript alongside the TypeScript with `--error-on-warnings`.
TypeScript, dependency-cruiser (253 modules and 937 dependencies), knip, and the structure tests passed.
The suite reported 1,576 passes, two todos, zero failures, and 4,104 assertions across 127 files.
The new script is 232 lines; every module remains within the 300-line limit.
No test opened a socket, no dependency was added, and no installation was needed.

## Deviations and coordinator rulings

The coordinator ruled that Task 5's GET `/api/v1/*` contract remains `400 use POST`.
Only other non-API GET paths remain `404 not-found`.
The coordinator authorised the single existing handler-test fixture change from `/` to `/missing`.

The exact plan filenames expose a TypeScript same-stem substitution absent from probe 3's wrapper in `index.ts`.
The first gate attempt reported `TS2613: Module .../api/page has no default export` for the text import of `./page.js` from `page.ts`.
The coordinator approved retaining the filenames, import, and declaration, adding one factual `@ts-expect-error` on that import, and assigning the imported value to `const SCRIPT: string`.
A subsequent gate caught Biome's required blank line before the export; formatting it resolved the error.

Browser passkey and compiled-binary coordinator checks were not run as part of this socket-free task.
