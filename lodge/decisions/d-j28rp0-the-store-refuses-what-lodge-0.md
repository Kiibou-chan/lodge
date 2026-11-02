---
id: d-j28rp0
kind: decision
title: "The store refuses what lodge 0.2's stores refuse, a decision's new text, and a path it cannot keep"
scope: process
decided_by: planner
date: 2026-11-02T19:50:47+01:00
replaces: [d-pmaw3a]
narrows: [d-fv20kp]
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-store.md"
numbers:
  - {value: "0.2", handle: "grep -n '^version' pyproject.toml (0.2.0)"}
  - {value: "14-25", handle: "sed -n 14,25p src/lodge/gitstore/plumbing.py"}
  - {value: "4 to 6", handle: "src/lodge/app/state.py:59-79, read_checked's checks of a change"}
  - {value: "6", handle: "docs/superpowers/plans/2026-11-02-lodge-server-store/probes.md, item 6"}
  - {value: "1", handle: "docs/superpowers/plans/2026-11-02-lodge-server-store/probes.md, item 1"}
  - {value: "32", handle: "sed -n 32p src/lodge/gitstore/trees.py"}
---

`SqliteStore.publish` refuses, before writing anything, a path outside `lodge/` and an existing attachment as lodge 0.2's `check_writes` words them, a path holding a surrogate, and a changed text for an existing decision file; it runs no other check, so every caller checks first: `app`'s writes run the change check, and the import, publishing a lodge 0.2 store's files through the project's store, runs lodge 0.2's state check on that store and imports into an empty project only.

## Reasoning

lodge 0.2's stores refuse a path with an empty, `.`, `..`, or `.git` part, a backslash, or a NUL, and an existing attachment (`check_writes`, `src/lodge/gitstore/plumbing.py:14-25`), and d-ae1vn5 keeps lodge 0.2's outcomes; git refuses `lodge/../x`, `lodge//x`, and `lodge/.git/x` with `Invalid path` (correctness review I-7, `docs/superpowers/plans/2026-11-02-lodge-server-store/plan-review-correctness.md`), so a bad path kept in an append-only table would fail every later export of the project.
On the server's one state, checks 4 to 6 compare a state with itself, so a decision rewritten through `publish` reads clean: lodge 0.2's app over a one-state `MemoryStore` gives `show flags ()` and `problems [] True` after a hand edit of a decision's statement (correctness review I-8); this shows d-pprhpz's cost wrong, since reads do not flag such a write.
The store is the one place every write passes, and no write of `app` changes a decision's fields, since check 5 refuses such an edit before `publish` (probe 6 of `docs/superpowers/plans/2026-11-02-lodge-server-store/probes.md`); so the refusal keeps s-pncjp8's "Decisions are never rewritten" on the server at the cost of one case: a decision drafted and added back with no field changed passes check 5, which compares parsed fields (`src/lodge/core/check_immutable.py:49-52`), and reaches `publish` when lodge's rendering differs from the stored text (`src/lodge/core/apply.py:188`, `src/lodge/app/writes.py:90`), as an imported lodge 0.2 file's can; there the store refuses where lodge 0.2 publishes a reformatted file, and the refusal is accepted, since nothing is lost, the record reads the same either way, and comparing parsed fields in the store would put the core's check in the adapter (plan recheck 1, N-2).
d-pmaw3a stated the same rule with the claim that no write of `app` rewrites a decision file, which the case above shows too broad; this decision replaces it with the claim corrected.
A `text` column changes a lone surrogate and the character after it (probe 1), and lodge 0.2 decodes a file name with `surrogateescape` (`src/lodge/gitstore/trees.py:32`), so a path holding a surrogate would be kept as another name; refusing it is simpler than a `blob` path column for a name only a hand-made file can have.
The import is unchanged from d-pprhpz: plan 4 publishes a lodge 0.2 store's files through the project's store by its one owner, after lodge 0.2's check of that store (d-y42b7b and d-ag8p8h, recorded on `server-import`), into an empty project, where none of these refusals can fire but a surrogate path.
Cost if wrong: an agent re-adding an unchanged decision of an imported record is refused instead of reformatting it, and must leave that draft out of the add; a later tool that must rewrite a decision file needs an event kind of its own, and plan 3's carried command tests that rewrite a decision by hand through `publish` become changed rows that write a new file instead.
