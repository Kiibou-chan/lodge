# lodge server, build step 1, plan 2: the events store and the operations

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development to implement this plan task by task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** lodge 0.2's operations (`src/lodge/app`) run in TypeScript at parity over an append-only events store in SQLite, and the server design's model changes hold: `decided_by` names a person or an agent role, a person's decision drafted by anyone else waits for that person's approval, a review flag on a person's decision clears only when that person confirms, and every write is checked against the state it lands on; all proved in process, with no HTTP.

**Architecture:** two packages on plan 1's core (d-k5swcq): `app`, the operations, ported from `src/lodge/app` at parity behind the ports `Store`, `Clock`, `IdSource`, and the new `Projects`, all asynchronous (d-59q4jc); and `store`, the adapter that keeps every write as an event in one append-only SQLite table through Kysely over `bun:sqlite` (d-4k9wcr), a file's event holding its path and its bytes (d-smx3xf, d-wje1cn), with the current state and the tables for queries rebuilt from the events.
The port keeps lodge 0.2's shape, so the carried app tests run over in-memory fakes unchanged, and the SQLite store gives one state, its current and published states being the same (design line 79, d-ae1vn5).
The model changes come after the port, as tasks of their own with new tests (d-88p8h9): people in the core, then in the operations and the store, then drafted decisions awaiting their person, and review flags per person.

**Tech stack:** plan 1's (Bun 1.3.14, TypeScript 6.0.3 strict, Biome 2.5.15, dependency-cruiser 18.6.0, knip 6.42.0, `@types/bun` 1.4.3, `yaml` 2.9.1, `@noble/hashes` 2.4.0), plus Kysely 0.29.7 in `store` only (d-4k9wcr; published 2026-10-17, plan 1's probe 11).

**Spec:** `lodge spec` and lodge 0.2's tests for what the operations do; `docs/superpowers/specs/2026-11-02-lodge-server-design.md` (approved by the author 2026-11-02 13:52) for what changes, with her answer SRV-2 (d-zzfmj2).
The plan argues from them, never over them; where they disagree with this plan, they win and the builder reports it.
"Design line N" is a line of the design; "probe N" is an item of `docs/superpowers/plans/2026-11-02-lodge-server-store/probes.md`, whose sources are in `probes/` beside it; "plan 1" is `docs/superpowers/plans/2026-11-02-lodge-server-core.md`.

## Global Constraints

Plan 1's Global Constraints hold for every task of this plan, and each brief repeats them; in short, with what this plan adds:

- Builders are Codex (`codex exec`), one task per brief; Codex sees its brief, `CLAUDE.md`, and the repository, with no network, a read-only git index, and no sockets: the builder never stages, commits, or pushes, and never runs `bun install` or `bun add`; a package the task needs and `ts/package.json` lacks stops the task with BLOCKED and its name.
- The builder's gate is `sh scripts/check-ts.sh` (Biome with `--error-on-warnings`, d-f18pz7; `tsc`, dependency-cruiser, knip, and `bun test`); the coordinator's gate after every task is `sh scripts/check.sh` outside the sandbox, then it stages with explicit paths, commits with `git -c user.name="Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit`, the message ending `Co-Authored-By: Claude <noreply@anthropic.com>`, and pushes `server-store` to `origin`; never `main`.
- lodge 0.2 keeps working: `src/`, `tests/`, `pyproject.toml`, and `uv.lock` are not edited.
- Test-first: each carried or new test is written and seen failing before its code (a missing module or export counts as failing); a carried test over code an earlier task ported is seen failing against a targeted mutation of that code, never a throw at a function's entry, one per test or per named group, listed in the report as a table and then reverted (d-mfayy5, as plan 1's Task 8c did); every existing test keeps passing, edited only where a task says so.
- Lanes (d-d96y91): a task's tests call only what its lane and the tasks it waits for provide; a parameter a later task adds to a function plan 1 ported, or that another lane calls, is trailing and has a default, so every carried call stays as it is.
- Porting (d-88p8h9), as plan 1's Global Constraints say: each Python test becomes a test titled with its name without `test_`, in the file the parity table names, asserting no less; a parametrised test becomes `test.each(cases.map((c) => [c]))` or `test.each([[a, b], …])` with every case; a test that cannot hold keeps its title, asserts the TypeScript behaviour, and is listed in the report; the task's last step flips its rows of `ts/tests/parity.json` and sets each row's `task` to the task's number, as plan 1's rows have it (`"task": ["5a"]`); a row whose port is split over two files names both in its `ts`.
- Types, names, and exceptions follow plan 1: a frozen dataclass is an `interface` with `readonly` fields and, where a Python call leaves a defaulted field out, a default-filling function of the same name in camelCase beside it (`committed`, `gate`, `read`, `listed`, `added`, and `written`; probe 5, d-ca6wbw); `X | None` is `X | null`; a tuple is `readonly T[]`, a `Mapping` a `ReadonlyMap`; a `StrEnum` a `const` object and its union type; `raise E(m)` is `throw new E(m)`, and `except E` a `catch` that rethrows anything not an `E`.
- Calls (d-vd3175): a Python method's parameters without a default stay positional, and those with a default become one trailing options object with their names in camelCase (`add(drafts, { dryRun: true, attachments })`); a test calling Python with keywords calls TypeScript with that object.
- Asynchrony (d-59q4jc): every method of `Store` and `Projects` returns a `Promise`, `Clock.sleep` returns a `Promise`, and every operation of `Lodge` is `async`; a carried test `await`s each operation, and a `pytest.raises` becomes `await expect(promise).rejects.toThrow(Class)` with the pattern where Python matched one.
- Time (d-59q4jc): `Clock.now()` gives a `Now`, `{ epochMs, offsetMinutes }`, never a `Date`; `app/time.ts` (Task 2) turns it into stamps; `app` uses no clock, randomness, local time, or `Date` without `new` (d-mfskz3), so it may write `new Date(ms)` and call its UTC methods, and `core` still sees only stamps.
- Structure (plan 1, Task 3; d-x6f9za; d-s5s2c3; d-nf7wvx): `app` imports only `#core`; `store` imports `#app`, `#core`, `kysely`, and `bun:sqlite`, which the rule `store-imports` (Task 7a) checks, and its confinements hold it to no `fs`, no `fetch`, no socket, and no child process; another package only through its front door (`#app`, `#store`); no file over 300 lines, tests included; a module nearing it is split by topic, as plan 1 says.
- Exports read in a later task (d-tha8st): a file with an export whose first reader comes in a later task goes into `ts/knip.json`'s `entry` in the task that creates it and leaves in the task that gives it that reader; the files and tasks are listed in "Exports read in a later task" below.
- Bytes (d-0q54zn, d-wje1cn): text crosses into the database only as UTF-8 bytes through `encodeUtf8` and back through `decodeUtf8` of `core/text.ts` (Task 7a), which map a byte of an invalid sequence to U+DC00 plus the byte and back, as Python's `surrogateescape` does; a `text` column never holds a record's or a file's text, since it drops a leading U+FEFF and corrupts a lone surrogate (probes 1 and 2).
- No test of this plan needs a socket, so the builder runs every one; tests never touch a real repository or the network; a database is `":memory:"` or a file under a folder from `mkdtempSync` in the system's temporary folder; fixtures are the made-up project of lodge 0.2's tests (the `storage` area), and the people in them are made up (`ada`, `bo`).
- User-facing text and Markdown: British English, no em-dashes, the Oxford comma, one sentence per line; code comments state the fact.

### Exports read in a later task

From the import lines of `src/lodge/app/*.py` and `tests/app/*.py` (`grep -n '^from' tests/app/*.py`):

| File | Into `entry` | Names and the task that first reads them | Out of `entry` |
|---|---|---|---|
| `tests/app/fakes.ts` | Task 2 | `MemoryStore`, `FixedClock`, `CountingIds`, `START` (3) | Task 3 |
| `src/app/state.ts` | Task 3 | `readChecked`, `resolveRef`, `notFound` (4) | Task 4 |
| `src/app/writes.ts` | Task 3 | `mintUnused` (4) | Task 4 |
| `tests/app/support.ts` | Task 3 | `project`, `FIRST` (3); `ENTRY` (4) | Task 4 |
| `src/store/events.ts` | Task 7a | `appendEvents`, `json` (7b) | Task 7b |
| `tests/store/interleaving.ts` | Task 8 | `Interleaving` (9) | Task 9 |

Declared without `export`, so knip reports nothing: the Kysely table interfaces `EventsTable`, `HeadsTable`, `FilesTable`, `MembersTable`, and `HeldTable`, and `MIGRATIONS` of `schema.ts`; `NewEvent` of `events.ts` is exported only if another module names the type.

## Calls made

Each is the planner's ruling, recorded in lodge with scope `process` and this plan as its work item; its reasoning there holds a handle per argument and the cost if wrong.
Every task repeats what it needs of them, so no brief needs this section.

1. d-59q4jc: the ports are asynchronous and `Clock.now()` gives `{ epochMs, offsetMinutes }`.
2. d-ae1vn5: the `Store` port keeps lodge 0.2's methods and outcomes, and the SQLite store gives one state.
3. d-wje1cn: the events table, one event per file written with the file's bytes, the derived tables, and the compare-and-set that publishes; d-0q54zn's codec is this plan's.
4. d-vd3175: defaulted parameters become one trailing options object.
5. d-t7er56: the task cut, `Lodge` ported method by method with the modules it delegates to, and the lanes; d-d96y91 narrows it: a lane's tests call only what its waits provide, a new parameter of a function another lane calls has a default, and Task 12 is split into 12a and 12b; the held thread messages of d-2v8vtk are Task 12c, on the same hold machinery.
6. d-rp74dr: `test_thread_fix_paths.py`'s two command tests wait for plan 3 as `test.todo`, and its row becomes plan 3's.
7. d-vwsnz5 (replacing d-kj59bz): a person is an owner of the project, people reach the core in `Tree.people` and as a defaulted parameter, the words of lodge 0.2 stay for a person named `author`, and a name the records use as a role cannot join.
8. d-znagqe: a person's decision drafted by anyone else is held whole until that person approves or declines it.
9. d-4spcem: a review flag waits for each person whose decision raised it, and each clears their part.
10. d-fv20kp: the check on every write needs no new write path; plan 2 proves it over the events store; d-j28rp0 (replacing d-pmaw3a, which replaced d-pprhpz) narrows it for plan 4's import, which publishes through the store after its own state check, and has `publish` refuse what lodge 0.2's stores refuse, a path holding a surrogate, and a changed decision.
11. d-wx7d0f: projects and their members are events behind the `Projects` port.
12. d-2v8vtk (the author's answer to STORE-1): an agent may relay a person's words into a thread under that person's name, with where and when; the message is held, and the thread waits for that person until they approve it signed in; a person's own message is not held, and one person writing under another's name is refused (Task 12c).
13. d-nf7wvx: the rule `store-imports` holds `store` to `kysely` and `bun:sqlite` among outside modules.
14. d-thvvzx: a store transaction that reads before it writes opens with a write, and a hold is approved or declined once.

## Review Focus

1. A carried test that asserts less than its Python original, or one that no longer `await`s an operation, so that a rejected promise passes unnoticed.
2. The bytes: a file's text that does not come back byte for byte (U+FEFF first, CRLF, U+0000, an astral character, an escaped byte U+DC80 to U+DCFF), a lone surrogate outside the escapes stored rather than refused, and `contentHash` disagreeing with lodge 0.2 on an escaped byte (probe 7).
3. The compare-and-set: a publish on a stale base that writes anything, two writers that both succeed on one base, and a write whose check ran on a state other than the one it lands on.
4. Append-only: any path that updates or deletes an event, a derived table that `rebuild` does not give back row for row, and a `publish` that keeps a path lodge 0.2 refuses, overwrites an attachment, or changes a decision file (d-j28rp0).
5. People: a text that changes for a person named `author` (lodge 0.2's words must stay), a person's decision that becomes current without that person, a hold approved twice or after its decline, a relayed thread message published before its person approves it, a person's message written by another person, and a flag cleared by a person other than the one it waits for.
6. Time: a stamp whose offset is not the clock's, a minute that is not local to the offset, and any `Date` read of the local zone in `app`.

## The plan's place in build step 1

Plan 1 builds the core; this plan starts from its finished core, after plan 1 merges into `server-store`.
Plans 3 (the API, sign-in, and the command) and 4 (the importer, the export, and the design's records) are planned at the same time and build on this plan's `#app` and `#store`; "Interfaces for plans 3 and 4" below is what they may rely on.

## Interfaces for plans 3 and 4

The names are those of `src/lodge/app/__init__.py`'s `__all__` in camelCase, with the additions marked; every operation is `async`.

```ts
// #app, ports
export interface Now { readonly epochMs: number; readonly offsetMinutes: number }          // added
export interface Clock { now(): Now; sleep(seconds: number): Promise<void> }
export interface IdSource { entropy(): Uint8Array }                                         // at least six bytes
export const PublishOutcome = { PUBLISHED: "published", STAGED: "staged", REJECTED: "rejected" } as const;
export const CommitOutcome = { COMMITTED: "committed", ON_BASE: "on the base branch", DETACHED: "on a detached HEAD",
  IN_PROGRESS: "during a merge, rebase, cherry-pick, or revert", LOCKED: "git's index is locked by another process",
  FAILED: "git could not commit" } as const;
export interface Committed { readonly outcome: CommitOutcome; readonly detail: string }    // committed() fills detail ""
export interface Gate { readonly published: Tree; readonly checked: readonly (readonly [string, Tree])[]; readonly notes: readonly string[] }  // gate() fills notes
export interface Store {
  commit(paths: readonly string[], message: string): Promise<Committed>;
  trees(): Promise<readonly [Tree, Tree]>;                 // current, published
  attachmentTexts(): Promise<ReadonlyMap<string, string>>; // added: every attachment's text by path, for plan 4's export
  freshness(): Promise<string | null>;
  gate(current: Tree): Promise<Gate>;
  publish(base: Tree, writes: ReadonlyMap<string, string>, message: string, approves?: number | null): Promise<PublishOutcome>;  // approves: Task 12a
  hold(held: HeldDraft): Promise<number>;                  // Task 12a
  held(): Promise<readonly Held[]>;                        // Task 12a
  decline(seq: number, reason: string): Promise<void>;     // Task 12a: NotFound unless the hold is open
}
export type Actor = { readonly kind: "person"; readonly name: string } | { readonly kind: "agent"; readonly role: string | null };  // added
export function person(name: string): Actor;               // added
export function agent(role?: string | null): Actor;        // added
export function actorText(actor: Actor): string;           // added: "ada", "agent", "agent builder"
export const Role = { OWNER: "owner", MEMBER: "member" } as const;                          // added
export interface Projects {                                // added
  create(project: string, owner: string): Promise<void>;
  members(project: string): Promise<ReadonlyMap<string, Role>>;
  addMember(project: string, person: string, role: Role, by: Actor): Promise<void>;
  storeFor(project: string, actor: Actor): Store;
}
export function stampOf(now: Now): string;               // added: datetime.isoformat(timespec="seconds"), "2026-10-29T09:30:00+01:00"
export function minuteOf(now: Now): string;              // added: strftime("%Y-%m-%d %H:%M") in the offset's own time
export type HeldDraft = HeldAdd | HeldMessage;             // added, Task 12a: what waits for one person's approval
export interface HeldAdd {                                 // added, Task 12a: an add holding a person's decision (d-znagqe)
  readonly kind: "add"; readonly person: string; readonly by: string; readonly drafts: readonly (readonly [string, string])[];
  readonly attachments: readonly (readonly [string, string])[]; readonly importing: boolean; readonly message: string;
}
export interface HeldMessage {                             // added, Task 12a: a person's words relayed into a thread by an agent (d-2v8vtk)
  readonly kind: "message"; readonly person: string; readonly by: string;   // by: actorText of the agent that relayed it
  readonly operation: "ask" | "reply" | "close"; readonly ref: string;      // ask: the record's ref; reply and close: the thread's ID
  readonly raises: Raises | null; readonly text: string | null;            // raises: ask only; text: null only for close
  readonly where: string; readonly when: string;                            // the person's place and minute, as the relay gave them
}
export type Held = HeldDraft & { readonly seq: number; readonly at: string };  // added, Task 12a
export type Approved = { readonly kind: "add"; readonly added: Added } | { readonly kind: "message"; readonly written: Written };  // added, Task 12b

// #app, errors
export class LodgeError extends Error { readonly exitCode: number }  // 2
export class NotFound extends LodgeError {}                // 2
export class Conflict extends LodgeError {}                // 1
export class StaleList extends Conflict {}                 // 1
export class Forbidden extends LodgeError {}               // added, Task 11: 2; the API's 403
export function coreSettings(table: Readonly<Record<string, unknown>>): CoreSettings;  // as parseCoreSettings takes it; shares its name with #core's default-filling coreSettings: import one under an alias

// #app, results: AddOutcome (and HELD: "held for approval", Task 12b), Read, Shown, Listed, Added, Written,
// ThreadList, ThreadShown, ThreadsWaiting, Behind, as results.py, fields in camelCase;
// Added gains awaits: string | null and held: number | null (Task 12b);
// Written gains awaits: string | null and held: number | null, both filled null by written() (Task 12c).

// #app, the operations
export class Lodge {
  constructor(store: Store, clock: Clock, ids: IdSource, settings: CoreSettings, actor: Actor);  // actor: Task 11
  search(query: string, filters: Filters, options?: { limit?: number }): Promise<Listed>;
  show(ref: string, options?: { reasoning?: boolean; provenance?: boolean }): Promise<Shown>;
  waitingAll(): Promise<readonly [Listed, ThreadsWaiting]>;
  timeline(options?: { limit?: number }): Promise<Listed>;
  spec(options?: { area?: string | null }): Promise<readonly [string, Read, readonly SpecArea[]]>;
  problems(): Promise<readonly [CheckResult, Read]>;
  check(gate: boolean): Promise<readonly [CheckResult, Read]>;
  draft(ref: string): Promise<string>;
  mint(prefix: "d" | "s"): Promise<string>;
  add(drafts: readonly (readonly [string, string])[], options?: { importing?: boolean; dryRun?: boolean; attachments?: readonly (readonly [string, string])[] }): Promise<Added>;
  ask(ref: string, raises: Raises, by: string, text: string, options?: { where?: string | null; when?: string | null; commit?: boolean }): Promise<Written>;
  reply(thread: string, by: string, text: string, options?: { where?: string | null; when?: string | null; commit?: boolean }): Promise<Written>;
  close(thread: string, by: string, options?: { text?: string | null; where?: string | null; when?: string | null; commit?: boolean }): Promise<Written>;
  threads(): Promise<ThreadList>;
  thread(ref: string): Promise<ThreadShown>;
  threadsWaiting(): Promise<ThreadsWaiting>;
  confirm(ids: readonly string[], words: string, options?: { area?: string | null; commit?: boolean }): Promise<Written>;
  behindArea(name: string): Promise<readonly Behind[]>;
  held(): Promise<readonly Held[]>;                          // added, Task 12b
  approve(seq: number): Promise<Approved>;                   // added, Task 12b; a held message's approval, Task 12c
  decline(seq: number, reason: string): Promise<void>;       // added, Task 12b
}

// #store
export interface LodgeDatabase { readonly db: Kysely<Tables>; close(): Promise<void> }
export function openDatabase(path: string): Promise<LodgeDatabase>;   // ":memory:" or a file; creates or checks the schema
export class SqliteStore implements Store { constructor(database: LodgeDatabase, project: string, actor: string, clock: Clock) }
export class SqliteProjects implements Projects { constructor(database: LodgeDatabase, clock: Clock) }
export function rebuild(database: LodgeDatabase): Promise<void>;       // every derived table from the events
export interface Tables { events: EventsTable; heads: HeadsTable; files: FilesTable; members: MembersTable; held: HeldTable }  // held: Task 12a
```

- The events table (d-wje1cn): `events(seq integer primary key autoincrement, project text not null, at text not null, actor text not null, kind text not null, path text, body blob not null, message text)`, refused `update` and `delete` by two triggers raising `events are append-only` (probe 3); plan 2's kinds are `project`, `member`, `file`, `held`, `approved`, and `declined`, a `file` event's body the file's bytes and every other body UTF-8 JSON.
- A later plan adds an event kind by adding its case to `applyEvent` of `store/events.ts`, which both a write and `rebuild` run, and a derived table to `Tables`, `openDatabase`'s schema (raising `user_version`), and `rebuild`'s list; nothing ever updates or deletes an event.
- `applyEvent` inserts the project's `heads` row only for a `project` event; for every other kind it runs `update heads set rev = <seq> where project = <project>`, never an upsert, so an event whose `project` names no project (plan 3's account events, whose `project` is the empty text) adds no `heads` row.
- `Store.publish` refuses, before it writes anything, what lodge 0.2's `check_writes` refuses (`src/lodge/gitstore/plumbing.py:14-25`) with its two messages, a path holding a surrogate, and a changed text for a decision file the base holds (d-j28rp0, replacing d-pmaw3a); it runs no other check: `app` checks before it calls it (d-fv20kp), and plan 4's import, which publishes a lodge 0.2 store's files through the project's store into an empty project, checks that store with lodge 0.2's state check first; a test that writes through `publish` directly stands for a hand edit of lodge 0.2 that leaves decisions and attachments as they are.
- Every store transaction that reads before it writes opens with a write on the project's `heads` row (d-thvvzx, probe 4): `publish` with its compare-and-set, `create` with an insert that does nothing on an existing name, and `addMember`, `decline`, and an approving `publish` with an update that keeps the revision (probe 8).
- The SQLite store answers `trees()` with one tree twice, `gate(current)` with `gate({ published: current, checked: [["", current]] })`, `freshness()` with `null`, and `commit(…)` with `committed({ outcome: CommitOutcome.FAILED, detail: "the server keeps no checkout; its writes are published at once" })`, and `publish` never answers `STAGED` (d-ae1vn5).
- A person's name is `^[a-z][a-z0-9-]{0,31}$` and a project's `^[a-z0-9][a-z0-9-]{0,62}$` (d-wx7d0f); `decided_by` names a person when it names an owner of the project, `Tree.people` being the owners (d-vwsnz5, design lines 74 and 261); a name the project's records use as `decided_by` or as a thread message's `by` cannot join it.
- A thread message whose `by` names a person (d-2v8vtk): from that person it is published at once; from another person it is refused with `Forbidden` (Task 11); from an agent, with where and when, it is held as a `HeldMessage` and published only when that person approves it, the thread waiting for that person meanwhile (Task 12c).

## Tasks and lanes

| Task | What | Waits for | Lane |
|---|---|---|---|
| 1 | Setup: Kysely in `ts/package.json` (coordinator) | plan 1 merged | |
| 2 | App ports, results, errors, and time | 1 | A |
| 3 | State, writes, and `Lodge`'s writes | 2 | A |
| 4 | Reads, threads, and `Lodge`'s reads | 3 | A |
| 5 | The thread tests | 4 | A |
| 6 | Confirmations and `#app`'s front door | 5 | A |
| 7a | The byte codec, the database, and its events | 2 | B |
| 7b | The SQLite store and projects | 3, 7a | B |
| 8 | Two writers at once | 7b | B |
| 9 | The check on every write, over the events store | 6, 8 | |
| 10 | People in the core | 1 | C |
| 11 | People in the operations and the store | 9, 10 | |
| 12a | Held drafts in the port and both stores | 11 | |
| 12b | A person's decision drafted by another waits for that person | 12a | |
| 12c | A person's words relayed into a thread wait for that person | 12b | |
| 13 | Review flags per person | 10 | C |
| 14 | Closing checks | every task | |

Lanes A, B, and C run in parallel in their own worktrees, merged into `server-store` as each task passes its review (Tasks 2 and 7a both edit `ts/package.json`'s `imports` and `ts/knip.json`'s one-line `entry`, so the second merge meets a textual conflict, which the integrator resolves by keeping both sides), as plan 1's lanes are (d-xdqsmf, recorded on `server-core` and here once plan 1 merges); within a lane, tasks run in order.
The import graph decides the lanes (d-d96y91): lane B's code and tests need only `#app`'s ports, `Lodge.add`, and `tests/app/support.ts` (Tasks 2 and 3), reading the store through `load` of `#core` where a later task's `show` would do; lane C touches only `ts/src/core` and `ts/tests/core`, which no task of lanes A and B edits except Task 7a's `text.ts` and `fileformat.ts`, which lane C does not touch.
Lane C's new parameters (`people` of `isAuthor`, `parseThread`, and `writeThread`) default to `author` alone, so lane A's `app/threads.ts` and plan 1's carried tests compile whichever lane merges first.
Tasks 11 and 13 may also run in parallel, since Task 13 touches only the core's derivation, views, and feedback, and Task 11 only the operations, the store, and their tests; Task 11's test reads a flag's feedback by its first words, which Task 13 keeps.
Tasks 9, 11, 12a, 12b, and 12c run in that order, since each edits or extends the tests or modules the one before it wrote; in `app` the imports run `held.ts → threads.ts → writes.ts → awaits.ts` and `held.ts → writes.ts`, and neither `threads.ts` nor `writes.ts` imports `held.ts`, so plan 1's `no-circular` rule holds.

---

### Task 1: Setup

The coordinator does this task outside the sandbox, since it installs a package (brief; d-4psbdv).

**Files:**
- Modify: `ts/package.json` (`dependencies` gains `"kysely": "0.29.7"`), `ts/knip.json` (`ignoreDependencies` gains `"kysely"`, since no code imports it before Task 7a, which takes it out), `ts/bun.lock` (by `bun install`)

**Interfaces:**
- Produces: Kysely 0.29.7 installed, pinned exactly, published 2026-10-17 (plan 1's probe 11), at least two weeks before this plan (d-4psbdv).

- [ ] **Step 1:** In `ts/`, add the dependency, `bun install`, then `bun install --frozen-lockfile`, then `bun x biome format --write package.json knip.json`.
- [ ] **Step 2: Verify** `grep -c '"[~^]' ts/package.json` prints 0; `sh scripts/check.sh` exits 0.
- [ ] **Step 3:** Commit the three files and push; the ledger line names the version.

### Task 2: App ports, results, errors, and time

**Files:**
- Port: `src/lodge/app/errors.py`, `ports.py`, `results.py`
- Create: `ts/src/app/errors.ts`, `ts/src/app/ports.ts`, `ts/src/app/results.ts`, `ts/src/app/time.ts`, `ts/src/app/index.ts`, `ts/tests/app/fakes.ts`
- Modify: `ts/package.json` (`imports` gains `"#app": "./src/app/index.ts"`, no dependency), `ts/tests/parity.json` (`tests/app/fakes.py` to `ported`), `ts/knip.json` (`tests/app/fakes.ts` into `entry`, d-tha8st)
- Test: `ts/tests/app/time.test.ts`, `ts/tests/app/ports.test.ts`, `ts/tests/app/errors.test.ts` (new)

**Interfaces:**
- Consumes: plan 1's `#core`.
- Produces, through `#app`: the ports, errors, and results of "Interfaces for plans 3 and 4" as of this task: `Now`, `Clock`, `IdSource`, `PublishOutcome`, `CommitOutcome`, `Committed` and `committed`, `Gate` and `gate`, `Store` (the five methods of `ports.py` and `attachmentTexts`, no `approves`, `hold`, `held`, or `decline` yet), `Actor`, `person`, `agent`, `actorText`, `Role`, `Projects`, `stampOf`, `minuteOf`; `LodgeError`, `NotFound`, `Conflict`, `StaleList`, `coreSettings`; `AddOutcome` (without `HELD`), `Read` and `read`, `Shown`, `Listed` and `listed`, `Added` and `added`, `Written` and `written`, `ThreadList`, `ThreadShown`, `ThreadsWaiting`, `Behind`.
- The default-filling functions are those of probe 5: `committed` (detail `""`), `gate` (notes `[]`), `read` (statuses an empty `Map`), `listed` (more `0`), `added` (freshness `null`, minted `[]`, paths `[]`), and `written` (committed `null`, about `null`); `Shown` has none, since every call passes all its fields (probe 5).
- `LodgeError` extends `Error` with `exitCode` 2 and `name` its class name; `Conflict` sets `exitCode` 1, and `StaleList` extends it; `NotFound` extends `LodgeError`.
- `coreSettings(table)` calls `parseCoreSettings` and throws `new LodgeError(".lodge.toml: " + message)` for a `SettingsError`, as `src/lodge/app/errors.py:28-33`; it shares its name with `#core`'s default-filling `coreSettings`, so `errors.ts` imports that one as `import { coreSettings as defaultCoreSettings }` if it needs it.
- `Store.attachmentTexts()` is an addition for plan 4's export, which writes every file of the project; `MemoryStore` answers with its files under `lodge/attachments/`.
- `Actor`, `person`, `agent`, `actorText`, `Role`, `Projects`, `stampOf`, and `minuteOf` are additions (d-vwsnz5, d-wx7d0f), declared here so that lanes B and C build on one port: `actorText(person("ada"))` is `"ada"`, `actorText(agent())` is `"agent"`, and `actorText(agent("builder"))` is `"agent builder"`.
- `time.ts`, exported through `#app` as additions, since the store stamps its events with them (Task 7b):
  ```ts
  export function stampOf(now: Now): string    // datetime.isoformat(timespec="seconds"): "2026-10-29T09:30:00+01:00"
  export function minuteOf(now: Now): string   // strftime(MINUTE_FORMAT), "%Y-%m-%d %H:%M" in the offset's own time: "2026-10-29 09:30"
  ```
  Both compute from `new Date(now.epochMs + now.offsetMinutes * 60_000)` and its UTC methods (d-mfskz3), the offset written `+HH:MM` or `-HH:MM`, `+00:00` for zero.
- `fakes.ts` carries `tests/app/fakes.py`; its constructors stay positional, since d-vd3175 binds `app` only, so the carried keyword calls are written out: `CountingIds(step=0)` (`tests/app/test_writes.py:149`) is `new CountingIds(1, 0)`, `CountingIds(first=9, step=-1)` (`tests/app/test_thread_ops.py:186`) is `new CountingIds(9, -1)`, and `FixedClock(step=timedelta(seconds=1))` (`tests/app/test_writes.py:39`) is `new FixedClock(START, 1000)`:
  - `START: Now`, 2026-10-29 09:30 at offset +01:00 (`epochMs` from `instant("2026-10-29T09:30:00+01:00")` of `#core`, `offsetMinutes` 60);
  - `MemoryStore(items: (Area | Decision | SpecEntry)[] = [], options: { staged?: boolean } = {})`, building its trees with `tree()` of `#core`, with `files` and `published` as `Map`s, `staged`, `rev`, `commits`, `commitResult`, `stamp`, `publishes` (each `[Map, message]`), `attempts`, `gateFor`, and `movesAfterRead` and `rejectNext`, its methods `async` and otherwise line for line `fakes.py`'s;
  - `FixedClock(start: Now = START, stepMs = 0)`, with `calls`, `slept` (seconds), `now()`, and `async sleep(seconds)`, which adds `seconds * 1000` to `start`;
  - `CountingIds(first = 1, step = 1)`, with `draws` and `entropy()` giving six equal bytes.
- `filesOf` and the builders come from `ts/tests/core/builders.ts`, as `fakes.py` imports them from `builders`.

- [ ] **Step 1: Write the failing tests.**
  - `time.test.ts`: `stamp_keeps_the_offset` (`START` gives `2026-10-29T09:30:00+01:00`, and `isStamp` of `#core` accepts it); `stamp_drops_the_fraction` (`START` plus 999 ms gives the same stamp); `negative_and_zero_offsets` (offset -150 gives `-02:30`, offset 0 gives `+00:00`); `minute_is_local_to_the_offset` (`START` gives `2026-10-29 09:30`, and the same instant at offset 0 gives `2026-10-29 08:30`); `minute_crosses_midnight` (23:59 UTC at offset +60 gives the next day's `00:59`).
  - `ports.test.ts`: `actor_text_names_the_person_or_the_role`; `default_filling_functions_fill_python_defaults` (each of the six against the defaults above).
  - `errors.test.ts`: `exit_codes_follow_lodge_0_2` (`LodgeError` 2, `NotFound` 2, `Conflict` 1, `StaleList` 1, each `instanceof` its base); `core_settings_reports_a_bad_table_as_a_lodge_error` (a `[length]` table with a negative number throws a `LodgeError` whose message starts `.lodge.toml: `).
- [ ] **Step 2: Run** `cd ts && bun test tests/app`; expected: the new tests FAIL.
- [ ] **Step 3: Implement** the interfaces above, `ts/tests/app/fakes.ts` with them; add `#app` to `package.json`'s `imports` and `tests/app/fakes.ts` to `ts/knip.json`'s `entry`.
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; green; flip `tests/app/fakes.py` to `ported`; run it again.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 3: State, writes, and `Lodge`'s writes

**Files:**
- Port: `src/lodge/app/state.py`, `writes.py`; of `lodge.py`, the constructor, `mint`, and `add` (d-t7er56)
- Create: `ts/src/app/state.ts`, `ts/src/app/writes.ts`, `ts/src/app/lodge.ts`, `ts/tests/app/support.ts`
- Modify: `ts/src/app/index.ts` (`Lodge`), `ts/tests/parity.json`, `ts/knip.json` (`src/app/state.ts`, `src/app/writes.ts`, and `tests/app/support.ts` into `entry`; `tests/app/fakes.ts` out of it, since this task's tests read all four of its names, d-tha8st)
- Test: `ts/tests/app/writes-attach.test.ts` (carried); `ts/tests/app/writes.test.ts` (carried in part: the thirteen tests below, which call only `add` and `mint`; Task 4 adds the other six and flips the row)

**Interfaces:**
- Consumes: Task 2.
- Produces, through `#app`: `Lodge` with `constructor(store, clock, ids, settings)`, `mint(prefix)`, and `add(drafts, { importing = false, dryRun = false, attachments = [] })`; Task 11 adds the actor.
- Module-internal, first read by Task 4: `readChecked`, `resolveRef`, and `notFound` of `state.ts`, and `mintUnused` of `writes.ts`; `Wiring`, `State`, and `readState` are read in this task by `writes.ts` and `lodge.ts`.
- `writes.ts` is line for line `writes.py`, with these readings:
  - `_after_newest` takes the newest decision's instant from `instant` of `#core` (a stored date is always a stamp, since `read_date` writes a bare day back as midnight UTC); `(newest - now).total_seconds() > _WAITS` is `(newestMs - now.epochMs) / 1000 > WAITS`; `now.replace(microsecond=0) > newest` is `Math.floor(now.epochMs / 1000) * 1000 > newestMs`; and `clock.sleep(1.0 - now.microsecond / 1_000_000)` is `await clock.sleep(1 - (now.epochMs % 1000) / 1000)`;
  - `now.isoformat(timespec="seconds")` is `stampOf(now)`, and `check_change`'s `now` is that stamp (plan 1, Task 8b);
  - the after-state is built with `tree({ rev, files, attachments })` of `#core`, never a `Tree` literal, so that it still compiles once Task 10 adds `people` to `Tree`, and Task 11 then passes `people: current.people` in that one place;
  - `_attached`'s `{name!r}` is `pyRepr(name)` of `#core`.
- `Wiring` is declared in `state.ts`, as `src/lodge/app/state.py:24` has it, and `lodge.ts` holds a `Wiring` value and delegates as `lodge.py` does, so `state.ts` and `writes.ts` import nothing of `lodge.ts` and plan 1's `no-circular` rule holds; this task writes the constructor and the two methods, and Tasks 4 and 6 add the rest (d-t7er56).
- `support.ts` carries `tests/app/support.py` and `conftest.py` (whose only content is the path to the core's test helpers, which TypeScript imports by path): `AREA`, `ENTRY`, `FIRST`, `project({ staged = false } = {})`, and `wired(store: Store, clock = new FixedClock(), ids = new CountingIds())`, typed by the port so that Task 9 passes a `SqliteStore` or an `Interleaving` (Python's annotation names `MemoryStore`, `tests/app/support.py:26-29`).
- `add_fills_id_and_date_from_ports`'s `START.replace(microsecond=999_999)` (`tests/app/test_writes.py:32`) is `START` plus 999 ms, since `Now` counts milliseconds; the test asserts the same date.
- The thirteen tests of `tests/app/test_writes.py` that call only `add` or `mint` are this task's, so they are red for want of the code they test: `add_new_decision_entry_area`, `add_fills_id_and_date_from_ports`, `add_date_and_check_time_from_one_reading`, `add_failing_check_publishes_nothing`, `add_returns_feedback_and_notes`, `add_refuses_unreadable_or_unusable_drafts`, `add_imports_only_when_asked`, `dry_run_publishes_nothing`, `dry_run_reports_feedback_and_check`, `mint_skips_taken`, `mint_gives_up_after_ten_draws`, `add_area_sharing_a_rank_gives_feedback`, and `rest_on_entry_retired_in_the_same_add_is_refused`.

- [ ] **Step 1: Write the failing tests:** every test of `tests/app/test_writes_attach.py` by name, and the thirteen tests of `tests/app/test_writes.py` above into `writes.test.ts`, `await`ing each operation.
- [ ] **Step 2: Run** `cd ts && bun test tests/app`; expected: the new tests FAIL.
- [ ] **Step 3: Implement**; put the three files into `ts/knip.json`'s `entry`, and take `tests/app/fakes.ts` out of it.
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; green; flip `tests/app/conftest.py`, `tests/app/support.py`, and `tests/app/test_writes_attach.py` to `ported`; run it again.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 4: Reads, threads, and `Lodge`'s reads

**Files:**
- Port: `src/lodge/app/reads.py`, `threads.py`; of `lodge.py`, every method that delegates to them
- Create: `ts/src/app/reads.ts`, `ts/src/app/threads.ts`
- Modify: `ts/src/app/lodge.ts`, `ts/tests/parity.json`, `ts/knip.json` (`tests/app/support.ts`, `src/app/state.ts`, and `src/app/writes.ts` leave `entry`)
- Test: `ts/tests/app/reads.test.ts` and `ts/tests/app/reads-checks.test.ts`, `ts/tests/app/writes.test.ts` (the other six tests), `ts/tests/app/writes-dates.test.ts` (carried)

**Interfaces:**
- Consumes: Task 3.
- Produces, through `#app`: `Lodge`'s `search`, `show`, `waitingAll`, `timeline`, `spec`, `problems`, `check`, `draft`, `ask`, `reply`, `close`, `threads`, `thread`, and `threadsWaiting`, with the signatures of "Interfaces for plans 3 and 4".
- `reads.py`'s one `datetime.fromisoformat(d.date)` ordering (`_newest_first`, `src/lodge/app/reads.py:126-130`) sorts by `instant` of `#core` and then the ID, both descending, since Python sorts the pair with `reverse=True`, the reverse of plan 1's ascending `newestLast`; `threads.py` has none, and `writes.py`'s is Task 3's `afterNewest`; `writes-dates.test.ts`'s `NEWEST`, `datetime.fromisoformat(FIRST.date)` (`tests/app/test_writes_dates.py:11`), is the `Now` `{ epochMs: instant(FIRST.date), offsetMinutes: 60 }`, `FIRST`'s date being written at `+01:00` (`at()` of `ts/tests/core/builders.ts`); `now.strftime(core.MINUTE_FORMAT)` is `minuteOf(now)`, and `now.isoformat(timespec="seconds")` is `stampOf(now)`.
- `threads.ts` builds the after-state with `tree({ … })` of `#core`, as Task 3's writes do, and catches only the `ValueError` of `#core` around `writeThread(thread)`, called with one argument as plan 1 ported it (`src/lodge/app/threads.py:80-83`); Python's `threads.write` is `writeMessage` in TypeScript, since plan 1's call rule reports a call named `write` outside `git` as file writing (`ts/tests/structure/calls.ts`, its `writes` set), and `lodge.ts` calls `threads.writeMessage`.
- `reads.check`'s `found` keys problems by value, as Python's `dict[Problem, …]` does: the key is `JSON.stringify([path, check, line, message])`, and the order is `_by_position`'s, sorting by path and message by code point.
- `tests/app/test_reads.py` (282 lines) is ported into two files, since plan 1's ports ran about 1.1 times their Python lines and `tests/` is held to 300 lines (practice review P-I5): `reads.test.ts` takes the tests of its lines 14 to 142 (`show_of_an_entry_carries_the_deciding_views_with_its_reasoning`, `show_resolves_code_and_levels`, `show_unknown_ref_is_an_error`, `show_ambiguous_code_is_an_error`, `show_flags_a_failing_record`, `search_listed_with_read`, `search_honours_filters`, `unparsable_file_reported_by_every_read`, `waiting_lists_flagged`, `timeline_newest_first_and_limited`, and `spec_renders_and_narrows_to_an_area`), and `reads-checks.test.ts` the rest (`problems_run_the_one_state_checks`, the four `check_gate_…` tests, `draft_prints_file_with_base`, `draft_area`, `core_settings_error_becomes_lodge_error`, the three `not_found_…` tests, `timeline_refuses_a_negative_limit`, and `search_says_how_many_more_matched_beyond_the_limit`); the row's `ts` names both.
- The six remaining tests of `tests/app/test_writes.py` (`add_stale_base_conflicts_writes_nothing`, `feedback_skips_edited_decisions_which_the_check_refuses`, `staged_second_edit_builds_on_first`, `unchanged_draft_publishes_nothing`, `only_changed_files_are_published`, and `cycle_made_in_one_add_is_refused`) and the six of `test_writes_dates.py` call `draft`, which this task ports, so they are red for want of `draft` first; each is then seen failing against a targeted mutation of Task 3's code, listed in the report as a table of test and mutation: for the six date tests, mutations of `afterNewest` such as the sleep skipped, the sleep fixed at one second, `> WAITS` read as `>= WAITS`, and the whole-second comparison made on milliseconds.

- [ ] **Step 1: Write the failing tests:** every test of `tests/app/test_reads.py` (in the two files above), the six remaining tests of `test_writes.py`, and every test of `test_writes_dates.py`, by name.
- [ ] **Step 2: Run** `cd ts && bun test tests/app`; expected: the new tests FAIL; once `draft` exists, run the twelve write tests against their mutations, each FAIL, then revert.
- [ ] **Step 3: Implement**; take the three files out of `ts/knip.json`'s `entry`.
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; green, knip reporting no unused export; flip the three files to `ported`; run it again.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 5: The thread tests

**Files:**
- Modify: `ts/tests/parity.json` (`tests/app/test_thread_ops.py` to `ported`; `tests/app/test_thread_fix_paths.py` to plan 3, d-rp74dr); Task 4's modules only where a carried test finds them wrong
- Test: `ts/tests/app/thread-ops.test.ts` and `ts/tests/app/thread-ops-publish.test.ts`, `ts/tests/app/thread-fix-paths.test.ts` (carried)

**Interfaces:**
- Consumes: Task 4.
- Produces: no new name.
- These tests carry over code Task 4 ported, so each is seen failing against a targeted mutation of that code, listed in the report as a table of test and mutation, then reverted (d-mfayy5).
- `tests/app/test_thread_ops.py` (250 lines) is ported into two files, as Task 4 splits `test_reads.py` (P-I5): `thread-ops.test.ts` takes the tests of its lines 28 to 155, which write messages and refuse them (`ask_writes_a_thread_file` to `close_with_text`), and `thread-ops-publish.test.ts` the tests from line 156 on, which publish, commit, list, and wait (`rejected_publish_starts_again` to `three_rejections_are_a_conflict`); the row's `ts` names both.
- `thread-fix-paths.test.ts` holds `waiting_reads_one_snapshot` as a test, and `orphaned_thread_outputs` and `run_thread_outcomes` as `test.todo`s, since they call the command's `thread_head`, `thread_text`, `waiting_text`, and `run_thread` (`tests/app/test_thread_fix_paths.py:9-10`), which plan 3 ports; its row stays `planned`, its `plan` becomes 3, and plan 3's command task turns the two `test.todo`s into tests and flips it (d-rp74dr).

- [ ] **Step 1: Write** every test of `tests/app/test_thread_ops.py` by name, and `thread-fix-paths.test.ts` as above.
- [ ] **Step 2: Run** each against a mutation of Task 4's code that the report names; expected: FAIL; revert.
- [ ] **Step 3: Run** `sh scripts/check-ts.sh`; green; flip `tests/app/test_thread_ops.py` to `ported`, and set `tests/app/test_thread_fix_paths.py`'s `plan` to 3.
- [ ] **Step 4: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 6: Confirmations and `#app`'s front door

**Files:**
- Port: `src/lodge/app/confirm.py`; of `lodge.py`, `confirm` and `behind_area`
- Create: `ts/src/app/confirm.ts`
- Modify: `ts/src/app/lodge.ts`, `ts/src/app/index.ts`, `ts/tests/parity.json`
- Test: `ts/tests/app/confirm.test.ts` (carried); `ts/tests/app/front-door.test.ts` (new)

**Interfaces:**
- Consumes: Task 5.
- Produces, through `#app`: `Lodge`'s `confirm(ids, words, { area = null, commit = false })` and `behindArea(name)`; with them `index.ts` exports every name of `src/lodge/app/__init__.py`'s `__all__` in camelCase.
- `confirm.py`'s docstring about the viewer's lock (`src/lodge/app/confirm.py:52-57`) becomes a comment saying that callers serialise confirmations; plan 3 decides how the API does.
- `w.clock.now().strftime(core.MINUTE_FORMAT)` is `minuteOf(clock.now())`.
- `front-door.test.ts`: `front_door_exports_every_python_name` reads `__all__` of `../src/lodge/app/__init__.py` and the export names of `ts/src/app/index.ts` with TypeScript's parser, as plan 1's Task 11 does for `#core`, and finds each Python name, a `snake_case` name in camelCase; `front_door_exports_nothing_else` finds every other export among this plan's additions: the default-filling functions of probe 5 and `Now`, `Actor`, `person`, `agent`, `actorText`, `Role`, `Projects`, `stampOf`, `minuteOf`, `Forbidden`, `HeldDraft`, `HeldAdd`, `HeldMessage`, `Held`, and `Approved`, the last six listed now and exported by Tasks 11, 12a, and 12b.

- [ ] **Step 1: Write the failing tests:** every test of `tests/app/test_confirm.py` by name, and `front-door.test.ts`.
- [ ] **Step 2: Run** `cd ts && bun test tests/app`; expected: the new tests FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; green; flip `tests/app/test_confirm.py` to `ported`; then every `tests/app/` row is `ported` or `changed`, but for `test_thread_fix_paths.py` (plan 3).
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 7a: The byte codec, the database, and its events

**Files:**
- Create: `ts/src/store/index.ts`, `ts/src/store/schema.ts`, `ts/src/store/events.ts`
- Modify: `ts/src/core/text.ts` (`encodeUtf8`, `decodeUtf8`), `ts/src/core/fileformat.ts` (`contentHash` encodes through `encodeUtf8`, d-0q54zn), `ts/package.json` (`imports` gains `"#store": "./src/store/index.ts"`, no dependency), `ts/knip.json` (`kysely` leaves `ignoreDependencies`; `src/store/events.ts` goes into `entry`), `ts/.dependency-cruiser.cjs` (the rule `store-imports`), `ts/tests/structure/table.ts` (`STORE_NPM`), `ts/tests/structure/table.test.ts`, and `ts/tests/structure/imports.test.ts` (d-nf7wvx)
- Test: `ts/tests/core/bytes.test.ts`, `ts/tests/store/database.test.ts` (new)

**Interfaces:**
- Consumes: Task 2's ports; plan 1's `#core`.
- Produces, through `#core` (as names of `text.ts`, which plan 1's front-door test allows, d-hshapm):
  ```ts
  export function encodeUtf8(text: string): Uint8Array   // str.encode("utf-8", "surrogateescape"): U+DC80..U+DCFF become the byte 0x80..0xFF; any other lone surrogate throws a ValueError naming it with pyRepr
  export function decodeUtf8(bytes: Uint8Array): string  // bytes.decode("utf-8", "surrogateescape"): each byte of an invalid sequence becomes U+DC00 + byte
  ```
  `decodeUtf8` refuses what Python refuses, byte by byte: overlong forms, encoded surrogates, values beyond U+10FFFF, and truncated sequences each give one U+DCxx per byte (probe 7), and a broken sequence escapes only its own bytes, so the valid character after it is kept (`e2c2a9` gives U+DCE2 U+00A9, probe 11); `contentHash` hashes `encodeUtf8` of the normalised text, so `contentHash("a\uDC80\n")` is `518254327818` and a lone U+D83D throws the `ValueError`, as Python's `UnicodeEncodeError` is one (probe 7).
- Produces, through `#store`: `LodgeDatabase`, `Tables`, `openDatabase`, and `rebuild`, as in "Interfaces for plans 3 and 4".
- `schema.ts` (d-wje1cn):
  - `openDatabase(path)` opens `new Database(path, { strict: true, create: true })` of `bun:sqlite` and wraps it for Kysely as `probes/db.ts` does (plan 1's probe 1); it sets `PRAGMA journal_mode=WAL` and `PRAGMA busy_timeout=5000`, reads `PRAGMA user_version`, runs each migration above it in one transaction, and sets `user_version` to the number of migrations; a database whose `user_version` is above that is closed and refused with `LodgeError("the database at <path> has schema <n>, newer than this lodge's <m>")`.
  - It creates no folder: a file's folder must exist, so `store` keeps no file access of its own (d-x6f9za), and plan 3's entry point chooses the path.
  - `MIGRATIONS[0]` creates `events` (columns as in "Interfaces for plans 3 and 4"), the triggers `events_no_update` and `events_no_delete` (`before update` and `before delete on events`, `select raise(abort, 'events are append-only')`, probe 3), `heads(project text primary key, rev integer not null)`, `files(project text not null, path text not null, body blob not null, seq integer not null, primary key (project, path))`, and `members(project text not null, person text not null, role text not null, primary key (project, person))`.
  - The Kysely interfaces are `EventsTable` (`seq: Generated<number>`, `body: Uint8Array`, `path` and `message` `string | null`), `HeadsTable`, `FilesTable`, and `MembersTable`, declared without `export` beside the exported `Tables`, as is `MIGRATIONS`, so knip reports no unused export (practice review P-M2).
- The rule `store-imports` (d-nf7wvx), as probe 9 planted it: `from` `^src/store/`, `to` the `core`, `npm`, `npm-dev`, `npm-optional`, `npm-peer`, and `npm-no-pkg` dependency types with `pathNot` built from `STORE_NPM` (`["kysely"]`, exported by `ts/tests/structure/table.ts` beside `CORE_NPM`) and `bun:sqlite`; it allows `#app` and `#core`, which the existing rules govern.
- `events.ts`, module-internal but `rebuild`:
  ```ts
  interface NewEvent { readonly kind: string; readonly path: string | null; readonly body: Uint8Array; readonly message: string | null }  // exported only if another module names the type
  export async function appendEvents(tx: Transaction<Tables>, project: string, actor: string, at: string, events: readonly NewEvent[]): Promise<number>  // the last seq
  export function json(value: unknown): Uint8Array        // encodeUtf8(JSON.stringify(value))
  export async function rebuild(database: LodgeDatabase): Promise<void>
  ```
  `appendEvents` inserts each event and runs `applyEvent` (not exported) on the inserted row, so a write and `rebuild` fill the derived tables with one function; `applyEvent` sets `heads.rev` to the row's `seq` for every kind, by an insert that updates the row on a name already there for `project` and by `update heads set rev = <seq> where project = <project>` for every other kind, never an upsert, so an event of no project adds no `heads` row; it upserts `members` for `member` (`{ person, role }`) and `files` for `file` (path and bytes); an unknown kind throws, so a later plan cannot forget its case.
  `appendEvents` and `json` are first read by Task 7b, so `events.ts` is in `ts/knip.json`'s `entry` until then (d-tha8st).
- `rebuild(database)` deletes every row of `heads`, `files`, and `members` and replays every event in `seq` order through `applyEvent`, in one transaction; it never touches `events`.

- [ ] **Step 1: Write the failing tests.**
  - `bytes.test.ts`: `decode_utf8_like_surrogateescape` (`test.each` over probe 7's seven byte strings and probe 11's three, with their code points); `encode_utf8_reverses_decode` (each decoded text encodes back to its bytes); `encode_refuses_a_lone_surrogate_outside_the_escapes` (U+D83D and U+DC7F throw `ValueError`); `content_hash_encodes_escaped_bytes` (`518254327818`, probe 7).
  - `database.test.ts`: `schema_is_created_once` (opening one file twice keeps one schema at `user_version` 1); `newer_schema_is_refused` (a file whose `user_version` a raw `bun:sqlite` connection set to 9); `events_are_append_only` (an `update` and a `delete` through `database.db` each throw `events are append-only`, probe 3); `rebuild_derives_the_tables_from_raw_events` (events inserted through `database.db` for a `project`, a `member`, and two `file`s of one path give, after `rebuild`, one `heads` row at the last `seq`, the member, and the second file's bytes); `an_event_of_no_project_adds_no_head` (a raw `file` event whose `project` is the empty text, which no `project` event names, leaves `heads` without a row for it after `rebuild`, as plan 3's account events need).
  - `imports.test.ts`: `store_importing_another_package` (`yaml` from `src/store/a.ts`: one `store-imports` finding); `store_importing_node_builtin` (`node:fs`: `store-imports` and `file-confinement`); `store_imports_its_own` (`kysely`, `bun:sqlite`, `#app`, and `#core`: nothing); `table.test.ts` expects `STORE_NPM` to be `["kysely"]`.
- [ ] **Step 2: Run** `cd ts && bun test tests/store tests/core/bytes.test.ts`; expected: the new tests FAIL.
- [ ] **Step 3: Implement**; add `#store` to `package.json`'s `imports`, take `kysely` out of `ts/knip.json`'s `ignoreDependencies`, and put `src/store/events.ts` into its `entry`.
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; green, dependency-cruiser reporting no `file-confinement`, `sqlite-confinement`, or `store-imports` violation.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 7b: The SQLite store and projects

**Files:**
- Create: `ts/src/store/sqlite-store.ts`, `ts/src/store/projects.ts`, `ts/src/store/read-tree.ts` (module-internal: `readTree(tx, project)`, the project's tree as `trees()` gives it, for `trees()` and `addMember`)
- Modify: `ts/src/store/index.ts`, `ts/knip.json` (`src/store/events.ts` leaves `entry`)
- Test: `ts/tests/store/projects.test.ts`, `ts/tests/store/sqlite-store.test.ts` and `ts/tests/store/sqlite-store-refusals.test.ts`, `ts/tests/store/rebuild.test.ts` (new)

**Interfaces:**
- Consumes: Tasks 3 and 7a (`Lodge.add`, `AREA` of `tests/app/support.ts`, and `filesOf` of `ts/tests/core/builders.ts` for `lodge_adds_through_the_store`); no test of this task calls an operation of Task 4 or later (d-d96y91).
- Produces, through `#store`: `SqliteStore` and `SqliteProjects`, as in "Interfaces for plans 3 and 4".
- `SqliteStore(database, project, actor, clock)` implements `Store` (d-ae1vn5):
  - `trees()` reads `heads` and `files` of the project in one transaction; an unknown project throws `NotFound("no project named <project>")`; the tree is `tree({ rev: String(rev), files, attachments })` of `#core`, a path under `lodge/attachments/` listed in `attachments` and never decoded, every other path in `files` as `decodeUtf8` of its bytes; it returns that one tree as both the current and the published state.
  - `publish(base, writes, message)` first refuses, writing nothing, each path in `writes` that lodge 0.2's `check_writes` refuses (`src/lodge/gitstore/plumbing.py:14-25`, ported line for line with its two messages): a path whose first part is not `lodge`, with one part only, holding a backslash or a NUL, or with an empty, `.`, `..`, or `.git` part throws `LodgeError("<path> is outside lodge/, which is all the store writes")`, and a path in `base.attachments` throws `LodgeError("<path> is an attachment, and lodge never overwrites an attachment")`; then a path holding any surrogate throws `LodgeError("<path>: a path holding a lone surrogate cannot be stored")`, since the `path` column is `text` (probe 1, d-j28rp0); then a path under `lodge/decisions/` that `base.files` holds with another text throws `LodgeError("<path> is a published decision, and lodge never rewrites a decision")` (d-j28rp0); `base` is the state the compare-and-set below must match, so checking against it is checking against the state written onto; it then encodes every text with `encodeUtf8` (a `ValueError` becomes `LodgeError("<path>: <message>")`), then in one transaction runs, as its first statement, `update heads set rev = rev where project = :project and rev = :base` (probes 4 and 8): no row matched, or a `base.rev` that is not a decimal, answers `REJECTED` and writes nothing; otherwise it appends one `file` event per path of `writes` in the map's order, each with the message, the actor, and `at` = `stampOf(clock.now())` of `#app`, and answers `PUBLISHED`.
  - `attachmentTexts()` reads the project's files under `lodge/attachments/` and decodes each with `decodeUtf8`.
  - `freshness()` answers `null`, `gate(current)` `gate({ published: current, checked: [["", current]] })`, and `commit()` the `FAILED` outcome of "Interfaces for plans 3 and 4"; none reads or writes.
- `SqliteProjects(database, clock)` implements `Projects` (d-wx7d0f):
  - `create(project, owner)` checks both names, then in one transaction whose first statement is `insert into heads (project, rev) values (:project, 0) on conflict do nothing` (d-thvvzx): no row inserted throws `Conflict("a project named <project> exists")`; otherwise it appends a `project` event (`{ owner }`) and a `member` event (`{ person: owner, role: "owner" }`), the actor being the owner;
  - `members(project)` gives the members by name in code-point order, `NotFound` for an unknown project;
  - `addMember(project, person, role, by)` checks the name, then in one transaction whose first statement is `update heads set rev = rev where project = :project` (no row: `NotFound`, d-thvvzx) refuses a member already there with `Conflict("<person> is a member of <project>")` and a name that the project's current state (`readTree` and `load` of `#core`) uses as the `decidedBy` of a decision or the `by` of a thread message with `Conflict("<person> is a role in <id>, so it cannot name a person")`, `<id>` the first such record in code-point order (d-vwsnz5), and appends a `member` event, the actor being `actorText(by)`;
  - `storeFor(project, actor)` gives `new SqliteStore(database, project, actorText(actor), clock)`;
  - a bad name throws `LodgeError("<name> is not a project name: …")` or `"… is not a person's name: …"`, with the pattern.

- [ ] **Step 1: Write the failing tests.**
  - `projects.test.ts`: `create_writes_the_project_and_its_owner` (two events in order, `members` gives `ada` as owner); `existing_project_conflicts`; `names_are_checked` (`Lodge`, `-x`, and a 64-character project name; `Ada` and `1ada` as persons); `add_member_needs_a_new_name`; `unknown_project_is_not_found`.
  - `sqlite-store.test.ts` and `sqlite-store-refusals.test.ts`, split so neither nears 300 lines: the second holds `lone_surrogate_outside_the_escapes_is_refused`, `path_outside_lodge_is_refused`, `a_path_holding_a_surrogate_is_refused`, `an_attachment_is_never_overwritten`, and `a_published_decision_is_never_rewritten`, and the first the rest: `trees_give_one_state`; `a_write_is_one_event_per_file` (kind, path, message, actor `ada`, `at` the clock's stamp); `file_bytes_survive_exactly` (a text starting with U+FEFF, CRLF, U+0000, an astral character, and U+DC80, read back equal, the last stored as the byte 0x80; probes 1 and 2); `lone_surrogate_outside_the_escapes_is_refused` (no event written); `stale_base_is_rejected_and_writes_nothing`; `attachments_are_listed_not_read` (in `attachments` of the tree, not in `files`, and given back by `attachmentTexts`); `gate_compares_the_current_state_with_itself`; `freshness_is_null_and_commit_is_refused`; `path_outside_lodge_is_refused` (`test.each` over `notes/x`, `lodge`, `lodge/../x`, `lodge//x`, `lodge/./x`, `lodge/.git/x`, and the TypeScript strings `"lodge\\x"` and `"lodge/x\0"`, each refused with lodge 0.2's message and no event written); `a_path_holding_a_surrogate_is_refused`; `an_attachment_is_never_overwritten` (a second publish of an attachment path the tree holds is refused and `attachmentTexts` keeps the first text); `a_published_decision_is_never_rewritten` (a publish changing a decision file's text is refused, no event written, even when only the rendering differs and the fields are the same, which d-j28rp0 accepts; one writing it with its own text is accepted); `lodge_adds_through_the_store` (`Lodge` over a `SqliteStore` whose project holds `filesOf(AREA)`, published through `publish`, adds a decision of `coordinator` creating `s-bbbbbb` with its entry and the attachment `run.log`, drafted in the test with `decisionText` and `specText` of `ts/tests/core/applying.ts`, since `writes-attach.test.ts`'s drafts are locals of a test file; the add answers `PUBLISHED`, `load((await store.trees())[0]).entries.has("s-bbbbbb")` holds, and the attachment's path is in the tree's `attachments`).
  - `projects.test.ts` also: `a_second_create_conflicts_across_connections` (two `openDatabase` connections on one file in a temporary folder: the second `create` of one name throws `Conflict`, not a SQLite error); `a_name_used_as_a_role_cannot_join` (after a publish of a decision `decided_by: reviewer` and a thread message `by: builder`, `addMember` of `reviewer` and of `builder` each throw `Conflict` naming the record, and no event is written).
  - `rebuild.test.ts`: `rebuild_gives_the_same_tables` (after a project, a member, three publishes, one rewriting an entry, the rows of `heads`, `files`, and `members` before and after `rebuild` are equal); `rebuild_keeps_every_event`.
- [ ] **Step 2: Run** `cd ts && bun test tests/store`; expected: the new tests FAIL.
- [ ] **Step 3: Implement**; take `src/store/events.ts` out of `ts/knip.json`'s `entry`.
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 8: Two writers at once

**Files:**
- Create: `ts/tests/store/interleaving.ts`
- Modify: `ts/knip.json` (`tests/store/interleaving.ts` into `entry`, since `Interleaving` is first read by Task 9, d-tha8st); Tasks 7a and 7b's modules only where a test finds them wrong
- Test: `ts/tests/store/concurrent.test.ts` (changed, design line 72)

**Interfaces:**
- Consumes: Task 7b.
- Produces, for Task 9's tests:
  ```ts
  export class Interleaved implements Store {     // tests/gitstore/test_concurrent.py:29-58: runs during's add of drafts once, after the first trees()
    constructor(inner: Store, during: Lodge, drafts: readonly (readonly [string, string])[]);
    readonly outcomes: PublishOutcome[];
  }
  export class Interleaving implements Store {    // tests/app/fakes.py's rejectNext and movesAfterRead over any Store
    constructor(inner: Store);
    attempts: number;
    readonly publishes: (readonly [ReadonlyMap<string, string>, string])[];
    rejectNext(...changes: ReadonlyMap<string, string>[]): void;
    movesAfterRead(change: ReadonlyMap<string, string>): void;
    files(): Promise<ReadonlyMap<string, string>>;
  }
  ```
  Both pass `attachmentTexts` and every other method they do not change on to the inner store; Python's `Interleaved` holds `A_DRAFTS` itself (`tests/gitstore/test_concurrent.py:32-35`), and here the drafts are a parameter, so Task 9 runs another add through it.
  `Interleaving(inner)` counts `attempts` and keeps `publishes` (the writes and message of each `PUBLISHED` answer) as `MemoryStore` does; `rejectNext(...changes)` lands each change through `inner.publish` on a fresh `inner.trees()` before passing the next publish on, so the inner store's compare-and-set rejects it; `movesAfterRead(change)` lands it after the next `trees()`; `files()` gives the current tree's `files` together with `attachmentTexts()`, as `MemoryStore.files` holds attachments too (`tests/app/test_writes_retry.py:67` asserts an attachment path in it).
- `concurrent.test.ts` keeps the three titles of `tests/gitstore/test_concurrent.py` over the events store, each with Python's assertions on the outcomes and the state:
  - `two_clones_add_at_once`: two `openDatabase` connections on one file in a temporary folder, as two server processes would hold; A's add lands between B's read and B's publish, B's outcomes are `[REJECTED, PUBLISHED]`, and a third connection reads `s-bbbbbb`, `s-cccccc`, and `s-dddddd`, three decisions, the area's order, and `checkState` ok;
  - `two_worktrees_of_one_clone_add_interleaved`: the same with two `SqliteStore`s over one `LodgeDatabase`;
  - `stale_tree_publish_rejected_ref_unchanged`: two stores read, A publishes, B's publish on its read is `REJECTED`, and the project's `rev` read afresh is A's.
- The `Lodge`s are those of Python's `lodge_over`: `FixedClock`, `CountingIds(first)`, `coreSettings()`; the project is created with the owner `author`, and once Task 11 makes the actor required, each `Lodge` acts as `person("author")`, as `wired` does.

- [ ] **Step 1: Write the failing tests:** the three tests as above, and `interleaving.ts`.
- [ ] **Step 2: Run** `cd ts && bun test tests/store`; expected: the new tests FAIL until `interleaving.ts` exists, then pass on Task 7b's store; a mutation of the compare-and-set (`rev = :base` dropped) makes each fail, which the report names, then it is reverted (d-mfayy5).
- [ ] **Step 3: Run** `sh scripts/check-ts.sh`; green.
- [ ] **Step 4: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 9: The check on every write, over the events store

**Files:**
- Create: `ts/tests/store/seed.ts`
- Modify: `ts/tests/parity.test.ts` (a `changed` row of plan 2 is held to the rules of a `ported` row), `ts/knip.json` (`tests/store/interleaving.ts` leaves `entry`); Tasks 3 to 7b's modules only where a test finds them wrong
- Test: `ts/tests/app/reads-published.test.ts`, `ts/tests/app/writes-retry.test.ts` (changed, as the parity table says); `ts/tests/store/checked-writes.test.ts` (new)

**Interfaces:**
- Consumes: Tasks 6 (`Lodge.confirm`, for `a_refused_write_leaves_no_event`) and 8 (d-d96y91).
- Produces: no new name; the proof of design line 79 (d-fv20kp).
- Every `Lodge` here is built with four arguments, and Task 11, which comes next, adds `person("author")` to each, as it does for `wired`.
- `seed.ts`: `seeded(...items)` opens `":memory:"`, creates the project `storage-notes` owned by `author`, and publishes `filesOf(...items)` through the store's `publish`, as `MemoryStore` seeds its files without the check; it returns the database and the store.
- `reads-published.test.ts` keeps the six titles of `tests/app/test_reads_published.py`; on the server a record is never edited by hand, the store refusing a rewritten decision (d-j28rp0, Task 7b), and the published state is the current state, so each test sends the same edit through `add` and asserts the server's behaviour, over `seeded(AREA, ENTRY, FIRST)`:
  - `show_flags_a_hand_edited_published_decision`: the edit of `FIRST`'s statement to "Transcripts are deleted after a day." (from `draft("d-aaaaaa")`) answers `CHECK_FAILED` with the problems' checks `[5]` (probe 6), no event is written, and `show("ITEM-1")`'s flags hold no `fails check`;
  - `search_and_timeline_flag_it_too`: after it, `search("deleted")` lists nothing and the timeline's first item has no `fails check`;
  - `plain_check_lists_the_problem_and_fails`: after it, `problems()` is ok with no problem;
  - `gate_still_reports_it_once`: after it, `check(true)` equals `problems()`, since the gate compares the current state with itself;
  - `an_unedited_published_state_reads_clean`: as in Python;
  - `a_shrunk_agent_reasoning_fails_on_a_read`: with the agent decision `d-bbbbbb` seeded, shrinking its reasoning through `add` answers `CHECK_FAILED` with check 5's message for an agent decision, and `show("d-bbbbbb")` has no `fails check`.
- `writes-retry.test.ts` keeps the eight titles of `tests/app/test_writes_retry.py`, each over `seeded(…)` with the items Python gives `MemoryStore`, wrapped in `Interleaving`, with Python's assertions: `attempts` and `publishes` are the wrapper's, `files` its `files()`; a rejected publish is a real rejection by the events store's compare-and-set, not a fake's.
- `checked-writes.test.ts`:
  - `every_write_is_checked_against_the_state_it_lands_on`: session B reads; session A's add of drafts retiring `s-aaaaaa`, given to `new Interleaved(inner, a, drafts)`, lands after B's read; B's add of an entry resting on `s-aaaaaa` is rejected, read again, and answers `CHECK_FAILED` with check 6, writing nothing;
  - `a_refused_write_leaves_no_event`: the events counted before and after a failing add, a failing confirmation, and a dry run are equal;
  - `gate_on_the_server_is_the_current_state`: after three adds, `check(true)` equals `problems()`, and `gate`'s `published` is the tree `trees()` gave;
  - `a_refused_add_carries_its_feedback`: a failing add whose decision's title is over the guidance answers `CHECK_FAILED` with the length feedback in `feedback`, as lodge 0.2's `add` does (`src/lodge/app/writes.py:96-104`).
- `parity.test.ts`'s `ported_files_exist`, `ported_files_keep_every_python_test_name`, and `ported_files_hold_no_todo` also take a `changed` row with `plan` 2, so the three changed files keep every Python name.

- [ ] **Step 1: Write the failing tests** above, and `seed.ts`.
- [ ] **Step 2: Run** `cd ts && bun test tests/app tests/store`; expected: the new tests FAIL until `seed.ts` exists; each test that then passes on the earlier tasks' code is seen failing against a targeted mutation (the check skipped in `writes.ts`, the compare-and-set dropped, the retry in `add` cut to one attempt), listed in the report as a table of test and mutation, then reverted (d-mfayy5).
- [ ] **Step 3: Run** `sh scripts/check-ts.sh`; green, and the parity test holds the three changed files to their Python names.
- [ ] **Step 4: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 10: People in the core

**Files:**
- Modify: `ts/src/core/snapshot.ts` (`Tree`, `tree()`, `Snapshot`, `load`, and its `parseThread` call), `ts/src/core/derive.ts` (`isAuthor`, at `derive.ts:153` on `server-core` 579fb11, and its callers there), `ts/src/core/check-state.ts`, `ts/src/core/check-immutable.ts`, `ts/src/core/views.ts`, `ts/src/core/threads.ts`, `ts/src/core/confirmation.ts`, `ts/src/core/feedback.ts`, and `ts/src/core/apply-areas.ts` (`restored`, whose `tree({ … })` at line 65 passes `people: add.tree.people`); `ts/scripts/differential.ts`, whose `load({ rev: null, files, attachments: new Set() })` at line 41 is a `Tree` literal that a required `people` breaks under `tsc`, which includes `scripts`, so it becomes `load(tree({ rev: null, files, attachments: new Set() }))`, `author` alone being lodge's own records' person; `ts/tests/core/builders.ts` only where it builds a `Snapshot` literally; this is the list `grep -rn "isAuthor\|parseThread(\|writeThread(\|tree({" ts/src/core` gives at 579fb11, and Step 3 runs it again on the merged core
- Create: `ts/src/core/people.ts` (module-internal: the words below)
- Test: `ts/tests/core/people.test.ts` (new)

**Interfaces:**
- Consumes: plan 1's core; nothing of this plan.
- Produces, through `#core`, no new name (plan 1's front-door test stays as it is):
  - `people.ts` exports, inside the core only, `AUTHOR_ONLY: ReadonlySet<string>`, the set holding `author` alone, the one default below;
  - `Tree` gains `people: ReadonlySet<string>`, and the default-filling `tree()` fills it with `AUTHOR_ONLY`, so every carried test, which builds its trees with `tree()`, keeps lodge 0.2's meaning (d-vwsnz5);
  - `Snapshot` gains `people: ReadonlySet<string>`, which `load` copies from the tree;
  - `isAuthor(d, people = AUTHOR_ONLY)` is `people.has(d.decidedBy)`, and every caller in the core passes the snapshot's `people`;
  - `parseThread(path, text, people = AUTHOR_ONLY)` and `writeThread(thread, people = AUTHOR_ONLY)` read a message as a person's when its `by` is in `people`, `load` passing the tree's, and `writeThread`'s read-back using the same set;
  - `confirmationDraft(ids, scope, words, minute, area, person = "author")` writes `decided_by: <person>`.
- The new parameters are trailing and defaulted (d-d96y91), so plan 1's carried calls (`isAuthor(decision(…))` in `ts/tests/core/derive.test.ts`, `writeThread(t)` and `parseThread(path, text)` in `thread-text.test.ts` and `thread-files.test.ts`, and `writeThread(i)` in `builders.ts`) stay as they are, and lane A's `ts/src/app/threads.ts` compiles with its one-argument `writeThread` call whichever lane merges first; Task 11 then passes the snapshot's `people` from `app`.
- The words (d-vwsnz5): each message below keeps lodge 0.2's words when the person concerned is `author`, character for character, and otherwise reads as the right column, P being the person; `people.ts` holds the functions that choose:

  | Where in lodge 0.2 | lodge 0.2, and with the person `author` | With a person P |
  |---|---|---|
  | `src/lodge/core/check_state.py:124-128` | `decided_by is X; write author exactly, with a quote, or use your own role` | when `people` holds no `author`: `decided_by is X; name a person of the project exactly, with a quote, or use your own role` |
  | `check_state.py:132-137` | `decided_by is author, but there is no quote; add quote: {text, where, when} with the author's words, or record it under your own role` | `decided_by is P, but there is no quote; add quote: {text, where, when} with P's words, or record it under your own role` |
  | `check_state.py:147-150` | `confirms is for author decisions, but decided_by is X` | when `people` holds no `author`: `confirms is for a person's decisions, but decided_by is X` |
  | `check_immutable.py:21-24` | `reasoning of a published author decision was changed…` | `reasoning of a published decision of P was changed…`; an agent's as in lodge 0.2 |
  | `views.py:73` | the quote of an `author` decision is shown | the quote of a person's decision is shown |
  | `views.py:207` | `unquoted` on an imported `author` decision without a quote | on an imported person's decision without a quote |
  | `threads.py:85-86` | `an author message needs where` | `a message by P needs where` |
  | `threads.py:87-88` and `:118` | an `author` message's `when` is a minute, any other's a stamp | a person's message's `when` is a minute |
  | `confirmation.py:57-59` | `decided_by: author` and `The author confirms …` | `decided_by: P` and `P confirms …` |

  The review flags' words (`views.py:196-201`) and the feedback on a flag (`feedback.py:83-87`) are Task 13's, which names the persons a flag waits for; until then they keep lodge 0.2's words.
- `derive` reads `isAuthor(d, s.people)` wherever lodge 0.2 reads `is_author(d)`, so a flag is raised by any person's decision and cleared by any person's later confirmation, as lodge 0.2 does for `author`; Task 13 makes both per person.

- [ ] **Step 1: Write the failing tests** in `people.test.ts`, each over a tree whose `people` is `{ada}` or `{ada, bo}` (made up): `a_person_is_a_name_in_people`; `tree_defaults_to_lodge_0_2_people` (`tree({ rev: null, files })` gives `{author}`, and `load` copies it); `person_decision_needs_a_quote` (row 2); `author_is_a_role_where_no_person_is_author` (row 1, `decided_by: author` with `{ada}`); `confirms_is_for_a_person` (row 3); `immutable_names_the_person` (row 4); `quote_and_unquoted_follow_the_person` (rows 5 and 6); `person_message_needs_where_and_a_minute` (rows 7 and 8, parsed and written); `confirmation_draft_names_the_person` (row 9); `agent_change_to_a_persons_decision_is_flagged` (an agent decision replacing `ada`'s is in `awaitingAuthor`, and `ada`'s later confirmation clears it).
- [ ] **Step 2: Run** `cd ts && bun test tests/core`; expected: the new tests FAIL, every carried test passing.
- [ ] **Step 3: Implement**; then `grep -rn "isAuthor(\|parseThread(\|writeThread(\|tree({\|load({" ts/src/core ts/scripts` shows `people` passed at every call, and no `Tree` literal,, the only lines without it being the definitions of `isAuthor`, `parseThread`, `writeThread`, and `tree`.
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; green, every carried core test unchanged (`git diff --stat -- ts/tests/core` names only `people.test.ts` and, if it built a `Snapshot` literally, `builders.ts`).
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, then `sh scripts/differential.sh` (plan 1, Task 12), which must still print no difference, since lodge's own records are a store whose one person is `author`; commit, push.

### Task 11: People in the operations and the store

**Files:**
- Modify: `ts/src/app/errors.ts`, `ts/src/app/state.ts` (`Wiring` gains `actor: Actor`, which `threads.ts` and `confirm.ts` read), `ts/src/app/lodge.ts`, `ts/src/app/writes.ts`, `ts/src/app/threads.ts`, `ts/src/app/confirm.ts`, `ts/src/app/index.ts`, `ts/src/store/read-tree.ts`, `ts/tests/app/fakes.ts` (`MemoryStore`'s `people` option), `ts/tests/app/support.ts` (`wired`'s actor), and every test that builds a `Lodge` without `wired` (`ts/tests/store/*.test.ts`, Tasks 7b to 9's)
- Test: `ts/tests/app/people.test.ts`, `ts/tests/store/people.test.ts` (new)

**Interfaces:**
- Consumes: Tasks 9 and 10 (d-d96y91: Task 9's store tests are among those this task gives an actor).
- Produces, through `#app`: `Lodge`'s constructor takes a fifth parameter, `actor: Actor`, required; `Forbidden` (extending `LodgeError`, `exitCode` 2), for an operation the actor may not make.
- `support.ts`'s `wired(store: Store, clock = new FixedClock(), ids = new CountingIds(), actor = person("author"))`, so every carried test runs as the person `author` and keeps lodge 0.2's behaviour; `MemoryStore(items, { staged, people })` gives its trees `people`, by default `{author}`; every `Lodge` of Tasks 7b to 9's store tests acts as `person("author")`, the owner of their project.
- `readTree` gives the tree `people` = the project's owners, the members whose role is `owner` (d-vwsnz5; design lines 74 and 261: an owner decides and confirms, a member works, answers, and raises doubts); a member who is not an owner joins `people` when the design's roles step says so (design line 302).
- `writes.ts` and `threads.ts` build their after-states with `people: current.people`, so a write is checked with the people it was read with; every call of `writeThread` and `isAuthor` in `app` passes the snapshot's `people` (practice review P-I3).
- `threads.ts`'s `_message` (`src/lodge/app/threads.py:22-40`) reads a person as a name in the snapshot's `people`, with these words when `people` holds no `author`: `name a person of the project exactly, or use your own role` (for a role containing `author`), `a message by P needs where, the place of P's words`, and `where and when are for messages by a person`; with `author` in `people`, lodge 0.2's words; it calls `writeThread(thread, people)`.
- `_message`, after lodge 0.2's refusals and before anything is written, refuses a `by` that is in `people` from a person actor of another name with `Forbidden("only <by> writes as <by>; nothing was written")` (d-2v8vtk); a person may still write under a role, which the carried tests do through `wired`'s `person("author")` (`by: agent`, `reviewer`, and `coordinator`); an agent actor writing a person's `by` is published here as lodge 0.2 publishes it, and Task 12c holds it instead, since the hold port comes in Task 12a.
- `threads.ts`'s `waitingIn` (`src/lodge/app/threads.py:139-145`) splits by `people.has(last.by)` where lodge 0.2 compares with `"author"`: a thread whose last message is a person's waits for an agent (`forAgent`), any other for a person (`forAuthor`, the field keeping its Python name).
- `confirm` refuses an agent actor with `Forbidden("only a person confirms; nothing was written")` and a person not in the snapshot's `people` with `Forbidden("only an owner of the project confirms; nothing was written")`, and passes the actor's name to `confirmationDraft`, so the confirmation is that person's decision.

- [ ] **Step 1: Write the failing tests.**
  - `app/people.test.ts`, over `MemoryStore` with `people` `{ada, bo}`: `confirm_writes_the_persons_decision` (as `ada`: `decided_by: ada`, `ada confirms d-…`); `an_agent_cannot_confirm` (`Forbidden`, nothing written); `a_person_not_among_the_people_cannot_confirm` (as `cy`: `Forbidden`, nothing written); `a_persons_message_needs_where`; `author_is_a_role_where_no_person_is_author` (a message `by: author` refused with the words above); `a_person_writes_only_as_themselves` (as `bo`, an `ask`, a `reply`, and a `close` with `by: ada` and `where: "chat"`, so lodge 0.2's `where` refusal does not fire first, are each `Forbidden` with nothing written; as `ada`, `by: ada` with `where` is written); `a_persons_question_waits_for_an_agent` (a question whose last message is `ada`'s is in `forAgent`, one whose last message is `reviewer`'s in `forAuthor`); `an_agent_edit_of_a_persons_entry_waits` (an agent decision editing an entry whose last change is `ada`'s: one `feedback` line starts with `this decision will wait for`, and `derive` of the store's state after the add holds the decision in `awaitingAuthor`; the rest of the line is Task 13's, which runs beside this task, d-d96y91).
  - `store/people.test.ts`: `owners_are_the_people_of_the_tree` (owner `ada` and member `bo` give `{ada}`; after `cy` is added as an owner, `{ada, cy}`); `a_new_member_moves_the_rev` (a publish on a tree read before `addMember` is `REJECTED`).
- [ ] **Step 2: Run** `cd ts && bun test tests/app tests/store`; expected: the new tests FAIL, every carried test passing once `wired` passes the actor.
- [ ] **Step 3: Implement**; then `grep -rn "writeThread(\|isAuthor(\|parseThread(" ts/src/app` shows the snapshot's `people` passed at every call.
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 12a: Held drafts in the port and both stores

The port comes before the operations, since a method added to `Store` fails `tsc` until every class implementing it has it (probe 10), so the port and its two implementations are one task (d-d96y91, practice review P-I7).

**Files:**
- Modify: `ts/src/app/ports.ts` (`HeldDraft`, `HeldAdd`, `HeldMessage`, `Held`, `Store`'s `hold`, `held`, and `decline`, and `publish`'s `approves`), `ts/src/app/index.ts` (`HeldDraft`, `HeldAdd`, `HeldMessage`, `Held`), `ts/src/store/schema.ts` (`MIGRATIONS[1]`, `HeldTable`, `Tables.held`), `ts/src/store/events.ts` (the `held`, `approved`, and `declined` cases, and `rebuild`'s list), `ts/src/store/sqlite-store.ts`, `ts/tests/app/fakes.ts` (`MemoryStore`), `ts/tests/store/interleaving.ts` (passing the three methods and `approves` on), `ts/tests/store/database.test.ts` (`schema_is_created_once` now expects `user_version` 2)
- Test: `ts/tests/store/held.test.ts`, `ts/tests/app/fakes-held.test.ts` (new)

**Interfaces:**
- Consumes: Task 11.
- Produces, through `#app`: `HeldDraft` (the union of `HeldAdd` and `HeldMessage`, told apart by `kind`) and `Held`; `Store`'s `hold`, `held`, and `decline`, and `publish`'s fourth parameter `approves`, as in "Interfaces for plans 3 and 4".
- One hold machinery serves both kinds (d-znagqe for adds, d-2v8vtk for relayed thread messages): the stores keep a hold's body as JSON and read only its `person`, so a `HeldMessage` is held, listed, approved, and declined exactly as a `HeldAdd` is, and d-thvvzx's settle-once holds for both.
- The SQLite store (d-znagqe, d-thvvzx):
  - `MIGRATIONS[1]` creates `held(seq integer primary key, project text not null, person text not null, at text not null, body blob not null, state text not null)`, `at` copied from the `held` event by `applyEvent`, so `held()` reads one table, so `user_version` becomes 2; `HeldTable` is declared without `export`, as Task 7a's table interfaces are;
  - `hold(held)` appends a `held` event whose body is the `HeldDraft` as JSON, and answers its `seq`; `applyEvent`'s `held` case inserts the row as `open`;
  - `held()` gives the project's open holds, oldest first, each the `HeldDraft` with `seq` and `at`, from the row;
  - `decline(seq, reason)` runs, in one transaction whose first statement is `update heads set rev = rev where project = :project` (no row: `NotFound("no project named <project>")`), a read of the hold, `NotFound("nothing is held under number <seq>")` unless it is this project's and `open`, then appends a `declined` event (`{ held: seq, reason }`);
  - `publish(base, writes, message, approves)` with a number runs, after the compare-and-set and inside its transaction, a read of the hold: unless it is this project's and `open`, it answers `REJECTED` and writes nothing; otherwise it appends the `file` events and then an `approved` event (`{ held: seq }`), so the files and the approval land together (correctness review I-1);
  - `applyEvent`'s `approved` and `declined` cases set the row's state and throw when the row is missing or not `open`, so `rebuild` cannot replay a history the store could not have written; `rebuild` empties and refills `held` too;
  - every event moves `heads.rev`, so a tree read before a decline is stale for an approving publish too.
- `MemoryStore` keeps its holds in memory with the same answers: `hold` raises `rev` by one and numbers the hold with it, `decline` and an approving `publish` raise it too, and a hold not open makes `decline` throw `NotFound` and an approving `publish` answer `REJECTED`; `Interleaving` and `Interleaved` pass the three methods and `approves` on.

- [ ] **Step 1: Write the failing tests.**
  - `store/held.test.ts`: `a_hold_is_an_event_and_not_a_file`; `approval_and_files_land_together` (`publish(base, writes, message, seq)` called directly writes the `file` events and the `approved` event under one compare-and-set; one on a stale base writes neither); `a_declined_hold_cannot_be_approved` (after `decline`, an approving `publish` on a fresh tree answers `REJECTED` and writes no event); `a_hold_is_approved_once` (a second approving `publish` on a fresh tree answers `REJECTED`); `a_settled_hold_cannot_be_declined` (`NotFound`); `a_held_message_round_trips` (a `HeldMessage` given to `hold` comes back from `held()` field for field, with its `seq` and `at`); `holds_rebuild` (`rebuild` gives the `held` rows back); `rebuild_refuses_an_impossible_history` (raw `held`, `declined`, and `approved` events of one hold: `rebuild` throws, and the derived tables are as before it, its transaction rolled back); `schema_1_is_migrated_to_2` (a file built through a raw `bun:sqlite` connection with Task 7a's statements for migration 0 written out in the test, since `MIGRATIONS` is not exported, `user_version` set to 1, and one event inserted, opens with `openDatabase` at 2 with `held`, its event kept).
  - `app/fakes-held.test.ts`: `memory_store_settles_a_hold_once` (the same hold, decline, and approving publish over `MemoryStore`, with the answers above).
  - `database.test.ts`'s `schema_is_created_once` expects `user_version` 2 (correctness review M-2).
- [ ] **Step 2: Run** `cd ts && bun test tests/app tests/store`; expected: the new tests FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 12b: A person's decision drafted by another waits for that person

**Files:**
- Create: `ts/src/app/awaits.ts` (who an add awaits: the person its new decisions name other than the actor, or the two-person refusal; it imports nothing of `writes.ts` or `held.ts`), `ts/src/app/held.ts` (the operations `held`, `approve`, and `decline`, which `lodge.ts` delegates to)
- Modify: `ts/src/app/results.ts` (`AddOutcome.HELD`, `Added`'s `awaits` and `held`), `ts/src/app/writes.ts` (`add`'s attempt holds where `awaits.ts` says), `ts/src/app/lodge.ts`, `ts/src/app/index.ts`
- Modify also: `ts/tests/app/ports.test.ts` (`default_filling_functions_fill_python_defaults` checks `added()`'s `awaits` and `held` as `null`)
- Test: `ts/tests/app/held.test.ts` and `ts/tests/app/held-approve.test.ts` (new)

**Interfaces:**
- Consumes: Task 12a; the lane waits are unchanged.
- The imports run `held.ts → writes.ts → awaits.ts`, and `writes.ts` imports nothing of `held.ts`, since plan 1's `no-circular` rule (`ts/.dependency-cruiser.cjs:40-44` on `server-core`) refuses two modules importing each other (plan recheck 1, N-1); `held.ts` calls `writes.ts`'s attempts for `approve`.
- Produces, through `#app`: `AddOutcome.HELD` (`"held for approval"`), `Added.awaits` (the person whose approval the add needs, or `null`) and `Added.held` (the hold's number, or `null`), both filled `null` by `added()`; `Approved`; `Lodge`'s `held()`, `approve(seq)`, and `decline(seq, reason)`.
- The rule (SRV-2, d-zzfmj2, design line 75; d-znagqe): an add whose new decisions name in `decided_by` a person (a name in the state's `people`, the owners, d-vwsnz5) other than the actor (any person, for an agent actor) is held whole, entries and attachments with it, after its check passes and before anything is published:
  - `add` answers `HELD` with `ids` and `minted` as a dry run gives them (provisional), `awaits` the person, and `held` the number `store.hold` gave; nothing is written to the records, so the decision is not current;
  - a dry run of such an add answers `DRY_RUN` with `awaits` the person, so the session knows before it adds;
  - an add naming two persons other than the actor is refused with `LodgeError("an add holds the decisions of one person at a time; split the drafts by person")`;
  - a held add whose check fails is not held: it answers `CHECK_FAILED`, as any add does, so a draft without the person's quote never reaches the person (check 3).
- `held()` lists every open hold of the project, adds and messages alike, oldest first; plan 3 picks the actor's.
- `approve(seq)`: an unknown or settled number throws `NotFound("nothing is held under number <seq>")`; an actor other than the hold's person throws `Forbidden("only <person> approves this; nothing was written")`; for a `HeldAdd` it answers `{ kind: "add", added }` and runs the held drafts through `add`'s attempts as that person, reading the holds afresh at each attempt, dated at the approval, and publishes with `approves` = `seq`, so the files and the approval land in one transaction; a `REJECTED` answer reads again, and a hold no longer open then throws `NotFound`; `added` is the `Added` of that add, and a failing check (`CHECK_FAILED`) or a refusal leaves the hold open; a `HeldMessage` is Task 12c's, and until then `approve` of one throws `LodgeError("hold <seq> is a thread message, which this build cannot approve yet")`, which Task 12c replaces.
- `decline(seq, reason)`: the same refusals, and an empty reason after `cleanText` throws `LodgeError("a reason is required; nothing was written")`; it calls `store.decline`, and the hold leaves `held()`; it is the same for both kinds.

- [ ] **Step 1: Write the failing tests** in `app/held.test.ts` and `app/held-approve.test.ts`, the second holding the approval and decline tests (`the_person_approves_and_it_becomes_current`, `another_person_or_an_agent_cannot_approve`, `approval_runs_the_check_again`, `a_declined_hold_cannot_be_approved`, and `decline_needs_the_person_and_a_reason`) so neither nears 300 lines, over `MemoryStore` with `people` `{ada, bo}` and a draft decision `decided_by: ada` with her quote (made up): `an_agents_add_of_a_persons_decision_is_held`; `another_persons_add_is_held` (as `bo`: `HELD`, `awaits` `ada`, correctness review M-9); `a_dry_run_names_who_must_approve`; `a_held_add_is_not_current` (`show` of the provisional ID is `NotFound`, `search` lists nothing, and no file is written); `the_person_approves_and_it_becomes_current` (as `ada`: `{ kind: "add" }` with `PUBLISHED`, dated at the approval, `held()` empty); `another_person_or_an_agent_cannot_approve` (`Forbidden` for `bo` and for an agent); `approval_runs_the_check_again` (a change landing between the hold and the approval makes it fail check 6, so `CHECK_FAILED` and still held); `a_declined_hold_cannot_be_approved` (`approve` after `decline`: `NotFound`); `decline_needs_the_person_and_a_reason`; `a_persons_own_decision_is_not_held`; `an_add_for_two_people_is_refused`; `a_failing_check_is_not_held` (no quote: check 3, nothing held).
- [ ] **Step 2: Run** `cd ts && bun test tests/app`; expected: the new tests FAIL.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 12c: A person's words relayed into a thread wait for that person

The author's answer to STORE-1 (d-2v8vtk): an agent may relay a person's words into a thread under that person's name, with where and when; the message is held on Task 12a's machinery, and the thread waits for that person until they approve it signed in.

**Files:**
- Modify: `ts/src/app/threads.ts` (an agent's message under a person's name is held, not published; `waitingIn` reads the held messages), `ts/src/app/held.ts` (`approve`'s `message` branch), `ts/src/app/results.ts` (`Written`'s `awaits` and `held`)
- Modify also: `ts/tests/app/ports.test.ts` (`written()`'s `awaits` and `held` as `null`)
- Test: `ts/tests/app/held-messages.test.ts` and `ts/tests/app/held-messages-approve.test.ts`, `ts/tests/store/held-messages.test.ts` (new)

**Interfaces:**
- Consumes: Task 12b (`held.ts`, `Approved`, `AddOutcome.HELD`) and Task 12a's port.
- Produces, through `#app`: `Written.awaits` (the person whose approval the message needs, or `null`) and `Written.held` (the hold's number, or `null`), both filled `null` by `written()`; `approve(seq)` answers `{ kind: "message", written }` for a `HeldMessage`.
- The imports run `held.ts → threads.ts → writes.ts → awaits.ts`; `threads.ts` calls `store.hold` and `store.held` through the port and imports nothing of `held.ts`, so plan 1's `no-circular` rule holds.
- `ask`, `reply`, and `close` from an agent actor with a `by` in the snapshot's `people`: lodge 0.2's refusals come first, so a relay without `where` is refused with its words (`a message by P needs where, the place of P's words`); the ref or thread is resolved and a reply or close to a closed thread refused as lodge 0.2 refuses it; the message, its `when` the relay's or else `minuteOf(clock.now())`, is built and the thread write checked against the current state as a published one would be, so a message that fails is not held; then, instead of publishing, `store.hold` receives a `HeldMessage` (`person` the `by`, `by` the agent's `actorText`, the operation, the ref, `raises`, the cleaned text, `where`, and `when`), and the operation answers `Written` with `outcome` `HELD`, `ids` the thread's ID for a reply or close or the provisional ID a dry run would mint for an ask, `awaits` the person, and `held` the number; nothing is written to the records.
- A person actor writing under their own name is published at once, and one writing under another person's name is `Forbidden`, as Task 11 has it; an agent writing under a role is published as lodge 0.2 publishes it.
- `approve(seq)` of a `HeldMessage`: the refusals of Task 12b; then it runs the thread write as that person, with the held `where` and `when`, through the same attempts as an unheld message, minting an asked thread's ID at the approval, and publishes with `approves` = `seq`, so the thread file and the approval land in one transaction; a `REJECTED` answer reads again, a hold no longer open then throws `NotFound`, and a refusal (the thread closed meanwhile, a failing check) leaves the hold open; it answers `{ kind: "message", written }`.
- `decline(seq, reason)` of a `HeldMessage` is Task 12b's: nothing is published, and the hold leaves `held()`.
- Waiting (`waitingIn`, `threadsWaiting`, `waitingAll`): a held message is not the thread's last message until it is approved; a thread waits for a person (`forAuthor`) when its last published message is not a person's or when an open `HeldMessage` of a `reply` or `close` names it, and for an agent (`forAgent`) only when its last published message is a person's and nothing is held for it; the held messages are read once through `store.held()` beside the state; a held `ask` has no thread yet and is listed by `held()` only.

- [ ] **Step 1: Write the failing tests.**
  - `app/held-messages.test.ts` and `app/held-messages-approve.test.ts`, the second holding `the_person_approves_and_the_message_is_published`, `a_relayed_question_mints_its_thread_at_approval`, `decline_publishes_nothing`, `another_person_or_an_agent_cannot_approve_a_message`, and `approval_after_the_thread_closed_leaves_it_held`, over `MemoryStore` with `people` `{ada, bo}`, a question asked by `reviewer` on `s-aaaaaa`, and the agent actor `agent("coordinator")`: `an_agent_relaying_a_persons_words_is_held` (a `reply` by `ada` with `where: "chat"` and `when: "2026-10-29 09:00"` answers `HELD`, `awaits` `ada`, and a `held` number; no publish is made; `held()` lists a `message` hold with that text, `where`, and `when`); `the_thread_still_waits_for_the_person` (after that relay, the thread is in `forAuthor`, not `forAgent`, and `thread` shows `reviewer`'s message last); `the_person_approves_and_the_message_is_published` (as `ada`, `approve` answers `{ kind: "message" }` with `PUBLISHED`; the thread's last message is `ada`'s with `where` `chat` and `when` `2026-10-29 09:00`; the thread moves to `forAgent`; `held()` is empty); `a_relayed_question_mints_its_thread_at_approval` (an agent's `ask` by `ada`: held, no thread listed; after approval, one thread whose first message is `ada`'s); `decline_publishes_nothing` (as `ada`, `decline` with a reason: no publish is made, `held()` is empty, and the thread waits for the person by its last published message, `reviewer`'s); `a_persons_own_message_is_published_at_once` (as `ada`, a `reply` by `ada` with `where`: `PUBLISHED`, `held` `null`); `one_person_cannot_write_as_another` (as `bo`, a `reply` by `ada` with `where`: `Forbidden`, nothing held or published); `a_relay_without_where_is_refused_as_lodge_0_2_refuses_it` (an agent's `reply` by `ada` without `where`: `LodgeError` with `a message by ada needs where, the place of ada's words`, nothing held); `a_relay_to_a_closed_thread_is_refused` (nothing held); `another_person_or_an_agent_cannot_approve_a_message` (`Forbidden` for `bo` and for an agent); `approval_after_the_thread_closed_leaves_it_held` (the thread closed between the hold and the approval: the approval is refused, and the hold stays in `held()`).
  - `store/held-messages.test.ts`, over a `SqliteStore` from `seeded`: `a_relayed_message_lands_with_its_approval` (one `approve` writes the thread file's `file` event and the `approved` event under one compare-and-set, and `trees()` then holds the message).
- [ ] **Step 2: Run** `cd ts && bun test tests/app tests/store`; expected: the new tests FAIL.
- [ ] **Step 3: Implement**, removing Task 12b's interim refusal for a `HeldMessage`; `bun x depcruise` (through `sh scripts/check-ts.sh`) reports no `no-circular` violation.
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

### Task 13: Review flags per person

**Files:**
- Create: `ts/src/core/derive-flags.ts` (module-internal: the review flags' derivation per person, `src/lodge/core/derive.py:174-209` read per person, moved out of `derive.ts`, which is 238 lines at `server-core` 579fb11 against the 300-line limit)
- Modify: `ts/src/core/derive.ts` (which holds `isAuthor` and calls `derive-flags.ts`), `ts/src/core/views.ts`, `ts/src/core/feedback.ts`, `ts/src/core/people.ts`
- Test: `ts/tests/core/flags-people.test.ts` (new)

**Interfaces:**
- Consumes: Task 10.
- Produces, through `#core`: `Derived` gains `awaiting: ReadonlyMap<string, readonly string[]>`, each flagged decision's ID to the persons it still waits for, in code-point order; `awaitingAuthor` stays, the set of its keys.
- The rule (design line 77, d-4spcem): a decision that lodge 0.2 flags is flagged for each person P whose decision, or a decision P confirmed, raises the flag under lodge 0.2's rules (`src/lodge/core/derive.py:174-198`, `_counts_for` read per person); P's part clears when a later, non-imported decision of P confirms or replaces it (`_cleared`, `:200-209`, read per person); the decision is flagged while any part is left.
  With one person, this is lodge 0.2's rule, with that person for `author`.
- The words: `awaiting the author` becomes `awaiting P`, or `awaiting P and Q` (the Oxford comma for three or more); `awaiting the author on X` becomes `awaiting P on X`, P being the persons the listed decisions wait for; `confirmed by the author (X)` becomes `confirmed by P (X)`, grouped by person in code-point order (`confirmed by ada (d-1) and bo (d-2)`); and the feedback `this decision will wait for the author: … a later author decision that confirms or replaces it clears the flag` becomes `this decision will wait for P: it takes effect at once, and a later decision of P that confirms or replaces it clears the flag`, P the persons it waits for; lodge 0.2's words stay where the only person concerned is `author`; the feedback line keeps its first words, `this decision will wait for`, which Task 11's test reads (d-d96y91).

- [ ] **Step 1: Write the failing tests** in `flags-people.test.ts`, people `{ada, bo}`: `flag_waits_for_the_person_whose_decision_it_touches`; `another_persons_confirmation_leaves_it`; `that_persons_confirmation_clears_it`; `that_persons_replacement_clears_it`; `touching_two_people_waits_for_both` (the flag reads `awaiting ada and bo`, then `awaiting bo` after `ada` confirms); `a_confirmed_agent_text_counts_for_its_confirmer` (an agent edit of an entry whose last change `bo` confirmed waits for `bo`); `feedback_names_who_it_waits_for`; `confirmed_by_names_each_person`.
- [ ] **Step 2: Run** `cd ts && bun test tests/core`; expected: the new tests FAIL, every carried test passing.
- [ ] **Step 3: Implement.**
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh` and `sh scripts/differential.sh` (no difference), commit, push.

### Task 14: Closing checks

The coordinator runs this on `server-store` after every lane has merged, as d-442r2f has plan 1's closing step run (recorded on `server-core`).

**Files:**
- Modify: `ts/tests/parity.json` and `ts/knip.json` only where a check below finds them wrong

- [ ] **Step 1: Verify** every `tests/app/` row of `parity.json` is `ported` or `changed`, but `test_thread_fix_paths.py` (`planned`, plan 3); `tests/gitstore/test_concurrent.py` is `changed` and its file keeps the three names; `cd ts && bun -e 'for (const [p, r] of Object.entries(await Bun.file("tests/parity.json").json())) if (r.status === "planned") console.log(r.plan, p)'` prints only rows of plans 3 and 4, the plan first.
- [ ] **Step 2: Verify** `ts/knip.json`'s `entry` is plan 1's closing two patterns, and knip reports no unused export or dependency.
- [ ] **Step 3: Verify** `ts/tests/app/front-door.test.ts` passes with every addition exported; `bun test` passes in process with no socket (`grep -rn "Bun.serve\|fetch(" ts/src/app ts/src/store` prints nothing).
- [ ] **Step 4: Verify** with a scratch database: `openDatabase` on a fresh file, a project, two members, an add, a held add approved, a declined hold, then `rebuild`, gives the same rows of every derived table (Task 7b's and Task 12a's `rebuild` tests together cover it; this step runs them once more after the merge).
- [ ] **Step 5:** `sh scripts/check.sh`; commit, push; the ledger line says the plan ends: the carried app tests and the model tests pass in process, with no HTTP.
