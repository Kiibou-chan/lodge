# Brief: Task 7b of `docs/superpowers/plans/2026-11-02-lodge-server-store.md`

You build Task 7b of the plan named above, in the worktree `/var/tmp/lodge-store-b`, on branch `server-store-b`.
Read `CLAUDE.md` first, then this brief; it is your requirements, with the exact values to use verbatim.
Test-first: write each test, run it and see it fail, then write the code; all existing tests keep passing.
You have full access (d-94tynf). Run `sh scripts/check-ts.sh` last; it must exit 0. The structure checks gate the finished task, not intermediate commits.
Never run `bun install` or `bun add`: a package the task needs and `ts/package.json` lacks stops the task with BLOCKED and its name.
Never edit earlier briefs, reports, or reviews in `docs/superpowers/plans/2026-11-02-lodge-server-store/`: they are history.
Line handles in this brief drift as tasks land; re-locate them by content.
Commit when the gate is green, with explicit paths: `git -c "user.name=Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit`, message ending with the trailer `Co-Authored-By: Codex <noreply@openai.com>`; then `git push origin server-store-b`. Never touch `main`.
Write your report to `docs/superpowers/plans/2026-11-02-lodge-server-store/task-7b-report.md`: what you changed per file, each test added or carried with its first failing output (or the mutation it failed against, as a table), the commands you ran and their last lines, every test that cannot hold in TypeScript with the reason, anything you were unsure of. Commit the report too.
Your final message: DONE, DONE_WITH_CONCERNS, or BLOCKED, one line on the tests, and your concerns.
The "Coordinator" step of the task is not yours: the coordinator runs the whole gate, merges, and updates the ledger.
Plan 1's code is in `ts/`; the plan's Global Constraints, Calls made, and Interfaces follow, then your task.

## Global Constraints

Plan 1's Global Constraints hold for every task of this plan, and each brief repeats them; in short, with what this plan adds:

- Builders are Codex (`codex exec`), one task per brief; Codex sees its brief, `CLAUDE.md`, and the repository, with no network, a read-only git index, and no sockets: the builder never stages, commits, or pushes, and never runs `bun install` or `bun add`; a package the task needs and `ts/package.json` lacks stops the task with BLOCKED and its name.
- The builder's gate is `sh scripts/check-ts.sh` (Biome with `--error-on-warnings`, d-f18pz7; `tsc`, dependency-cruiser, knip, and `bun test`); the coordinator's gate after every task is `sh scripts/check.sh` outside the sandbox, then it stages with explicit paths, commits with `git -c user.name="Svenja Kernig" -c user.email=20756868+Kiibou-chan@users.noreply.github.com commit`, the message ending `Co-Authored-By: Claude <noreply@anthropic.com>`, and pushes `server-store` to `origin`; never `main`.
- lodge 0.2 keeps working: `src/`, `tests/`, `pyproject.toml`, and `uv.lock` are not edited.
- Test-first: each carried or new test is written and seen failing before its code (a missing module or export counts as failing); a carried test over code an earlier task ported is seen failing against a targeted mutation of that code, never a throw at a function's entry, one per test or per named group, listed in the report as a table and then reverted (d-mfayy5, as plan 1's Task 8c did); every existing test keeps passing, edited only where a task says so.
- Plan 1's final state is `origin/server-core` at 4f5d5fb; every line this plan cites in `ts/` is at that commit, and the coordinator checks each against the merged code before the task that reads it.
- Rules in `core` only (`ts/tests/structure/calls.ts` and `guards.ts` at 4f5d5fb), which bind Tasks 7a, 10, and 13, the tasks that edit `ts/src/core`: every `catch` begins with `if (!(e instanceof X)) throw e;`; no object literal has an `ok` key outside `check-state.ts`, so a check result is built through `checkResult` (d-snrhjs); a regular expression literal carries the `u` flag, never `m`, and no Python shorthand; and no `sort()` or `toSorted()` is called without a comparator.
- Check results in `app` are built through `checkResult` of `#core` too (d-snrhjs), where Python builds `CheckResult(…)` (`src/lodge/app/state.py:69`, `src/lodge/app/reads.py:96`), as plan 1's hand-off asks (`docs/superpowers/plans/done/2026-11-02-lodge-server-core/plan-2-writes-handoff.md` on `server-core`).
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
10. d-fv20kp: the check on every write needs no new write path; plan 2 proves it over the events store; d-j28rp0 (replacing d-pmaw3a, which replaced d-pprhpz) narrows it for plan 4's import, which publishes through the store after running the change check from an empty state with the store's settings and then the project's (d-n9nm8h, narrowing d-j28rp0), and has `publish` refuse what lodge 0.2's stores refuse, a path holding a surrogate, and a changed decision.
11. d-wx7d0f: projects and their members are events behind the `Projects` port.
12. d-2v8vtk (the author's answer to STORE-1): an agent may relay a person's words into a thread under that person's name, with where and when; the message is held, and the thread waits for that person until they approve it signed in; a person's own message is not held, and one person writing under another's name is refused (Task 12c).
13. d-nf7wvx: the rule `store-imports` holds `store` to `kysely` and `bun:sqlite` among outside modules.
14. d-thvvzx: a store transaction that reads before it writes opens with a write, and a hold is approved or declined once.

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
- `Store.publish` refuses, before it writes anything, what lodge 0.2's `check_writes` refuses (`src/lodge/gitstore/plumbing.py:14-25`) with its two messages, a path holding a surrogate, and a changed text for a decision file the base holds (d-j28rp0, replacing d-pmaw3a); it runs no other check: `app` checks before it calls it (d-fv20kp), and plan 4's import, which publishes a lodge 0.2 store's files through the project's store into an empty project, first runs the change check from an empty state with that store's settings and then with the project's (d-n9nm8h, narrowing d-j28rp0); a test that writes through `publish` directly stands for a hand edit of lodge 0.2 that leaves decisions and attachments as they are.
- Every store transaction that reads before it writes opens with a write on the project's `heads` row (d-thvvzx, probe 4): `publish` with its compare-and-set, `create` with an insert that does nothing on an existing name, and `addMember`, `decline`, and an approving `publish` with an update that keeps the revision (probe 8).
- The SQLite store answers `trees()` with one tree twice, `gate(current)` with `gate({ published: current, checked: [["", current]] })`, `freshness()` with `null`, and `commit(…)` with `committed({ outcome: CommitOutcome.FAILED, detail: "the server keeps no checkout; its writes are published at once" })`, and `publish` never answers `STAGED` (d-ae1vn5).
- A person's name is `^[a-z][a-z0-9-]{0,31}$` and a project's `^[a-z0-9][a-z0-9-]{0,62}$` (d-wx7d0f); `decided_by` names a person when it names an owner of the project, `Tree.people` being the owners (d-vwsnz5, design lines 74 and 261); a name the project's records use as `decided_by` or as a thread message's `by` cannot join it.
- A thread message whose `by` names a person (d-2v8vtk): from that person it is published at once; from another person it is refused with `Forbidden` (Task 11); from an agent, with where and when, it is held as a `HeldMessage` and published only when that person approves it, the thread waiting for that person meanwhile (Task 12c).

## Lanes
Lanes A, B, and C run in parallel in their own worktrees, merged into `server-store` as each task passes its review (Tasks 2 and 7a both edit `ts/package.json`'s `imports` and `ts/knip.json`'s one-line `entry`, so the second merge meets a textual conflict, which the integrator resolves by keeping both sides), as plan 1's lanes are (d-xdqsmf, recorded on `server-core` and here once plan 1 merges); within a lane, tasks run in order.
The import graph decides the lanes (d-d96y91): lane B's code and tests need only `#app`'s ports, `Lodge.add`, and `tests/app/support.ts` (Tasks 2 and 3), reading the store through `load` of `#core` where a later task's `show` would do; lane C touches only `ts/src/core` and `ts/tests/core`, which no task of lanes A and B edits except Task 7a's `text.ts` and `fileformat.ts`, which lane C does not touch.
Lane C's new parameters (`people` of `isAuthor`, `parseThread`, and `writeThread`) default to `author` alone, so lane A's `app/threads.ts` and plan 1's carried tests compile whichever lane merges first.
Tasks 11 and 13 may also run in parallel, since Task 13 touches only the core's derivation, views, and feedback, and Task 11 only the operations, the store, and their tests; Task 11's test reads a flag's feedback by its first words, which Task 13 keeps.
Tasks 9, 11, 12a, 12b, and 12c run in that order, since each edits or extends the tests or modules the one before it wrote; in `app` the imports run `held.ts → threads.ts → writes.ts → awaits.ts` and `held.ts → writes.ts`, and neither `threads.ts` nor `writes.ts` imports `held.ts`, so plan 1's `no-circular` rule holds.

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
  - `sqlite-store.test.ts` and `sqlite-store-refusals.test.ts`, split so neither nears 300 lines; `sqlite-store.test.ts` holds `trees_give_one_state`; `a_write_is_one_event_per_file` (kind, path, message, actor `ada`, `at` the clock's stamp); `file_bytes_survive_exactly` (a text starting with U+FEFF, CRLF, U+0000, an astral character, and U+DC80, read back equal, the last stored as the byte 0x80; probes 1 and 2); `stale_base_is_rejected_and_writes_nothing`; `attachments_are_listed_not_read` (in `attachments` of the tree, not in `files`, and given back by `attachmentTexts`); `gate_compares_the_current_state_with_itself`; `freshness_is_null_and_commit_is_refused`; `lodge_adds_through_the_store` (`Lodge` over a `SqliteStore` whose project holds `filesOf(AREA)`, published through `publish`, adds a decision of `coordinator` creating `s-bbbbbb` with its entry and the attachment `run.log`, drafted in the test with `decisionText` and `specText` of `ts/tests/core/applying.ts`, since `writes-attach.test.ts`'s drafts are locals of a test file; the add answers `PUBLISHED`, `load((await store.trees())[0]).entries.has("s-bbbbbb")` holds, and the attachment's path is in the tree's `attachments`); `sqlite-store-refusals.test.ts` holds `lone_surrogate_outside_the_escapes_is_refused` (no event written); `path_outside_lodge_is_refused` (`test.each` over `notes/x`, `lodge`, `lodge/../x`, `lodge//x`, `lodge/./x`, `lodge/.git/x`, and the TypeScript strings `"lodge\\x"` and `"lodge/x\0"`, each refused with lodge 0.2's message and no event written); `a_path_holding_a_surrogate_is_refused`; `an_attachment_is_never_overwritten` (a second publish of an attachment path the tree holds is refused and `attachmentTexts` keeps the first text); `a_published_decision_is_never_rewritten` (a publish changing a decision file's text is refused, no event written, even when only the rendering differs and the fields are the same, which d-j28rp0 accepts; one writing it with its own text is accepted).
  - `projects.test.ts` also: `a_second_create_conflicts_across_connections` (two `openDatabase` connections on one file in a temporary folder: the second `create` of one name throws `Conflict`, not a SQLite error); `a_name_used_as_a_role_cannot_join` (after a publish of a decision `decided_by: reviewer` and a thread message `by: builder`, `addMember` of `reviewer` and of `builder` each throw `Conflict` naming the record, and no event is written).
  - `rebuild.test.ts`: `rebuild_gives_the_same_tables` (after a project, a member, three publishes, one rewriting an entry, the rows of `heads`, `files`, and `members` before and after `rebuild` are equal); `rebuild_keeps_every_event`.
- [ ] **Step 2: Run** `cd ts && bun test tests/store`; expected: the new tests FAIL.
- [ ] **Step 3: Implement**; take `src/store/events.ts` out of `ts/knip.json`'s `entry`.
- [ ] **Step 4: Run** `sh scripts/check-ts.sh`; green.
- [ ] **Step 5: Coordinator:** `sh scripts/check.sh`, commit, push.

