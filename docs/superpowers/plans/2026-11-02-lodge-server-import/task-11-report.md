# Task 11 report

## Task 11a

Task 11a records Constraints, The model, Export to git, and Moving from lodge 0.2.
It adds 27 entries, edits seven entries, and records four section decisions plus the coordinator-approved dependency completion decision.
All record writes go through a successful dry run and then `uv run --frozen --quiet lodge add`.
No implementation or permanent test files change.

### Files and design coverage

Design handles below refer to `docs/superpowers/specs/2026-11-02-lodge-server-design.md`.
Each entry is one paragraph, at most 150 words, with present-tense claims and explicit future build steps.
Existing record filenames retain their original slugs when titles change.

| file:line | Decision | Design lines | Change |
|---|---|---|---|
| lodge/decisions/d-7s8k61-constraints-for-lodge-and-its-typescript.md:1 | d-7s8k61 | 52-62 | Constraints for lodge and its TypeScript server; coordinator, product scope, number handles, source rulings, and section reasons. |
| lodge/spec/constraints/s-a4jfp1-lodge-is-written-in-python.md:1 | d-7s8k61 | 55 | Edit: Python lodge and the TypeScript server. |
| lodge/spec/structure/s-v1sb0j-the-environment-is-reproducible-with-uv.md:1 | d-7s8k61 | 55, 59 | Edit: Python and TypeScript environments are reproducible. |
| lodge/spec/structure/s-165qfh-a-structure-test-enforces-the-import.md:1 | d-7s8k61 | 58 | Edit: Structure tests enforce Python and TypeScript boundaries. |
| lodge/spec/structure/s-3xka4c-static-analysis-is-strict-and-pinned.md:1 | d-7s8k61 | 58-59 | Edit: Static analysis is strict in both environments. |
| lodge/spec/constraints/s-sb9gee-server-storage-uses-sqlite-through-a.md:1 | d-7s8k61 | 56 | Create: Server storage uses SQLite through a typed port. |
| lodge/spec/constraints/s-gcwv38-the-full-interface-uses-preact-and.md:1 | d-7s8k61 | 57 | Create: The full interface uses Preact and signals. |
| lodge/spec/constraints/s-5fd1qs-carried-python-tests-specify-the-server.md:1 | d-7s8k61 | 59 | Create: Carried Python tests specify the server behaviour. |
| lodge/spec/constraints/s-7cseam-the-cloud-runner-supplies-a-pseudo.md:1 | d-7s8k61 | 60 | Create: The cloud runner supplies a pseudo-terminal. |
| lodge/spec/constraints/s-t8sj11-cloud-sessions-require-a-public-server.md:1 | d-7s8k61 | 61 | Create: Cloud sessions require a public server name. |
| lodge/spec/constraints/s-51ab7j-cloud-identity-comes-from-a-checked.md:1 | d-7s8k61 | 62 | Create: Cloud identity comes from a checked session ID. |
| lodge/decisions/d-sk1r7r-the-server-model-preserves-records-in.md:1 | d-sk1r7r | 64-94 | The server model preserves records in append-only events; coordinator, product scope, number handles, source rulings, and section reasons. |
| lodge/spec/purpose/s-07ar34-no-server-and-no-mcp-server.md:1 | d-sk1r7r | 66-72 | Edit: lodge 0.2 is serverless and the server exists. |
| lodge/spec/storage/s-z1zvb4-records-are-markdown-files-in-git.md:1 | d-sk1r7r | 66-72 | Edit: Records live in git files or server events. |
| lodge/spec/constraints/s-j8tp0n-files-in-git-are-the-only.md:1 | d-sk1r7r | 66, 72; 282 | Edit: The active store is the source of truth. |
| lodge/spec/model/s-31atpc-server-records-preserve-their-existing-meanings.md:1 | d-sk1r7r | 67-72 | Create: Server records preserve their existing meanings. |
| lodge/spec/model/s-ava922-a-decision-names-its-deciding-person.md:1 | d-sk1r7r | 74 | Create: A decision names its deciding person or agent role. |
| lodge/spec/model/s-yenn11-a-person-approves-decisions-drafted-in.md:1 | d-sk1r7r | 75-76 | Create: A person approves decisions drafted in their name. |
| lodge/spec/model/s-wb086g-only-the-deciding-person-clears-their.md:1 | d-sk1r7r | 77 | Create: Only the deciding person clears their review flag. |
| lodge/spec/model/s-e5rrwm-the-server-checks-writes-against-its.md:1 | d-sk1r7r | 79 | Create: The server checks writes against its current state. |
| lodge/spec/model/s-fabgyh-accepted-records-are-current-without-a.md:1 | d-sk1r7r | 80-81 | Create: Accepted records are current without a branch merge. |
| lodge/spec/model/s-g8m3qv-a-project-groups-its-records-and.md:1 | d-sk1r7r | 85 | Create: A project groups its records and export target. |
| lodge/spec/model/s-tprwhs-a-workflow-defines-a-project-task.md:1 | d-sk1r7r | 86 | Create: A workflow defines a project task's steps. |
| lodge/spec/model/s-d1dd20-tasks-group-work-and-allow-one.md:1 | d-sk1r7r | 87-89 | Create: Tasks group work and allow one level of children. |
| lodge/spec/model/s-8v6ek2-a-session-reports-agent-work-on.md:1 | d-sk1r7r | 90 | Create: A session reports agent work on a task. |
| lodge/spec/model/s-cf0qph-artefact-uploads-are-versioned-task-attachments.md:1 | d-sk1r7r | 91-92 | Create: Artefact uploads are versioned task attachments. |
| lodge/spec/model/s-nfgv2t-waiting-items-ask-a-person-for.md:1 | d-sk1r7r | 93 | Create: Waiting items ask a person for an answer or go. |
| lodge/spec/model/s-c0bd0b-a-person-signs-in-with-passkeys.md:1 | d-sk1r7r | 94; 304 | Create: A person signs in with passkeys. |
| lodge/decisions/d-tnpe08-export-to-git-is-a-one.md:1 | d-tnpe08 | 280-285 | Export to git is a one-way copy of server records; coordinator, product scope, number handles, source rulings, and section reasons. |
| lodge/spec/storage/s-f6eaj1-export-copies-record-files-one-way.md:1 | d-tnpe08 | 282-284 | Create: Export copies record files one way to git. |
| lodge/spec/storage/s-20dnpp-export-writes-a-dedicated-branch-safely.md:1 | d-tnpe08 | 282-284 | Create: Export writes a dedicated branch safely. |
| lodge/spec/storage/s-b4dtqk-export-batches-writes-within-each-server.md:1 | d-tnpe08 | 285 | Create: Export batches writes within each server run. |
| lodge/spec/storage/s-b6jxhr-export-names-the-person-who-decided.md:1 | d-tnpe08 | 284; 78 | Create: Export names the person who decided or wrote. |
| lodge/decisions/d-jtbrh6-moving-from-lodge-0-2-preserves.md:1 | d-jtbrh6 | 287-290 | Moving from lodge 0.2 preserves records and redirects advice; coordinator, product scope, number handles, source rulings, and section reasons. |
| lodge/spec/storage/s-txrm4h-the-owner-imports-a-store-into.md:1 | d-jtbrh6 | 289 | Create: The owner imports a store into an empty project. |
| lodge/spec/storage/s-5sgcxx-import-checks-the-original-and-mapped.md:1 | d-jtbrh6 | 289 | Create: Import checks the original and mapped states. |
| lodge/spec/storage/s-yaz279-import-changes-only-author-attribution.md:1 | d-jtbrh6 | 289; 78 | Create: Import changes only author attribution. |
| lodge/spec/storage/s-3cagcv-the-hook-redirects-moved-projects-to.md:1 | d-jtbrh6 | 290 | Create: The hook redirects moved projects to the server. |
| lodge/decisions/d-mgtnf5-link-the-server-object-definitions-to.md:1 | d-mgtnf5 | 85, 87, 90-93 | Link sessions and artefacts to tasks, waiting items to people, and projects to their event store; statements stay unchanged. |
| lodge/spec/constraints/_area.md:1 | Section adds | Section entries above | Include the new entries in the existing area order. |
| lodge/spec/model/_area.md:1 | Section adds | Section entries above | Include the new entries in the existing area order. |
| lodge/spec/storage/_area.md:1 | Section adds | Section entries above | Include the new entries in the existing area order. |
| docs/superpowers/plans/2026-11-02-lodge-server-import/task-11-report.md:1 | Report | Task 11a | Record changes, red-first checks, commands, deviations, and follow-up work. |

Design line 54 reuses s-fk3yzy, the public-repository constraint; this task follows that boundary in every file.
The model's author mapping at line 78 is covered by s-yaz279 and s-b6jxhr rather than duplicated in another entry.
The design's immutable-record sentence at line 67 preserves immutable decisions and event history; it does not revoke specification-entry editing.
The viewer changes in d-3d4g9j and d-dyrpc6 remain intact.

### Changed sentences

`s-a4jfp1`: lodge is written in Python.
The replacement statement is:

> lodge 0.2 is written in Python.
> The server, the runner, the interface, and the `lodge` command of the server design are written in TypeScript.
> The command ships as a single binary built with `bun build --compile`; from build step 4, the runner ships the same way.

`s-v1sb0j`: Python 3.12 or later is required; the uv environment and Python dependencies were the entire stated environment.
The replacement statement is:

> lodge 0.2 requires Python 3.12 or later.
> `pyproject.toml` and `uv.lock` are committed, so a fresh clone reproduces the Python environment with `uv sync`.
> Python runtime dependencies stay limited to PyYAML, and its viewer uses the standard library's HTTP server.
> The TypeScript environment sits beside it: Bun 1.3.14 runs the server, tests, and tools, with dependencies pinned in `ts/package.json` and `ts/bun.lock`.

`s-165qfh`: The structure test was described only through Python ast, with no module over about 300 lines.
The replacement statement is:

> The Python structure test uses the standard library's `ast`.
> The TypeScript structure tests use dependency-cruiser over the import graph and TypeScript's parser over calls.
> They enforce allowed imports, no module cycles, cross-package imports through front doors, and modules of at most 300 lines.
> `core` stays pure: time and randomness enter through ports, and clock, randomness, file, and network calls are refused.

`s-3xka4c`: Only Ruff, Vulture, and strict mypy were listed.
The replacement statement is:

> Python uses Ruff for linting and formatting, mypy in strict mode, and Vulture with a pinned allow-list; unused imports and variables fail the gate.
> The TypeScript gate uses Biome for linting and formatting, `tsc` in strict mode, and knip for unused code.
> Warnings fail the gate.
> Configuration and dependencies are pinned in each environment.

`s-07ar34`: There is no server for now: lodge starts serverless; a shared server is the later ideal, with Kotlin a candidate.
The replacement statement is:

> lodge 0.2 has no server and no MCP server.
> The TypeScript server of the server design exists from build step 1, holding records and serving the API.
> Its storage stays behind a port.
> This does not undo the viewer's existing confirmation and thread writing.

`s-z1zvb4`: Records are files in git, one record per file, behind one storage interface so that a server can replace it later.
The replacement statement is:

> lodge 0.2 keeps records as Markdown files with YAML headers in git, one record per file, behind a storage interface.
> On the server, records live as events in one append-only SQLite table.
> Each event that writes a record holds its path and file bytes; other tables are derived from events and can be rebuilt.

`s-j8tp0n`: Files in git are the only source of truth; a project's knowledge lives in its repository.
The replacement statement is:

> For a project on lodge 0.2, files in its git repository are the source of truth, and any index is disposable.
> For a project on the server, its events are the source of truth, and derived tables can be rebuilt.
> The export to git is a one-way copy that the database never reads back.

### Narrowed decisions

| Decision | Narrowing and retained meaning |
|---|---|
| d-zq5sfb | d-7s8k61 narrows Python as the universal language, and d-sk1r7r narrows git as the universal source of truth; public-repository and prose rules remain. |
| d-jxwj8m | d-7s8k61 adds the TypeScript toolchain alongside the Python environment; the Python checks remain. |
| d-cg3nn3 | d-sk1r7r narrows the absence of a server and Kotlin as a future server candidate; lodge 0.2 stays serverless, and the existing viewer narrowings remain. |
| d-a3e8kb | d-sk1r7r narrows universal file-based storage; lodge 0.2 files, their header format, and checkout settings remain. |

No author decision is narrowed or replaced.
Related-decision feedback is answered no in each applicable decision's reasoning.
The export keeps d-khew4n, d-sk1r7r, and d-sj6hmf; the import keeps d-sdpcyb, d-va3j7x, and d-n9nm8h; the dependency completion keeps d-sk1r7r, d-j3z85y, and d-rn4qzq.

### Test-first evidence

The coordinator approves ignored acceptance scripts for this records-only task, with their first red output reported here.
No existing test is copied, modified, or weakened, and there is no implementation mutation.
The content script uses `Bun.spawnSync` to run `lodge show` for each entry and compares its title and full statement with the draft expectation.
Its first run precedes every section add and exits 1 with `0 passed; 34 failed; 34 acceptance checks`.
Its green run exits 0 with `34 passed; 0 failed; 34 acceptance checks`.

| file:line | Acceptance check | First failing output |
|---|---|---|
| .drafts/task-11a/verify-records.ts:9 | s-a4jfp1: title and complete statement | FAIL s-a4jfp1: Python lodge and the TypeScript server (old specification) |
| .drafts/task-11a/verify-records.ts:9 | s-v1sb0j: title and complete statement | FAIL s-v1sb0j: Python and TypeScript environments are reproducible (old specification) |
| .drafts/task-11a/verify-records.ts:9 | s-165qfh: title and complete statement | FAIL s-165qfh: Structure tests enforce Python and TypeScript boundaries (old specification) |
| .drafts/task-11a/verify-records.ts:9 | s-3xka4c: title and complete statement | FAIL s-3xka4c: Static analysis is strict in both environments (old specification) |
| .drafts/task-11a/verify-records.ts:9 | s-sb9gee: title and complete statement | FAIL s-sb9gee: Server storage uses SQLite through a typed port (entry absent) |
| .drafts/task-11a/verify-records.ts:9 | s-gcwv38: title and complete statement | FAIL s-gcwv38: The full interface uses Preact and signals (entry absent) |
| .drafts/task-11a/verify-records.ts:9 | s-5fd1qs: title and complete statement | FAIL s-5fd1qs: Carried Python tests specify the server behaviour (entry absent) |
| .drafts/task-11a/verify-records.ts:9 | s-7cseam: title and complete statement | FAIL s-7cseam: The cloud runner supplies a pseudo-terminal (entry absent) |
| .drafts/task-11a/verify-records.ts:9 | s-t8sj11: title and complete statement | FAIL s-t8sj11: Cloud sessions require a public server name (entry absent) |
| .drafts/task-11a/verify-records.ts:9 | s-51ab7j: title and complete statement | FAIL s-51ab7j: Cloud identity comes from a checked session ID (entry absent) |
| .drafts/task-11a/verify-records.ts:9 | s-07ar34: title and complete statement | FAIL s-07ar34: lodge 0.2 is serverless and the server exists (old specification) |
| .drafts/task-11a/verify-records.ts:9 | s-z1zvb4: title and complete statement | FAIL s-z1zvb4: Records live in git files or server events (old specification) |
| .drafts/task-11a/verify-records.ts:9 | s-j8tp0n: title and complete statement | FAIL s-j8tp0n: The active store is the source of truth (old specification) |
| .drafts/task-11a/verify-records.ts:9 | s-31atpc: title and complete statement | FAIL s-31atpc: Server records preserve their existing meanings (entry absent) |
| .drafts/task-11a/verify-records.ts:9 | s-ava922: title and complete statement | FAIL s-ava922: A decision names its deciding person or agent role (entry absent) |
| .drafts/task-11a/verify-records.ts:9 | s-yenn11: title and complete statement | FAIL s-yenn11: A person approves decisions drafted in their name (entry absent) |
| .drafts/task-11a/verify-records.ts:9 | s-wb086g: title and complete statement | FAIL s-wb086g: Only the deciding person clears their review flag (entry absent) |
| .drafts/task-11a/verify-records.ts:9 | s-e5rrwm: title and complete statement | FAIL s-e5rrwm: The server checks writes against its current state (entry absent) |
| .drafts/task-11a/verify-records.ts:9 | s-fabgyh: title and complete statement | FAIL s-fabgyh: Accepted records are current without a branch merge (entry absent) |
| .drafts/task-11a/verify-records.ts:9 | s-g8m3qv: title and complete statement | FAIL s-g8m3qv: A project groups its records and export target (entry absent) |
| .drafts/task-11a/verify-records.ts:9 | s-tprwhs: title and complete statement | FAIL s-tprwhs: A workflow defines a project task's steps (entry absent) |
| .drafts/task-11a/verify-records.ts:9 | s-d1dd20: title and complete statement | FAIL s-d1dd20: Tasks group work and allow one level of children (entry absent) |
| .drafts/task-11a/verify-records.ts:9 | s-8v6ek2: title and complete statement | FAIL s-8v6ek2: A session reports agent work on a task (entry absent) |
| .drafts/task-11a/verify-records.ts:9 | s-cf0qph: title and complete statement | FAIL s-cf0qph: Artefact uploads are versioned task attachments (entry absent) |
| .drafts/task-11a/verify-records.ts:9 | s-nfgv2t: title and complete statement | FAIL s-nfgv2t: Waiting items ask a person for an answer or go (entry absent) |
| .drafts/task-11a/verify-records.ts:9 | s-c0bd0b: title and complete statement | FAIL s-c0bd0b: A person signs in with passkeys (entry absent) |
| .drafts/task-11a/verify-records.ts:9 | s-f6eaj1: title and complete statement | FAIL s-f6eaj1: Export copies record files one way to git (entry absent) |
| .drafts/task-11a/verify-records.ts:9 | s-20dnpp: title and complete statement | FAIL s-20dnpp: Export writes a dedicated branch safely (entry absent) |
| .drafts/task-11a/verify-records.ts:9 | s-b4dtqk: title and complete statement | FAIL s-b4dtqk: Export batches writes within each server run (entry absent) |
| .drafts/task-11a/verify-records.ts:9 | s-b6jxhr: title and complete statement | FAIL s-b6jxhr: Export names the person who decided or wrote (entry absent) |
| .drafts/task-11a/verify-records.ts:9 | s-txrm4h: title and complete statement | FAIL s-txrm4h: The owner imports a store into an empty project (entry absent) |
| .drafts/task-11a/verify-records.ts:9 | s-5sgcxx: title and complete statement | FAIL s-5sgcxx: Import checks the original and mapped states (entry absent) |
| .drafts/task-11a/verify-records.ts:9 | s-yaz279: title and complete statement | FAIL s-yaz279: Import changes only author attribution (entry absent) |
| .drafts/task-11a/verify-records.ts:9 | s-3cagcv: title and complete statement | FAIL s-3cagcv: The hook redirects moved projects to the server (entry absent) |

The dependency checks are written and run after the coordinator identifies the missing links, but before their drafts are added.
Each reads `lodge show ID --provenance` and requires the named current dependency.
Their first run exits 1 with `0 passed; 4 failed; 4 dependency checks`.
Their green run exits 0 with `4 passed; 0 failed; 4 dependency checks`.

| file:line | Acceptance check | First failing output |
|---|---|---|
| .drafts/task-11a/verify-links.ts:5 | Required dependency | FAIL s-8v6ek2 rests_on s-d1dd20 (dependency absent) |
| .drafts/task-11a/verify-links.ts:5 | Required dependency | FAIL s-cf0qph rests_on s-d1dd20 (dependency absent) |
| .drafts/task-11a/verify-links.ts:5 | Required dependency | FAIL s-nfgv2t rests_on s-c0bd0b (dependency absent) |
| .drafts/task-11a/verify-links.ts:5 | Required dependency | FAIL s-g8m3qv rests_on s-z1zvb4 (dependency absent) |

### Commands and results

Inspection uses `cat`, `sed`, `nl`, and `rg` for repository guidance, the plan's required sections, the complete frozen server design, the named implementation modules, the toolchain, and gate scripts.
Records are read only with lodge, never by opening their files.
The inspection probes for absent size-glob and AGENTS files have no matches; the structure rules are found by content instead.
Draft preparation, area refreshes, and report generation use ignored scripts; each child process they start uses `Bun.spawnSync`.
No dependency is installed or added.

| Command or command family | Last line or outcome |
|---|---|
| `git status --short`; `git branch --show-current` at start | Clean; server-import-records. |
| `uv run --frozen --quiet lodge guide` | Exit codes: 0 done, 1 check failed or the store changed under you (add again), 2 usage or environment. |
| `uv run --frozen --quiet lodge waiting` | nothing, for agents and the author. |
| `lodge show ID --reasoning --provenance`; `lodge search`; `lodge draft REF`; `lodge add --help` | Read the consumed records, prior narrowings, related rulings, and draft format successfully. |
| `lodge search 'build order' --limit 100` | No server build-order entry; search matches other records by words. |
| `lodge id s` for each new entry | 27 unique entry IDs, used in the table above. |
| `bun .drafts/task-11a/prepare.ts`; `bun .drafts/task-11a/refresh-area.ts export` and `import` | Exit 0; refreshed storage order against each preceding section. |
| `lodge add --dry-run .drafts/task-11a/constraints/*.md` then add | dry run: nothing published; staged d-7s8k61 and its entries. |
| `lodge add --dry-run .drafts/task-11a/model/*.md` then add | dry run: nothing published; staged d-sk1r7r and its entries. |
| `lodge add --dry-run .drafts/task-11a/export/*.md`, repeated after answering feedback, then add | dry run: nothing published; staged d-tnpe08 and its entries. |
| `lodge add --dry-run .drafts/task-11a/import/*.md`, repeated after answering feedback, then add | dry run: nothing published; staged d-jtbrh6 and its entries. |
| `bun .drafts/task-11a/prepare-links.ts`; link dry run, repeated after answering feedback, then add | Exit 0; dry run: nothing published; staged d-mgtnf5 and its four links. |
| `lodge spec` after each section and the link add, filtered for changed since | Exactly the same two explanatory sentences, with no dependency warning. |
| `lodge show s-a4jfp1`; `lodge show s-07ar34` | Names TypeScript; states that the server exists from build step 1. |
| `uv run --frozen --quiet lodge check` | ok. |
| `bun .drafts/task-11a/verify-records.ts` | 34 passed; 0 failed; 34 acceptance checks. |
| `bun .drafts/task-11a/verify-links.ts` | 4 passed; 0 failed; 4 dependency checks. |
| `sh scripts/check.sh`, before and after the dependency completion | Both exit 0; 1,399 Python tests, 2,137 TypeScript tests, and no differential differences; the final run ends with `Ran 1 test across 1 file. [187.00ms]`. |
| `sh scripts/check-ts.sh`, last verification command | Exit 0; `Ran 2137 tests across 191 files. [11.55s]`, with 2,137 pass and 0 fail. |
| `git diff --cached --check` | Exit 0, no output. |

### Deviations, uncertainties, and follow-up

The coordinator approves the ignored red-first acceptance scripts, rather than adding permanent tests for live repository records.
The coordinator also approves d-mgtnf5 as an extra link-only decision after the four required section decisions; this completes dependencies without changing statements.
Full-access authorisation d-94tynf and this brief replace the plan's sandbox-only index workaround: lodge stages the real index, and this task commits and pushes its lane branch with the requested Codex trailer.
The model also narrows d-zq5sfb, because editing s-j8tp0n makes that decision's universal git-source claim false; the required Constraints narrowing alone covers its language claim.
No Coordinator-only rollout, merge, ledger, or later-task step is taken.

No build-order entry exists in the complete search results, so future claims name their build step without a build-order `rests_on`, as the brief permits.
Task 11c needs to link s-a4jfp1, s-gcwv38, s-7cseam, s-51ab7j, s-ava922, s-yenn11, s-g8m3qv, s-tprwhs, s-d1dd20, s-8v6ek2, s-cf0qph, s-nfgv2t, and s-c0bd0b to that entry once created.
Every step comes from the design's Build order: reporting and artefacts at step 2, the full interface at step 3, the runner at step 4, workflows and usage at step 5, code views at step 6, and several-person roles at step 7.
The design assigns no separate step to the Tailscale Funnel requirement, so s-t8sj11 states that deployment constraint without inventing one.

The pre-existing `grep -c 'changed since'` result stays 2.
Those matches are explanatory prose in s-7wbv0e and s-kba448, not freshness warnings, so their unchanged statements need no reaffirming decision.
The final full gate reads 451 records across 10 areas with 0 problems and 0 differential differences.
The final TypeScript gate includes the structure checks and passes with no warnings failing the gate.
No other uncertainty remains for Task 11a.

## Fix round 1

Four new coordinator decisions narrow only the corresponding coordinator decisions published in 3601469.
All four adds have a successful dry run before publication, and every entry correction appears with `edit` in the same add as its decision.
No published decision is edited, and no author decision is narrowed or replaced.
The old decisions d-7s8k61, d-sk1r7r, d-tnpe08, and d-jtbrh6 retain their original eleven number handles unchanged; immutability requires leaving that historical excess in place.
The new decisions carry only the numbers used by their own statements and the entries they change.

### Decisions and entries

| Decision | Narrows | Entries and findings answered |
|---|---|---|
| d-v92j1d | d-7s8k61 | I1: edit s-165qfh to give Python and TypeScript their own explicit structure-rule sentence, retaining the Python allowed-imports table, cycles, front doors, 300-line limit, clock and randomness restrictions, and confinement of `os`, `subprocess`, and `open` I/O calls. M9: edit s-a4jfp1 to cite d-b1yjpp for TypeScript. M1: handles only for 0.2, 4, and 300. |
| d-t57k7f | d-sk1r7r | M5 and M9: edit s-07ar34 to drop the viewer non-sequitur and cite d-8kasej and d-14vk9b. M7 and M8: edit s-d1dd20 to retain task identity and nesting, create s-azfcx4 for workflow position, s-h4x7bx for planner-created children and the waiting parent, and s-1csktg for task code links. Reaffirm s-8v6ek2 and s-cf0qph unchanged because they still refer to the same task identity. M1: handles only for 0.2, build steps 1, 2, 4, and 5, and one nesting level. |
| d-9z5y74 | d-tnpe08 | M2: edit s-20dnpp to state separately the lodge-only branch, local work-tree refusal, remote export without a work-tree check, temporary index, and push without force. Remove its duplicated unchanged-tree claim. M1: reaffirm s-b4dtqk unchanged with handles for one commit a minute and the retry minute, both tied to `ts/src/app/exporters.ts:21`, `EXPORT_INTERVAL_SECONDS = 60`. |
| d-sw1dwn | d-jtbrh6 | M3: edit s-yaz279 so only a decision or thread it would map must round-trip through its writer, and remove the export sentence already in s-b6jxhr and its unnecessary dependency on that entry. M4: edit s-3cagcv so the attachment exception clearly applies to advised files. M7: edit s-5sgcxx to retain source and mapped checks and their publication refusal, create s-yv40f3 for non-UTF-8 path refusal, and create s-2wqxmw for attachment-byte preservation. M1: its only numeric handle is 0.2. |

The model and storage area orders gain the three and two new entries respectively.
No other record file changes.
The five new entries preserve the design coverage previously held by s-d1dd20 (design lines 87 to 89) and s-5sgcxx (line 289, with d-sdpcyb and d-ryss91 for the detailed validation and byte rules).
Their dependencies retain the task, workflow, and import prerequisites without breaking existing `rests_on` references.
The two task dependants and the batching entry have unchanged text, so their files have no diff although the new decisions list them with `edit`.

The I1 history probe uses `git show server-import:lodge/spec/structure/s-165qfh-a-structure-test-enforces-the-import.md`, followed by `lodge show d-jxwj8m --reasoning --provenance`.
The old entry explicitly includes allowed imports, cycles, front doors, the size limit, and forbidden calls; the earlier report's claim that it was described only through Python ast is incorrect.
The restored wording follows `tests/structure_rules.py`, `tests/structure_calls.py`, and the Python and TypeScript `MAX_LINES` constants, rather than attributing the combined rules to TypeScript alone.
The local-only export check is at `ts/src/git/export.ts:92`, and the import's skip before the writer comparison is at `ts/src/app/importing.ts:103` and `ts/src/app/importing.ts:108`.

### Dropped sentences and parked work

M6: s-j8tp0n dropped "A project's knowledge lives in the repository of the project it is about, and lodge is its own repository."
The universal repository claim no longer describes a server project's event source of truth, so the replacement scopes git to lodge 0.2 and events to the server.
The self-hosting clause is omitted from this store-authority entry because it adds no rule about which active store is authoritative; this is an omission, not a reversal of self-hosting.
No entry change is needed for this report-only accounting.

M6: s-z1zvb4 dropped "the header for programs, the body for people".
This describes the Markdown file presentation, which still holds for lodge 0.2; its explanatory slogan was omitted while the entry retained Markdown files with YAML headers and added event storage.
It was not made false by the server, and the omission should have been named in the original report.
No new decision is needed because this fix documents the cut rather than changing the entry.

M8: the earlier claim that every step assignment comes from the Build order is too broad.
Tasks are explicitly item 2, and workflow as data is item 5; these step numbers remain in s-d1dd20 and s-azfcx4.
The Build order gives no step specifically to "the planner session creates the child tasks through the API from the plan; the parent waits at its build step until every child is done" or to "a task has code links".
Those claims now live in s-h4x7bx and s-1csktg without an invented step.
Item 4 names the runner and item 6 names code views, but neither directly assigns the corresponding task claim a step.
This is the explicit exception to the general future-step convention permitted by the fix brief.
Task 11c should add the build-order dependencies to s-azfcx4 as well as the earlier report's list; the two unnumbered claims require no guessed step dependency.

M7: the further split of s-g8m3qv is parked.
The task and workflow definitions already rest on that project entry, and the entry brings together the project's workflow, repository links, and members across future steps.
Splitting it responsibly requires reconsidering those prerequisite links alongside the work and later model entries in Tasks 11b and 11c; that is broader than moving independent lookup sentences with no dependency consequences.
The identity and one-level nesting in s-d1dd20 stay together, and source settings, mapped checks, and refusal in s-5sgcxx stay together as one import-validation contract.
The review's additional s-5fd1qs title and test-first split suggestion is parked for the next Constraints pass; this brief's M7 scope names the other three entries.
No supported claim is lost in either completed split.

### Acceptance and checks

The existing ignored acceptance script now accepts `--fix1`, which runs ten finding probes from `.drafts/task-11a/fix1/verify.ts`.
Before any fix add, it exits 1 with `0 passed; 10 failed; 10 fix-round checks`.
I1, M2 to M5, M8, and M9 compare complete expected entry text; M1 reads correction-decision provenance, M7 checks the new lookup entries and the parking report, and M6 checks the report's two exact cut quotations.
Report-only findings necessarily inspect the report as well as the store.
The original 34 content expectations are extended to include the five new entries and the revised text, and the four original dependency checks remain intact.

| file:line | First failing output before publication |
|---|---|
| .drafts/task-11a/fix1/verify.ts:9 | FAIL I1 Python and TypeScript structure rules |
| .drafts/task-11a/fix1/verify.ts:10 | FAIL M1 minimal new number handles and minute evidence |
| .drafts/task-11a/fix1/verify.ts:11 | FAIL M2 local and remote branch checks |
| .drafts/task-11a/fix1/verify.ts:12 | FAIL M3 only mapped decisions and threads have writer checks |
| .drafts/task-11a/fix1/verify.ts:13 | FAIL M4 attachment exception reads clearly |
| .drafts/task-11a/fix1/verify.ts:14 | FAIL M5 remove unrelated viewer sentence |
| .drafts/task-11a/fix1/verify.ts:15 | FAIL M6 report accounts for both dropped sentences |
| .drafts/task-11a/fix1/verify.ts:16 | FAIL M7 split task and import lookups and account for parked project |
| .drafts/task-11a/fix1/verify.ts:17 | FAIL M8 task claims have no invented steps |
| .drafts/task-11a/fix1/verify.ts:18 | FAIL M9 use settling decision handles |

After each add, `lodge spec | grep 'changed since'` still prints just the two explanatory sentences in s-7wbv0e and s-kba448.
There is no dependency freshness warning to resolve.

| Command | Result |
|---|---|
| `lodge add --dry-run .drafts/task-11a/fix1/SECTION/*.md`, followed by the matching add, for constraints, model, export, and import | Four successful dry runs, then the four decisions listed above; no record hand edits. |
| `bun .drafts/task-11a/verify-records.ts --fix1` | `10 passed; 0 failed; 10 fix-round checks`. |
| `bun .drafts/task-11a/verify-records.ts` | `39 passed; 0 failed; 39 acceptance checks`. |
| `bun .drafts/task-11a/verify-links.ts` | `4 passed; 0 failed; 4 dependency checks`. |
| `uv run --frozen --quiet lodge check` | `ok`. |
| `uv run --frozen --quiet lodge spec` filtered for `changed since` after every add | Two explanatory sentences, accounted for above. |
| `sh scripts/check.sh` | Exit 0; 1,399 Python tests and 2,137 TypeScript tests pass; 460 records, 10 areas, 0 problems, and 0 differential differences; round-trip test passes. |
| `git diff --cached --check` and `git diff --check` | Exit 0, no output. |

Drafts and acceptance scripts remain ignored under `.drafts/task-11a/`.
No implementation, dependency, permanent test, frozen document, earlier brief, or review changes.
The parked project split and the additional Constraints suggestion are the only remaining review concerns.
The final verification command, `sh scripts/check-ts.sh`, exits 0 with `2137 pass`, `0 fail`, and `Ran 2137 tests across 191 files. [11.62s]`, including the structure checks.
