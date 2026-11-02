# Probes for the server-import plan

Run on 2026-11-02 with Bun 1.3.14, git 2.56.0, Python 3.13, and lodge 0.2 from this repository (`uv run --frozen --quiet --project <worktree> lodge`), in a scratch folder; the sources are in `probes/` beside this file, and outputs are quoted as printed.
The plan cites them as "probe N".

1. `python3 probes/decode-cases.py cases.json expected.json && bun probes/decode-probe.ts cases.json expected.json`: 20 edge byte strings (an overlong `c0af`, a truncated `e282`, an encoded surrogate `eda080`, `f4908080` above U+10FFFF, a lone `f5`, `c2`, and `80`, and valid two-, three-, and four-byte sequences) and 20,000 random ones of 1 to 12 bytes, decoded by `probes/decode.ts` and by Python's `bytes.decode("utf-8", "surrogateescape")`:
   `cases 20020; decodeStored differs from Python's surrogateescape on 0; encodeStored fails to give the bytes back on 0; TextDecoder differs on 19004`, and `TextDecoder of ff: U+fffd`.
   So `TextDecoder`'s default turns an undecodable byte into U+FFFD, and the 40-line decoder of `decode.ts`, which maps each byte of an invalid sequence to U+DC00 + b, agrees with Python on every case and its encoder gives the bytes back.
2. `bun probes/sqlite-surrogate.ts`: a text holding the lone surrogate U+DCFF, stored in a `bun:sqlite` `text` column and read back:
   `lone surrogate in: U+dcff; read back: U+61 U+4fc62; same false`.
   So a lone surrogate does not survive the events store: it reads back as another character, and the character after it is lost.
3. A made-up lodge 0.2 store in a scratch repository, built with lodge 0.2's own commands (`init`, then `add` of an author decision with a quote creating an entry in area `storage`, an agent decision `decided_by: coordinator`, and an author decision confirming the agent's), committed; `lodge check` prints `ok`.
   Then each `decided_by: author` line is replaced by `decided_by: ana`, as an export that writes the person would write it, and committed:
   `lodge check` prints `check 3: d-z2tjr2: confirms is for author decisions, but decided_by is ana` and exits 1 (the same with `person:ana` and `ana@example.com`);
   `lodge spec` prints the same text as before (`diff` exit 0);
   `lodge show` of the agent decision loses ` · confirmed by the author (d-z2tjr2)` from its first line;
   `lodge waiting` prints the same text as before.
   So lodge 0.2 reads an export that names a person in `decided_by` with the same specification, but its check fails on each confirmation the person made, and it no longer shows that the person confirmed anything.
4. `bun probes/export-probe.ts`: 402 files under `lodge/` committed into a branch of a bare repository through a temporary index, with every blob hashed by one `git hash-object -w --no-filters --stdin-paths` and the index filled by one `git update-index -z --index-info`, then `write-tree`, `commit-tree`, and `update-ref` with the old value:
   `bare target, 402 files: first export 8daff6b in 34 ms`;
   `same files again: unchanged in 23 ms` (the tree equals the tip's, so no commit is made);
   `one file changed: parent of the new commit is the first: true`;
   `files at the tip: 402; text kept: true`;
   `author: lodge <lodge@export.invalid>`;
   `update-ref with a stale old value: exit 128: fatal: update_ref failed for ref 'refs/heads/lodge': cannot lock ref 'refs/heads/lodge': is at 83871f3f… but expected 8daff6b…`;
   `worktree list names the checked-out branch: branch refs/heads/lodge`.
   So the export needs no work tree, makes no commit when nothing changed, refuses to move a branch that moved under it, and can tell a branch that a work tree has checked out.
5. This repository's store, counted without reading a record: `ls lodge/decisions | wc -l` prints 221 and `find lodge/spec -type f | wc -l` prints 137; `lodge/attachments` and `lodge/threads` do not exist; `git grep -c '^decided_by: author$' -- lodge/decisions | wc -l` prints 46.
   So the coordinator's run on a scratch copy of lodge's own records exercises decisions, entries, areas, and the author mapping, but no thread and no attachment, which the made-up store of the round-trip test holds.
6. A fuller made-up lodge 0.2 store, written by lodge 0.2's own commands in a scratch repository whose `.lodge.toml` lists `[import] sources = ["docs/choices.md"]`: `lodge init`; `lodge add --import` of an author decision with a bare day and `imported_from` and no quote; `lodge add` of an author decision with code `ITEM-1` and a quote, creating an entry in a new area `storage`; `lodge add --attach sizes.csv` of an agent decision; `lodge add` of an author decision confirming it; `lodge ask` of a question on the entry by `coordinator`; and `lodge reply` by `author` with `--where` and `--when`.
   `lodge check` prints `ok`, and the store holds ten files, copied unchanged into `probes/zero-two-store/` with its `.lodge.toml`: two `.gitkeep` files, four decisions, one area, one entry, one thread, and one attachment.
   The imported decision's bare day `2026-01-05` is written as `2026-01-05T00:00:00+00:00`, and the author's thread message keeps `by: author` with quoted `when` and `where`.
   These texts are lodge 0.2's own output for a made-up project, so the round-trip test can start from them byte for byte.
7. The store of probe 6 committed in a scratch repository, then each `decided_by: author` and each thread message's `by: author` replaced by `ana` and committed, lodge 0.2's standard output compared before and after (re-run in plan fix round 1):
   `lodge check` prints `problem: lodge/threads/q-j2dsgk.md:20: when must be ISO 8601 with seconds and an offset` and `check 3: d-t46j05: confirms is for author decisions, but decided_by is ana`, and exits 1; `lodge check --gate` prints `ok` with both as `note: already published, …` lines and exits 0;
   `lodge spec` gains the `problem:` line, and the entry's heading `## Transcripts are kept (s-cjhfb7 · question open)` becomes `## Transcripts are kept (s-cjhfb7)`;
   `lodge waiting` loses `q-j2dsgk · open · question · about s-cjhfb7 · 2 messages · last by author` and prints `nothing`.
   So lodge 0.2 reads a message by a person other than `author` as an agent's, whose `when` must be a stamp, and the thread drops out of its reads; plan 2's core reads a message as a person's when its `by` is one of the project's people, a person's `when` being a minute (plan 2, Task 10), which is why the importer maps thread messages too.
   The author ruled that the export names the person and need not stay readable by lodge 0.2 (d-b61590), so these are the expected effects on a lodge 0.2 reader, not defects.
8. `python3 probes/fixture.py probes/zero-two-store > zero-two-store.ts`, then a Bun script reading each path of the generated `ZERO_TWO_STORE` from `probes/zero-two-store/` and comparing the texts:
   `files 11; equal 11`.
   So the generator's JSON string literals give the made-up store's texts back exactly, and Task 1 can write the fixture with it rather than by hand.
9. `uv run --frozen --quiet python probes/check-change-empty.py ROOT [TOML]` runs lodge 0.2's `check_change` from an empty state to the store at `ROOT`, with `now` 2026-11-03T00:00Z and the `[length]` and `[import]` tables of its `.lodge.toml` (or of `TOML`):
   on this repository's records at ae2db4e (`git archive ae2db4e lodge .lodge.toml`): `files 374 state problems 0`, `change problems 0 {}`;
   on `probes/zero-two-store`: `change problems 0 {}`; with `TOML` `[import] sources = []`: `change problems 1 {4: 1}`, `d-40q44p: imported from docs/choices.md, which is not listed in [import] sources`.
   With `now` plan 2's `FixedClock` start, 2026-10-29T09:30:00+01:00, instead, on `probes/zero-two-store`: check 1 for `d-q59cdf`, `d-qqrf9k`, and `d-t46j05`, each `dated <its date>, which is after the time of this change`, its date 2026-11-02T18:56:29+01:00, 18:56:28, and 18:56:30 (run inline with the same calls); so a test that imports the made-up store sets its clock after 2026-11-02T18:56:30+01:00.
   So a change from an empty state judges every decision as new, the store's settings decide check 4, and history that replaces, narrows, and confirms raises no check 6, since the statuses are derived from the empty published state.
   `bun probes/spawn-sync.ts <empty folder>` and `bun probes/spawn-env.ts`, Bun 1.3.14: `Bun.spawnSync(["git", "--version"])` with `PATH` the empty text runs git (exit 0), and with `PATH` an empty folder throws `ENOENT`, `Executable not found in $PATH: "git"`; a child's standard input, output, and error are `memfd:spawn_stdio_stdin`, `…stdout`, and `…stderr`, no socket; `hash-object --stdin` of `a\n` gives `78981922613b2afb6025042ff6bd878ac1994e85`; after `process.env.FOO_PROBE = "mutated"`, a spawn without `env` sees `[]` and one with `env: { ...process.env }` sees `[mutated]`.
   So `Bun.spawnSync` needs no socket, plan 1's one spawning test, `ts/scripts/differential.test.ts`, passed in Codex's sandbox with it (`docs/superpowers/plans/2026-11-02-lodge-server-core/task-12-report.md:30` on `server-core`), and a test's change to `process.env` reaches git only through an explicit `env`.
