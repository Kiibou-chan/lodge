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

## Task 11b

Task 11b records Intent, Goals, Non-goals, Must nots, Workflow as data, and Tasks.
It adds 37 entries, edits two existing purpose entries, adds the work area, and records six section decisions plus a coordinator-approved corrective split decision.
The existing Task 11a report remains unchanged.
All records are written through a successful dry run followed by `uv run --frozen --quiet lodge add`.
No implementation, permanent test, dependency, frozen design, or earlier review file changes.

### Files and design coverage

Design handles refer to `docs/superpowers/specs/2026-11-02-lodge-server-design.md`.
Each new entry is one paragraph of at most 150 words; each sentence occupies its own line.
The file table describes the final entries after the corrective split.

| file:line | Decision | Design lines | Change |
|---|---|---|---|
| lodge/decisions/d-dx6xt4-lodge-integrates-agent-development-workflows.md:1 | d-dx6xt4 | 8-17 | lodge integrates agent development workflows; coordinator, product scope, section reasons, and applicable number handles |
| lodge/spec/purpose/s-fw6xhy-lodge-integrates-flexible-agent-development-workflows.md:1 | d-dx6xt4 | 10-17 | Create: lodge integrates flexible agent development workflows |
| lodge/decisions/d-6x8fd9-server-goals-keep-task-work-and.md:1 | d-6x8fd9 | 19-30 | Server goals keep task work and context together; coordinator, product scope, section reasons, and applicable number handles |
| lodge/spec/purpose/s-k570d9-task-state-is-actionable-in-one.md:1 | d-6x8fd9 | 21 | Create: Task state is actionable in one interface |
| lodge/spec/purpose/s-ts73yt-tasks-and-questions-keep-their-own.md:1 | d-6x8fd9 | 22 | Create: Tasks and questions keep their own conversation context |
| lodge/spec/purpose/s-wgkrmr-session-outputs-belong-to-the-task.md:1 | d-6x8fd9 | 23 | Create: Session outputs belong to the task and survive the session |
| lodge/spec/purpose/s-gyamm5-new-sessions-start-from-the-task.md:1 | d-6x8fd9 | 24 | Create: New sessions start from the task context |
| lodge/spec/purpose/s-fpxzb9-open-session-questions-share-a-waiting.md:1 | d-6x8fd9 | 25 | Create: Open session questions share a waiting list |
| lodge/spec/purpose/s-81kf9s-project-workflows-are-adaptable-data.md:1 | d-6x8fd9 | 26 | Create: Project workflows are adaptable data |
| lodge/spec/purpose/s-5tgnrn-lodge-starts-or-suggests-sessions-across.md:1 | d-6x8fd9 | 27 | Create: lodge starts or suggests sessions across execution locations |
| lodge/spec/purpose/s-cg69z0-session-reports-are-shown-apart-from.md:1 | d-6x8fd9 | 28 | Create: Session reports are shown apart from checked facts |
| lodge/spec/purpose/s-6r0exg-people-use-lodge-alone-or-together.md:1 | d-6x8fd9 | 30 | Create: People use lodge alone or together |
| lodge/decisions/d-ktz4rj-server-scope-leaves-optional-product-extensions.md:1 | d-ktz4rj | 32-40 | Server scope leaves optional product extensions for later; coordinator, product scope, section reasons, and applicable number handles |
| lodge/spec/purpose/s-6z04mq-a-code-editor-remains-outside-the.md:1 | d-ktz4rj | 34 | Create: A code editor remains outside the product scope |
| lodge/spec/purpose/s-gdtksn-mock-and-built-screenshot-comparison-waits.md:1 | d-ktz4rj | 35 | Create: Mock and built screenshot comparison waits for app starting |
| lodge/spec/purpose/s-chycjf-a-desktop-shell-must-earn-its.md:1 | d-ktz4rj | 36 | Create: A desktop shell must earn its place |
| lodge/spec/purpose/s-tjq0rm-sqlite-serves-until-another-database-or.md:1 | d-ktz4rj | 37 | Create: SQLite serves until another database or process is needed |
| lodge/spec/purpose/s-gyyt5k-managed-agents-remains-outside-the-scope.md:1 | d-ktz4rj | 38 | Create: Managed Agents remains outside the scope |
| lodge/spec/purpose/s-4gjz9j-self-hosted-cloud-environments-remain-outside.md:1 | d-ktz4rj | 39 | Create: Self-hosted cloud environments remain outside the scope |
| lodge/spec/purpose/s-nhx8zw-pull-request-and-ci-integration-starts.md:1 | d-ktz4rj | 40 | Create: Pull request and CI integration starts with GitHub |
| lodge/decisions/d-jch6c9-server-safeguards-preserve-trust-and-human.md:1 | d-jch6c9 | 42-50 | Server safeguards preserve trust and human control; coordinator, product scope, section reasons, and applicable number handles |
| lodge/spec/purpose/s-ydkmyq-lodge-never-handles-claude-sign-in.md:1 | d-jch6c9 | 47 | Create: lodge never handles Claude sign-in credentials |
| lodge/spec/purpose/s-jqh7hf-a-session-claim-never-appears-as.md:1 | d-jch6c9 | 48 | Create: A session claim never appears as a checked fact |
| lodge/spec/purpose/s-4w05xp-secrets-never-go-where-other-people.md:1 | d-jch6c9 | 49 | Create: Secrets never go where other people can read them |
| lodge/spec/purpose/s-xy6qte-merging-to-main-requires-a-person.md:1 | d-jch6c9 | 50 | Create: Merging to main requires a person’s go |
| lodge/decisions/d-11yx0r-workflow-documents-retain-process-history-and.md:1 | d-11yx0r | 96-170 | Workflow documents retain process history and explicit transitions; coordinator, product scope, section reasons, and applicable number handles |
| lodge/spec/work/s-c0k9hx-workflow-documents-are-versioned-per-task.md:1 | d-11yx0r | 98 | Create: Workflow documents are versioned per task kind |
| lodge/spec/work/s-xqza9k-workflow-steps-name-actors-and-progression.md:1 | d-11yx0r, d-vsspgk | 101 | Create, then split edit: Workflow steps name their actors |
| lodge/spec/work/s-hmj4mc-workflow-steps-specify-session-starts-and.md:1 | d-11yx0r, d-vsspgk | 103 | Create, then split edit: Workflow steps specify how sessions start |
| lodge/spec/work/s-krdpxq-workflow-steps-declare-artefact-inputs-and.md:1 | d-11yx0r | 105 | Create: Workflow steps declare artefact inputs and outputs |
| lodge/spec/work/s-68mfam-workflow-failures-follow-named-back-edges.md:1 | d-11yx0r | 106 | Create: Workflow failures follow named back-edges |
| lodge/spec/work/s-an745k-workflow-checklists-expose-omissions.md:1 | d-11yx0r | 107, 170 | Create: Workflow checklists expose omissions |
| lodge/spec/work/s-pttahq-review-findings-determine-progression-thresholds.md:1 | d-11yx0r | 109-110 | Create: Review findings determine progression thresholds |
| lodge/spec/work/s-h48a8n-a-fix-round-counts-entry-into.md:1 | d-11yx0r | 111 | Create: A fix round counts entry into a fix step |
| lodge/spec/work/s-0tn1e8-the-default-plan-workflow-runs-from.md:1 | d-11yx0r | 112-145, 168 | Create: The default plan workflow runs from mock to authorised merge |
| lodge/spec/work/s-hke5m9-the-default-child-task-workflow-builds.md:1 | d-11yx0r | 146-168 | Create: The default child task workflow builds reviews and rechecks |
| lodge/spec/work/s-73ee5k-session-to-do-reports-sit-under.md:1 | d-11yx0r | 169 | Create: Session to-do reports sit under the workflow step |
| lodge/spec/work/s-3ysqhz-workflow-steps-declare-progression-conditions.md:1 | d-vsspgk | 102 | Create: Workflow steps declare progression conditions |
| lodge/spec/work/s-mrnqdh-workflow-steps-name-execution-locations.md:1 | d-vsspgk | 104 | Create: Workflow steps name execution locations |
| lodge/decisions/d-pfdqpp-task-views-show-work-state-and.md:1 | d-pfdqpp | 172-176 | Task views show work state and permit reasoned movement; coordinator, product scope, section reasons, and applicable number handles |
| lodge/spec/work/s-h1e6jc-a-task-page-shows-its-state.md:1 | d-pfdqpp | 174 | Create: A task page shows its state and related work |
| lodge/spec/work/s-bxws89-project-boards-group-task-cards-by.md:1 | d-pfdqpp | 175 | Create: Project boards group task cards by step |
| lodge/spec/work/s-pyr5rx-a-person-moves-a-task-on.md:1 | d-pfdqpp | 176 | Create: A person moves a task on or sends it back with a reason |
| lodge/decisions/d-vsspgk-separate-independent-workflow-fields-for-lookup.md:1 | d-vsspgk | 101-104 | Separate actors, progression conditions, session starts, and execution locations |
| lodge/spec/purpose/s-7ah5n7-kinds-of-knowledge-and-projects-outside.md:1 | d-6x8fd9 | 21, 23, 25, 30 | Scope previous exclusions to lodge 0.2 and add the server scope by build step |
| lodge/spec/purpose/s-c8hrye-threads-wait-for-an-agent-session.md:1 | d-6x8fd9 | 22, 27 | Scope live-chat exclusion to lodge 0.2 and retain the server goal settled by d-wc9wt2 |
| lodge/spec/purpose/_area.md:1 | Section adds | 8-50 | Order new purpose entries and place the server must-nots immediately after s-4ykcm0 |
| lodge/spec/work/_area.md:1 | d-11yx0r, d-pfdqpp, d-vsspgk | 96-176 | Create Tasks and workflows at rank 11, with its intro and ordered entries |
| docs/superpowers/plans/2026-11-02-lodge-server-import/task-11-report.md:1 | Report | Task 11b | Append this coverage, test evidence, commands, and accounting |

Line 29 reuses s-31atpc for unchanged record meanings.
Line 44 reuses s-q4s548, s-pncjp8, and s-4ykcm0 for the original must-nots.
The model definitions s-tprwhs, s-d1dd20, s-azfcx4, s-h4x7bx, s-1csktg, s-8v6ek2, s-cf0qph, and s-nfgv2t are linked where required rather than restated as new definitions.
Workflow syntax remains open, as line 168 requires; the default-flow entries hold the sample's content rather than fixing YAML syntax.

### Changed sentences and narrowings

In s-7ah5n7, the exclusion sentence gains the scope “For lodge 0.2”, and the evaluation-and-pilot sentence gains the same scope.
The thread sentence retains that a thread holds no claim of its own and that its settlement enters lodge as a decision.
The new server sentence is:

> On the server, tasks, artefacts, and session reporting are in scope from build step 2, the phone interface from build step 3, and use by several people from build step 7.

In s-c8hrye, the live-chat exclusion gains the scope “For lodge 0.2”.
Its existing session-instructions and later-thread-format sentences remain.
The new server sentence is:

> From build step 4, a session lodge starts is talked to inside lodge, in the thread of its task or artefact, as settled by d-wc9wt2.

The corrective split changes s-xqza9k to contain only the actor field and s-hmj4mc to contain only how sessions start, with matching titles.
The removed progression-condition and execution-location sentences become s-3ysqhz and s-mrnqdh respectively; no claim is lost.

| Narrowed decision | Reason and retained meaning |
|---|---|
| d-cg3nn3, by d-6x8fd9 | Universal phone and task-knowledge exclusions become lodge 0.2 exclusions; other boundaries and previous viewer narrowings remain |
| d-3d4g9j, by d-6x8fd9 | Universal live-session exclusion becomes the lodge 0.2 viewer exclusion; attribution, confirmation, configured-address, and thread safeguards remain |
| d-11yx0r, by d-vsspgk | Combined field groupings split for independent lookup; workflow semantics remain |

No author decision is narrowed or replaced.
In particular, d-dyrpc6 and d-wc9wt2 retain their full authority.
Other looks-related feedback is answered no in the decisions' reasoning.

### Test-first evidence

The coordinator approves ignored acceptance scripts, following Task 11a's records-only practice.
Every process those scripts start uses Bun.spawnSync.
The initial script checks each entry's title, complete statement, and required current dependencies through lodge show, and checks the complete statements of the two scoped edits.
Its first run precedes every section add and exits 1 with `0 passed; 37 failed; 37 acceptance checks`.
After the section adds it exits 0 with `37 passed; 0 failed; 37 acceptance checks`.
No carried implementation test is changed, and no implementation mutation is needed.

| file:line | Acceptance check | First failing output |
|---|---|---|
| .drafts/task-11b/manage.ts:36 | s-fw6xhy: full expected statement and dependencies | FAIL s-fw6xhy: lodge integrates flexible agent development workflows (entry absent) |
| .drafts/task-11b/manage.ts:36 | s-k570d9: full expected statement and dependencies | FAIL s-k570d9: Task state is actionable in one interface (entry absent) |
| .drafts/task-11b/manage.ts:36 | s-ts73yt: full expected statement and dependencies | FAIL s-ts73yt: Tasks and questions keep their own conversation context (entry absent) |
| .drafts/task-11b/manage.ts:36 | s-wgkrmr: full expected statement and dependencies | FAIL s-wgkrmr: Session outputs belong to the task and survive the session (entry absent) |
| .drafts/task-11b/manage.ts:36 | s-gyamm5: full expected statement and dependencies | FAIL s-gyamm5: New sessions start from the task context (entry absent) |
| .drafts/task-11b/manage.ts:36 | s-fpxzb9: full expected statement and dependencies | FAIL s-fpxzb9: Open session questions share a waiting list (entry absent) |
| .drafts/task-11b/manage.ts:36 | s-81kf9s: full expected statement and dependencies | FAIL s-81kf9s: Project workflows are adaptable data (entry absent) |
| .drafts/task-11b/manage.ts:36 | s-5tgnrn: full expected statement and dependencies | FAIL s-5tgnrn: lodge starts or suggests sessions across execution locations (entry absent) |
| .drafts/task-11b/manage.ts:36 | s-cg69z0: full expected statement and dependencies | FAIL s-cg69z0: Session reports are shown apart from checked facts (entry absent) |
| .drafts/task-11b/manage.ts:36 | s-6r0exg: full expected statement and dependencies | FAIL s-6r0exg: People use lodge alone or together (entry absent) |
| .drafts/task-11b/manage.ts:36 | s-6z04mq: full expected statement and dependencies | FAIL s-6z04mq: A code editor remains outside the product scope (entry absent) |
| .drafts/task-11b/manage.ts:36 | s-gdtksn: full expected statement and dependencies | FAIL s-gdtksn: Mock and built screenshot comparison waits for app starting (entry absent) |
| .drafts/task-11b/manage.ts:36 | s-chycjf: full expected statement and dependencies | FAIL s-chycjf: A desktop shell must earn its place (entry absent) |
| .drafts/task-11b/manage.ts:36 | s-tjq0rm: full expected statement and dependencies | FAIL s-tjq0rm: SQLite serves until another database or process is needed (entry absent) |
| .drafts/task-11b/manage.ts:36 | s-gyyt5k: full expected statement and dependencies | FAIL s-gyyt5k: Managed Agents remains outside the scope (entry absent) |
| .drafts/task-11b/manage.ts:36 | s-4gjz9j: full expected statement and dependencies | FAIL s-4gjz9j: Self-hosted cloud environments remain outside the scope (entry absent) |
| .drafts/task-11b/manage.ts:36 | s-nhx8zw: full expected statement and dependencies | FAIL s-nhx8zw: Pull request and CI integration starts with GitHub (entry absent) |
| .drafts/task-11b/manage.ts:36 | s-ydkmyq: full expected statement and dependencies | FAIL s-ydkmyq: lodge never handles Claude sign-in credentials (entry absent) |
| .drafts/task-11b/manage.ts:36 | s-jqh7hf: full expected statement and dependencies | FAIL s-jqh7hf: A session claim never appears as a checked fact (entry absent) |
| .drafts/task-11b/manage.ts:36 | s-4w05xp: full expected statement and dependencies | FAIL s-4w05xp: Secrets never go where other people can read them (entry absent) |
| .drafts/task-11b/manage.ts:36 | s-xy6qte: full expected statement and dependencies | FAIL s-xy6qte: Merging to main requires a person’s go (entry absent) |
| .drafts/task-11b/manage.ts:36 | s-c0k9hx: full expected statement and dependencies | FAIL s-c0k9hx: Workflow documents are versioned per task kind (entry absent) |
| .drafts/task-11b/manage.ts:36 | s-xqza9k: full expected statement and dependencies | FAIL s-xqza9k: Workflow steps name actors and progression conditions (entry absent) |
| .drafts/task-11b/manage.ts:36 | s-hmj4mc: full expected statement and dependencies | FAIL s-hmj4mc: Workflow steps specify session starts and locations (entry absent) |
| .drafts/task-11b/manage.ts:36 | s-krdpxq: full expected statement and dependencies | FAIL s-krdpxq: Workflow steps declare artefact inputs and outputs (entry absent) |
| .drafts/task-11b/manage.ts:36 | s-68mfam: full expected statement and dependencies | FAIL s-68mfam: Workflow failures follow named back-edges (entry absent) |
| .drafts/task-11b/manage.ts:36 | s-an745k: full expected statement and dependencies | FAIL s-an745k: Workflow checklists expose omissions (entry absent) |
| .drafts/task-11b/manage.ts:36 | s-pttahq: full expected statement and dependencies | FAIL s-pttahq: Review findings determine progression thresholds (entry absent) |
| .drafts/task-11b/manage.ts:36 | s-h48a8n: full expected statement and dependencies | FAIL s-h48a8n: A fix round counts entry into a fix step (entry absent) |
| .drafts/task-11b/manage.ts:36 | s-0tn1e8: full expected statement and dependencies | FAIL s-0tn1e8: The default plan workflow runs from mock to authorised merge (entry absent) |
| .drafts/task-11b/manage.ts:36 | s-hke5m9: full expected statement and dependencies | FAIL s-hke5m9: The default child task workflow builds reviews and rechecks (entry absent) |
| .drafts/task-11b/manage.ts:36 | s-73ee5k: full expected statement and dependencies | FAIL s-73ee5k: Session to-do reports sit under the workflow step (entry absent) |
| .drafts/task-11b/manage.ts:36 | s-h1e6jc: full expected statement and dependencies | FAIL s-h1e6jc: A task page shows its state and related work (entry absent) |
| .drafts/task-11b/manage.ts:36 | s-bxws89: full expected statement and dependencies | FAIL s-bxws89: Project boards group task cards by step (entry absent) |
| .drafts/task-11b/manage.ts:36 | s-pyr5rx: full expected statement and dependencies | FAIL s-pyr5rx: A person moves a task on or sends it back with a reason (entry absent) |
| .drafts/task-11b/manage.ts:44 | s-7ah5n7: full expected statement | FAIL s-7ah5n7: lodge 0.2 scope and server goal (old unscoped exclusion) |
| .drafts/task-11b/manage.ts:44 | s-c8hrye: full expected statement | FAIL s-c8hrye: lodge 0.2 scope and server goal (old unscoped exclusion) |

The corrective split gets four independent expectations before its add.
Their first run exits 1 with `0 passed; 4 failed; 4 split checks`, against the combined entries and the absent new entries.
Their green run exits 0 with `4 passed; 0 failed; 4 split checks`.

| file:line | Acceptance check | First failing output |
|---|---|---|
| .drafts/task-11b/split.ts:36 | s-xqza9k: separate field, complete statement, and dependencies | FAIL s-xqza9k: Workflow steps name their actors (combined fields) |
| .drafts/task-11b/split.ts:36 | s-hmj4mc: separate field, complete statement, and dependencies | FAIL s-hmj4mc: Workflow steps specify how sessions start (combined fields) |
| .drafts/task-11b/split.ts:36 | s-3ysqhz: separate field, complete statement, and dependencies | FAIL s-3ysqhz: Workflow steps declare progression conditions (entry absent) |
| .drafts/task-11b/split.ts:36 | s-mrnqdh: separate field, complete statement, and dependencies | FAIL s-mrnqdh: Workflow steps name execution locations (entry absent) |

The combined script's final expectations include the split entries and exit 0 with `39 passed; 0 failed; 39 acceptance checks`.
The permanent structure checks run in the whole TypeScript gate and remain unchanged.

### Coordinator rulings, deviations, and uncertainty

The coordinator approves scoping s-7ah5n7 and s-c8hrye to lodge 0.2, narrowing only coordinator decisions, and using ignored acceptance scripts.
The coordinator approves the exact Build order mapping and leaving unassigned claims unnumbered.
The coordinator also approves the corrective field split and its extra decision, d-vsspgk; this is the only additional decision beyond the six section decisions.
The extra decision is needed because self-review finds that independent fields deserve separate lookup entries after the original workflow decision is already added and immutable.

Build steps come only from Build order: tasks, artefacts, session reporting, briefs, and waiting use step 2; interface uses step 3; starting sessions uses step 4; workflow and claimed versus checked use step 5; GitHub uses step 6; several people use step 7.
Intent, permanent must-nots, and non-goals have no invented build step.
Design line 22's local task-and-question threads backed by sessions and line 176's go or return-with-reason claim have no specifically assigned step, so they stay unnumbered with the coordinator's approval.
The first design's original must-nots and record meanings stay linked to their existing entries.
The managed-service billing and environment-eligibility observations stay in the Non-goals reasoning as the design's reasons, rather than new service promises.

No build-order entry exists when lodge search “build order” is read.
As the brief requires, this task creates no build-order entry; Task 11c adds build-order rests_on links to the numbered entries in this report, as it does for 11a.
The parked s-g8m3qv and s-5sgcxx splits remain for 11c.
No sessions area is created because no Task 11b section belongs there.
The work area is absent at the start, so its first section add creates it; later adds extend it.

After each section add, lodge spec filtered for “changed since” shows only the same two inherited explanatory sentences.
They are s-7wbv0e's description of link freshness and s-kba448's description of dependency warnings, rather than newly stale claims.
They remain unchanged and named here, as the brief requires.
There is no unresolved content question after the coordinator rulings.
The initial Intent and Must nots adds emit advisory missing-number feedback for source-line labels in reasoning; number handles are restricted to numbers actually used by the statements, as the brief requires.
Other related-record and area-order feedback is advisory; lodge check remains clean.

### Commands and final results

Commands below run from the lane checkout; outputs and helper scripts stay ignored under .drafts/task-11b.
The preparatory reads cover CLAUDE.md, the required plan sections, the complete design, Task 11a's report, the current specification, all consumed IDs, the eight author decisions, and the relevant built export, import, and hook modules.

| Command or command family | Result or last line |
|---|---|
| uv run --frozen --quiet lodge guide | Exit 0; guide ends with exit-code definitions |
| uv run --frozen --quiet lodge waiting | Exit 0; nothing waiting for an agent or the author |
| git branch --show-current; git status --short | server-import-records; initially clean |
| lodge spec, spec --area purpose, and spec --area work | Current entries read; work initially absent |
| lodge search 'build order'; lodge show ID --reasoning --provenance; lodge draft REF | Existing decisions, entries, prerequisites, and base handles read |
| bun .drafts/task-11b/manage.ts prepare | Prepared entry drafts and acceptance expectations; lodge id s per new entry |
| bun .drafts/task-11b/manage.ts verify, before adds | Exit 1; 0 passed; 37 failed; 37 acceptance checks |
| bun .drafts/task-11b/manage.ts assemble SECTION | Six section draft groups assembled; current area bases and scoped edit bases used |
| bun .drafts/task-11b/manage.ts dry-run SECTION | Exit 0 for each; dry run: nothing published |
| bun .drafts/task-11b/manage.ts add SECTION | Exit 0 for each; staged each section decision and its entries |
| uv run --frozen --quiet lodge spec filtered for 'changed since', after every section and correction | Only s-7wbv0e and s-kba448 explanatory sentences |
| bun .drafts/task-11b/manage.ts verify, after sections | Exit 0; 37 passed; 0 failed; 37 acceptance checks |
| bun .drafts/task-11b/split.ts prepare and verify | Four split expectations prepared; exit 1; 0 passed; 4 failed; 4 split checks |
| bun .drafts/task-11b/split.ts dry-run | Exit 0; dry run: nothing published |
| bun .drafts/task-11b/split.ts add | Exit 0; staged d-vsspgk s-xqza9k s-hmj4mc s-3ysqhz s-mrnqdh |
| bun .drafts/task-11b/split.ts update and verify | Expectations updated; exit 0; 4 passed; 0 failed; 4 split checks |
| bun .drafts/task-11b/manage.ts verify, final | Exit 0; 39 passed; 0 failed; 39 acceptance checks |
| uv run --frozen --quiet lodge check | Exit 0; ok |
| uv run --frozen --quiet lodge spec filtered and counted for 'changed since' | Exit 0; 2, both explanatory sentences named above |
| git diff --cached --check | Exit 0; no output |
| sh scripts/check.sh | Exit 0; 1399 Python tests passed, 2137 TypeScript tests passed, structure checks passed, and 0 differential differences; last line: Ran 1 test across 1 file. [191.00ms] |
| sh scripts/check-ts.sh, last verification command | Exit 0; 2137 pass, 0 fail, and structure checks passed; last line: Ran 2137 tests across 191 files. [11.86s] |

The full gate includes the unchanged structure tests, strict typing, unused-code checks, Python tests, TypeScript tests, and the differential comparison.
No package installation is required, and bun add is never run.
The final record and report commit uses explicit paths, the requested identity, and the Codex co-author trailer, and is pushed to origin/server-import-records.

## Task 11b fix round 1

The correction removes the misplaced Talking claim, separates independently looked-up claims, fixes the build-step wording and number evidence, and preserves stable IDs for the first claims.
All records are written through lodge add after a successful dry run, with drafts and acceptance scripts under .drafts/task-11b/.
There are 12 edited entries, 10 new entries, two area-order edits, and two new coordinator decisions.
No published decision is edited, and no author decision is narrowed or replaced.

### Decisions and changed entries

| file:line | Decision | Finding answered |
|---|---|---|
| lodge/decisions/d-tx7e0m-correct-goal-scope-and-separate-independently.md:1 | d-tx7e0m | Narrows d-6x8fd9, d-ktz4rj, d-11yx0r, and d-pfdqpp for I1, I2, I3, and the wording corrections; retains their other claims and safeguards |
| lodge/decisions/d-p94znc-keep-the-workflow-cardinality-handle-precise.md:1 | d-p94znc | Narrows d-tx7e0m only for an extraneous number citation introduced during this round; the workflow statement is unchanged |
| lodge/spec/purpose/s-c8hrye-threads-wait-for-an-agent-session.md:1 | d-tx7e0m | I1: edit s-c8hrye, Threads wait for an agent session |
| lodge/spec/purpose/s-fpxzb9-open-session-questions-share-a-waiting.md:1 | d-tx7e0m | I2: edit s-fpxzb9, Open session questions share a waiting list |
| lodge/spec/purpose/s-t4tbrj-the-waiting-list-is-answerable-from.md:1 | d-tx7e0m | I2: create s-t4tbrj, The waiting list is answerable from a phone |
| lodge/spec/purpose/s-6r0exg-people-use-lodge-alone-or-together.md:1 | d-tx7e0m | M1: edit s-6r0exg, Other people use lodge alone or together |
| lodge/spec/purpose/s-chycjf-a-desktop-shell-must-earn-its.md:1 | d-tx7e0m | I2: edit s-chycjf, A desktop application is outside the present scope |
| lodge/spec/purpose/s-wrksm5-the-browser-app-installs-on-phones.md:1 | d-tx7e0m | I2: create s-wrksm5, The browser app installs on phones and computers |
| lodge/spec/purpose/s-q6g68q-a-desktop-shell-must-also-run.md:1 | d-tx7e0m | I2: create s-q6g68q, A desktop shell must also run the local server |
| lodge/spec/purpose/s-nhx8zw-pull-request-and-ci-integration-starts.md:1 | d-tx7e0m | I2 weaker: edit s-nhx8zw, Pull request and CI integration starts with GitHub |
| lodge/spec/purpose/s-mnfeyz-git-level-features-work-on-any.md:1 | d-tx7e0m | I2 weaker: create s-mnfeyz, Git-level features work on any host |
| lodge/spec/purpose/s-d56aky-a-gitlab-connector-follows-project-need.md:1 | d-tx7e0m | I2 weaker: create s-d56aky, A GitLab connector follows project need |
| lodge/spec/purpose/s-xy6qte-merging-to-main-requires-a-person.md:1 | d-tx7e0m | M2: edit s-xy6qte, Merging to main requires a person's go |
| lodge/spec/work/s-c0k9hx-workflow-documents-are-versioned-per-task.md:1 | d-tx7e0m, d-p94znc | I2: edit s-c0k9hx, A project has a workflow per task kind |
| lodge/spec/work/s-dxmhjg-workflow-changes-retain-who-changed-what.md:1 | d-tx7e0m | I2: create s-dxmhjg, Workflow changes retain who changed what and when |
| lodge/spec/work/s-pttahq-review-findings-determine-progression-thresholds.md:1 | d-tx7e0m | I2, M6: edit s-pttahq, Reviews report findings with severity |
| lodge/spec/work/s-pw47pk-progression-thresholds-read-review-findings.md:1 | d-tx7e0m | I2, M6: create s-pw47pk, Progression thresholds read review findings |
| lodge/spec/work/s-d0tvr8-session-driven-review-moves-remain-reported.md:1 | d-tx7e0m | I2, M6: create s-d0tvr8, Session-driven review moves remain reported |
| lodge/spec/work/s-73ee5k-session-to-do-reports-sit-under.md:1 | d-tx7e0m | I2 weaker: edit s-73ee5k, Lodge tracks the workflow step of each task |
| lodge/spec/work/s-r2cc8d-session-to-do-reports-sit-under.md:1 | d-tx7e0m | I2 weaker: create s-r2cc8d, Session to-do reports sit under the workflow step |
| lodge/spec/work/s-1hecad-session-to-do-items-may-name.md:1 | d-tx7e0m | I2 weaker: create s-1hecad, Session to-do items may name produced code references |
| lodge/spec/work/s-0tn1e8-the-default-plan-workflow-runs-from.md:1 | d-tx7e0m | M4: edit s-0tn1e8, The default plan workflow runs from mock to authorised merge |
| lodge/spec/work/s-hke5m9-the-default-child-task-workflow-builds.md:1 | d-tx7e0m | M4: edit s-hke5m9, The default child task workflow builds reviews and rechecks |
| lodge/spec/work/s-h1e6jc-a-task-page-shows-its-state.md:1 | d-tx7e0m | M5: edit s-h1e6jc, A task page shows its state and related work |
| lodge/spec/purpose/_area.md:1 | d-tx7e0m | Place the split claims immediately after their retained first claims |
| lodge/spec/work/_area.md:1 | d-tx7e0m | M3: place s-3ysqhz after s-xqza9k and s-mrnqdh after s-hmj4mc, and place split claims beside their first claims |

I1 removes only the final sentence of s-c8hrye, which assigned Talking with a session to build step 4.
Its lodge 0.2 scope, session instructions, and later thread-format sentence remain.
The server goal remains once in s-ts73yt, using the Goals section's own claim at design line 22.
The coordinator selected that interpretation through coord.ask_coordinator, rather than duplicating the goal in s-c8hrye.
The earlier q-2 answer allowing the Talking sentence is withdrawn by this brief.
Task 11c records Talking in sessions from design lines 184 to 190, without assigning a step the Build order does not give.

I2 separates s-pttahq into findings with severity, threshold evaluation (s-pw47pk), and reported progression (s-d0tvr8), each explicitly from build step 5.
All retain s-tprwhs and s-cf0qph, and all gain rests_on s-jqh7hf for M6.
The workflow-kind and change-history claims at design line 98 remain separately named [my call] choices, in s-c0k9hx and s-dxmhjg respectively, from build step 5.
The waiting list stays in s-fpxzb9 from build step 2, and phone access moves to s-t4tbrj from build step 3, both retaining s-nfgv2t.
Desktop scope stays in s-chycjf, installability moves to s-wrksm5 from build step 3, and the shell condition moves to s-q6g68q without an inferred step.
The weaker s-73ee5k case splits cleanly into workflow-step tracking, session to-do reports (s-r2cc8d), and produced code references (s-1hecad), each from build step 5 and retaining s-azfcx4 and s-8v6ek2.
The weaker s-nhx8zw case also splits cleanly: GitHub integration retains the original ID and build step 6, while host-independent git (s-mnfeyz) and a GitLab connector following project need (s-d56aky) receive no invented steps.
No pre-existing rests_on link is removed by these splits.

I3 is answered by d-tx7e0m's 0.2 handle, pyproject.toml:3, project.version = "0.2.0".
The incorrect design-line handle in immutable d-6x8fd9 stays historical.
The correction initially also cited design line 109 as a waiting-list handle alongside the correct workflow cardinality at line 98.
Line 109 describes review findings, so d-p94znc narrows that extraneous citation and carries only line 98 for one workflow per kind, with line 300 for build step 5.
This extra correction is the deviation from the planned single corrective add; both adds have successful dry runs and red acceptance probes.

M1 changes s-6r0exg to say other people use lodge from build step 7, avoiding a claim that solitary use starts then.
M2 replaces the curly apostrophe in s-xy6qte's title with a plain apostrophe; its safeguard statement is unchanged.
M4 names mock, plan, plan-review, plan-fix, build, review, fix, and merge in s-0tn1e8, includes next for plan-fix, and uses continues to for forward then edges in both default workflows.
Failure back-edges still return.
M5 removes code from the step-3 task-page sentence in s-h1e6jc and adds a separate sentence assigning code presentation to build step 6.

### Acceptance first

The existing ignored acceptance script is extended with manage.ts verify-fix-round1, which delegates to fix-round1.ts.
The 22 entry probes compare full statements, titles, and all required current dependencies; separate probes check field order and corrective version evidence.
Before the add, all fail against the current store: 0 passed; 24 failed; 24 fix acceptance checks.
After the add, the same expectations pass: 24 passed; 0 failed; 24 fix acceptance checks.

| file:line | First failing output |
|---|---|
| .drafts/task-11b/fix-round1.ts:47 | FAIL I1: s-c8hrye |
| .drafts/task-11b/fix-round1.ts:47 | FAIL I2: s-fpxzb9 |
| .drafts/task-11b/fix-round1.ts:47 | FAIL I2: s-t4tbrj |
| .drafts/task-11b/fix-round1.ts:47 | FAIL M1: s-6r0exg |
| .drafts/task-11b/fix-round1.ts:47 | FAIL I2: s-chycjf |
| .drafts/task-11b/fix-round1.ts:47 | FAIL I2: s-wrksm5 |
| .drafts/task-11b/fix-round1.ts:47 | FAIL I2: s-q6g68q |
| .drafts/task-11b/fix-round1.ts:47 | FAIL I2 weaker: s-nhx8zw |
| .drafts/task-11b/fix-round1.ts:47 | FAIL I2 weaker: s-mnfeyz |
| .drafts/task-11b/fix-round1.ts:47 | FAIL I2 weaker: s-d56aky |
| .drafts/task-11b/fix-round1.ts:47 | FAIL M2: s-xy6qte |
| .drafts/task-11b/fix-round1.ts:47 | FAIL I2: s-c0k9hx |
| .drafts/task-11b/fix-round1.ts:47 | FAIL I2: s-dxmhjg |
| .drafts/task-11b/fix-round1.ts:47 | FAIL I2, M6: s-pttahq |
| .drafts/task-11b/fix-round1.ts:47 | FAIL I2, M6: s-pw47pk |
| .drafts/task-11b/fix-round1.ts:47 | FAIL I2, M6: s-d0tvr8 |
| .drafts/task-11b/fix-round1.ts:47 | FAIL I2 weaker: s-73ee5k |
| .drafts/task-11b/fix-round1.ts:47 | FAIL I2 weaker: s-r2cc8d |
| .drafts/task-11b/fix-round1.ts:47 | FAIL I2 weaker: s-1hecad |
| .drafts/task-11b/fix-round1.ts:47 | FAIL M4: s-0tn1e8 |
| .drafts/task-11b/fix-round1.ts:47 | FAIL M4: s-hke5m9 |
| .drafts/task-11b/fix-round1.ts:47 | FAIL M5: s-h1e6jc |
| .drafts/task-11b/fix-round1.ts:48 | FAIL M3: field entries precede Tasks |
| .drafts/task-11b/fix-round1.ts:49 | FAIL I3: current corrective decision has the version handle |
| .drafts/task-11b/fix-round1/number-handle.ts:4 | FAIL precise workflow cardinality handle without unrelated line 109 |

The additional number-handle probe fails before d-p94znc and passes afterwards.
The existing acceptance manifest and scoped-edit expectation are refreshed to the corrected statements; manage.ts verify passes all 39 carried checks.
No implementation or permanent test is changed.
All child processes in the draft scripts use Bun.spawnSync.

### Parked and intentionally unchanged

s-7ah5n7 remains parked as allowed by I2.
It combines historical lodge 0.2 exclusions, the independent thread semantic, the evaluation-and-pilot condition, and server scope by build step.
Separating it cleanly requires reviewing the older decisions and redistributing their scope and dependencies; this round preserves those historical boundaries rather than making that wider change.
Its phone scope consequently remains alongside the more specific phone claims.

The immutable reasoning beginning "The coordinator approves ..." in d-6x8fd9, d-pfdqpp, and d-vsspgk remains unchanged, as directed.
No new decision repeats that unsupported approval wording.
The display side effect of d-vsspgk narrowing d-11yx0r remains unchanged, as directed: unchanged entries from that decision can show its narrowing.
The new narrowings can likewise appear on other entries of their section decisions; the entry table above identifies what actually changes.

Task 11c creates the build-order entry and adds the build-order rests_on links to all numbered claims here, including the 10 new entries where numbered, as well as the previous 11a and 11b lists.
It also links s-cg69z0 to its claimed-and-checked entry.
For Code and git and Interface, 11c should link the existing GitHub integration in s-nhx8zw, the installability in s-wrksm5, and phone access in s-t4tbrj rather than repeat them.
Desktop scope, shell eligibility, host-independent git, and the deferred GitLab connector have no step assigned by the design and remain unnumbered.
The Talking claim remains explicitly deferred to sessions in 11c.

### Commands and results

| Command | Result |
|---|---|
| bun .drafts/task-11b/fix-round1.ts verify, before adds | Exit 1; 0 passed; 24 failed |
| bun .drafts/task-11b/fix-round1.ts dry-run; add | Exit 0 each; staged d-tx7e0m and its entries and areas |
| bun .drafts/task-11b/fix-round1/number-handle.ts verify, before correction | Exit 1; precise-cardinality probe fails |
| bun .drafts/task-11b/fix-round1/number-handle.ts | Both dry run and add exit 0; staged d-p94znc and unchanged s-c0k9hx |
| bun .drafts/task-11b/fix-round1/number-handle.ts verify, after correction | Exit 0; precise-cardinality probe passes |
| bun .drafts/task-11b/manage.ts verify | Exit 0; 39 passed; 0 failed; 39 acceptance checks |
| bun .drafts/task-11b/manage.ts verify-fix-round1 | Exit 0; 24 passed; 0 failed; 24 fix acceptance checks |
| uv run --frozen --quiet lodge check | Exit 0; ok |
| uv run --frozen --quiet lodge spec, filtered for changed since | Two matches, both explanatory sentences: s-7wbv0e and s-kba448; neither is edited or a new freshness warning |
| sh scripts/check.sh | Exit 0; Python 1399 passed; TypeScript 2137 pass, 0 fail; differential 1 pass, 0 fail |
| sh scripts/check-ts.sh, last gate | Exit 0; 2137 pass, 0 fail; type, lint, unused-code, and structure checks pass |

The changed-since accounting retains the two matches already named by 11a and the original 11b report.
The report extension and lodge paths are committed explicitly with the required Codex trailer and pushed to server-import-records.
