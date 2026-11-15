---
id: d-vwsnz5
kind: decision
title: "A person is an owner of the project, and lodge 0.2's words stay for a person named author"
scope: process
decided_by: planner
date: 2026-11-02T19:35:58+01:00
replaces: [d-kj59bz]
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-store.md"
numbers:
  - {value: "0.2", handle: "grep -n '^version' pyproject.toml (0.2.0)"}
  - {value: "74", handle: "sed -n 74p docs/superpowers/specs/2026-11-02-lodge-server-design.md"}
  - {value: "261", handle: "sed -n 261p docs/superpowers/specs/2026-11-02-lodge-server-design.md"}
  - {value: "302", handle: "sed -n 302p docs/superpowers/specs/2026-11-02-lodge-server-design.md"}
  - {value: "81", handle: "sed -n 81p src/lodge/app/threads.py"}
  - {value: "85-88", handle: "sed -n 85,88p src/lodge/core/threads.py"}
  - {value: "3", handle: "src/lodge/core/check_state.py:132-137, check 3's quote rule"}
---

`decided_by` names a person when it names an owner of the project; the core reads the people from `Tree.people`, `author` alone by default and the owners in the SQLite store; `isAuthor`, `parseThread`, and `writeThread` take them as a trailing parameter defaulting to `author` alone; lodge 0.2's words stay for `author` and name any other person; only an actor among the people confirms; a name the records use as a role cannot join the project.

## Reasoning

The design makes "the author" "the person who decided, one of the project's owners" (`docs/superpowers/specs/2026-11-02-lodge-server-design.md:74`), and gives deciding and confirming to `owner` and working, answering, and raising doubts to `member` (`:261`), so members are not the people who decide (correctness review I-6).
With `author` as the default person, the core's carried tests and the differential run on this repository's records (d-0qmd10), whose one person is `author`, keep proving parity unedited.
Plan 1's carried tests call `isAuthor`, `parseThread`, and `writeThread` without people (`ts/tests/core/derive.test.ts`, `thread-text.test.ts`, and `thread-files.test.ts` on `server-core`, practice review P-I3), and lane A ports `src/lodge/app/threads.py:81`'s `write_thread(thread)` before lane C adds the people, so a required parameter would break both; a default keeps them compiling until Task 11 passes the snapshot's people.
d-wx7d0f's name pattern admits the agent roles of lodge's own records (`planner` decided d-pprhpz; the guide's example has `decided_by: coordinator`), and a person joining under such a name would turn earlier agent decisions into a person's decisions without a quote, which check 3 fails, and earlier agent thread messages into a person's without `where` (`src/lodge/core/threads.py:85-88`); refusing the name when it joins keeps the two name spaces apart without a list of reserved roles (correctness review I-3).
A confirmation is the confirming person's decision (s-bhew59), so an agent, or a member who does not decide, cannot confirm.
Cost if wrong: if members are to decide too, which the design's roles step settles (`:302`), `trees()` reads the members as well, one query; a person whose name an agent already used picks another name.
