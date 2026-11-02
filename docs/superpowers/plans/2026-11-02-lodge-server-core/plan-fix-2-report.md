# Plan fix round 2: report

Planner, 2026-11-02; answers `plan-recheck-1.md` (N1 to N3, m1 to m6, the preflight's mismatch rows).
Status: done.

## Probes run

- knip 6.42.0 in a scratch folder: an unread export of a module and of a test helper fail (`Unused exports (2) orderKey … LATER`, exit 1); with both files in `entry` knip exits 0; with the reader added and the file taken out it exits 0; with a file taken out while a name is still unread it fails again (`LATER`, exit 1); an export re-exported by `index.ts` and read by no test is not reported.
- `tsc` 6.0.3 with `noUnusedLocals`: a top-level function left unexported and unread fails with `TS6133: 'orderKey' is declared but its value is never read.`, so dropping `export` does not work for a name its own file never reads.
- `python3 -c "print(repr('\u200b'))"` prints `'\u200b'`.
- Python 3.13.5 (Unicode 15.1.0): `isdecimal` takes 680 code points, `/\p{Nd}/u` under Bun 770, 90 more, all of category `Cn` in Python's database, the first U+10D40.
- dependency-cruiser 18.6.0 on a planted tree whose `node_modules` links to a real one: without `dependencies` and without `preserveSymlinks`, `yaml` resolves outside the tree with type `npm-no-pkg`; with `dependencies` copied and `preserveSymlinks: true`, it resolves to `node_modules/yaml/dist/index.js` with type `npm`, as on an unplanted tree.

## Rulings

- d-tha8st (N1): an export first read in a later task waits in knip's `entry` list; the reading task takes the file out.
- d-hshapm (N2, narrows d-s2rdn2): `#core` exports `__all__`, the default-filling functions, and `errors.ts`, `text.ts`, and `stamps.ts`; `quoted`, `unreadableChar`, and `LINE_BREAKS_AND_TABS` stay inside the package.
- d-bxcave (m2): a planted tree copies `dependencies` and is cruised with `preserveSymlinks`.
- d-87kzys (m3): `text.ts` exports `PY_SPACE_CLASS`.

- Bun 1.3.14: `import page from "./page.html" with { type: "text" }` gives the text, also from a compiled binary after the file is removed.

## Plan edits

Every finding and mismatch row is answered against its ID in `plan-fix-2.md`; probes 21 to 25 are in `probes.md`, sources in `probes/fix2/`.
N1's rule covers eight files, from a scan of the import lines of `src/lodge/core/*.py` and `tests/core/*.py` against the tasks' Port and Test lists; no other export of a ported module or helper has its first reader in a later task.
The recheck's own N1 fix (leave `export` off until the reader's task) was not taken, since `tsc` fails on an unexported name its file never reads.
`plan-fix-1.md`'s M-8 row is corrected in place for m5.
The editing tool turns a written `\u200b` into the raw character, the likely origin of N3; every escape this round was written through `chr(92)`, and the plan, `probes.md`, `plan-fix-2.md`, and this report hold no character of categories `Cf`, `Cn`, `Co`, `Cs`, `Zl`, or `Zp`.

## Gate

`sh scripts/check.sh`: `1399 passed`, `lodge check --gate` `ok`.

## Open

None for the author; no value trade-off, so no `questions.md`.
