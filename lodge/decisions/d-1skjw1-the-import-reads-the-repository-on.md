---
id: d-1skjw1
kind: decision
title: "The import reads the repository on the server, for the signed-in person only"
scope: process
decided_by: planner
date: 2026-11-02T19:03:24+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "1", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, 'The rest of build step 1'"}
  - {value: "78", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:78"}
  - {value: "75", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:75"}
  - {value: "253", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:253"}
  - {value: "3", handle: "docs/superpowers/plans/2026-11-02-lodge-server-core.md, Task 3"}
---

The `import` operation names a repository on the server's machine and a revision, and the server reads the store there through the `git` package; only the signed-in person may call it, so an agent's token is answered `forbidden`.
Build step 1 gives the import no command and no form on the minimal page.

## Reasoning

An import writes decisions in a person's name, since it maps `decided_by: author` to the project's first owner (design line 78), and a person's decision is written only through that person (SRV-2, d-zzfmj2; design line 75), so an agent's token may not import.
lodge keeps a clone of each project repository and reads from it (design line 253), and only `git` may run git (d-k5swcq, d-x6f9za), so reading on the server keeps git in one package; the command could not read the store and upload it without running git in `cli`, which plan 1's process-confinement rule refuses (plan 1, Task 3).
Reading a path the request names is a read of the server's own machine, which only the person who runs it may ask for.
No project moves during build step 1 (d-2jk0mw), whose reasoning has the first move wait for step 3's interface, so a command or a form would have no user before then; the tests and the coordinator's run call the operation in process.
Cost if wrong: an agent-driven import later needs the mapped decisions to wait for the person's approval as drafted decisions do (SRV-2), and a command or a form is one task when a project moves.
