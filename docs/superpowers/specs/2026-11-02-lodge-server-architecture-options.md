# lodge as a server: architecture options

Status: options for the author, 2026-11-02.
The shape is decided: option A, the author's answer "A" to ARCH-1 (2026-11-02 00:18).
Argues from the needs (`2026-11-01-lodge-server-needs.md`) and the research (`../../research/2026-11-02-server-feasibility.md`).
Two needs points stay open and are treated as room the design must leave: which concerns get a place of their own, and how tasks and decisions relate to code in git.

## What every option keeps

- Records are events: a decision never changes once written, and entries, tasks, and threads are what the events add up to; lodge's `core` already works this way and reads no clock, file, or network (`src/lodge/core`, LODGE-5).
- Code stays in git; lodge links a task to its branches, commits, and pull requests, and never holds code.
- Agents reach lodge through one API, offered three ways: the `lodge` command (talking to the server), an MCP server, and, where a session has no network to lodge, a mailbox branch in the project's repository that lodge reads.
- Cloud sessions reach the API through a public name (Tailscale Funnel while lodge runs locally), with lodge's token as a network secret on the cloud environment, so the session never sees it.
- People sign in with passkeys; each agent session gets its own token, scoped to its project and task, issued when lodge starts it.

## Option A: one server, a runner on each machine

- The server holds the records, serves the web interface and the API, and runs the workflows.
- A small runner on each machine that may do work (the server's own machine, a laptop, a second workstation) connects out to the server and starts sessions there when told: Claude Code, Codex, or a cloud session through `claude --cloud` in a pseudo-terminal.
- A session reports to the server itself; the runner reports only that a process started, ended, or failed.
- Machines behind a router or on another network need no open port, since the runner connects out.
- Cost: two programs to build and keep in step, the server and the runner.

## Option B: one server, no runners

- As A, but the server starts sessions only on its own machine and in the cloud.
- Work on another machine starts by hand there and joins by registering with the server.
- Cost: need 3 ("any set of clients connected and working") holds only for sessions a person starts; lodge cannot start or suggest-and-start work on the laptop.

## Option C: git as the bus

- As the academic editor's sessions do today: records and messages live in branches of the repository, sessions coordinate by pushing and fetching, and the server is an interface and a watcher over the repository.
- Cost: contradicts the direction ("Server I would say") for records; every state change is a push, so the interface sees changes only as fast as fetches run; several people writing means merge conflicts in shared files.
- Kept from it: the mailbox branch as one of the three ways in, for sessions that cannot reach the server.

## Chosen

A, with the mailbox branch as a fallback way in.
Recommended because it is the only option that meets need 3 for work lodge starts itself, and the runner is the piece that starts `claude --cloud` in a pseudo-terminal anyway.

## Language: TypeScript throughout

Decided by the author (ARCH-2, 2026-11-02 00:34): "Okay then TS sounds fine. I might prefer kotlin personally, but the code reuse point is quite a strong one I think."
Server, runner, interface, and the `lodge` command are TypeScript; the runner and the command ship as single binaries (`bun build --compile`).
Today's Python code is rewritten, with its tests as the specification of its behaviour.
Performance was weighed and is not what separates the candidates at lodge's load; types, binaries, how well agents write each language, and reuse were.
The academic editor's agent code is about 3,650 lines of TypeScript with no Electron imports, but it imports the editor's own `safety`, `store`, `base`, and `ui` packages, so reusing it means first moving it into a package both projects share.

## Storage: SQLite

Decided by the author (ARCH-3, 2026-11-02 00:38): "A then".
One SQLite file; records go into an append-only events table, and the tables for entries, tasks, and threads are built from it; queries go through a typed builder that also speaks Postgres, behind a storage port.
Only the server writes, so one writer is enough; Postgres follows when lodge needs a second server process.

## Export to git

The server writes its records out as text files into a git repository and commits them, one way only: the database stays the authority and never reads the copy back.
It gives history readable with plain git, a backup off the machine, and the records as plain files if lodge stops.
The author (2026-11-02 00:38): "That sounds reasonable. It should support a separate repo."
Open: how often it runs, and whether tasks and threads go out with decisions and entries.

## Interface: an app in the browser, Preact with signals

Decided by the author (ARCH-4, 2026-11-02 10:44): "C".
An app in the browser, written with Preact and `@preact/signals`, installable on a phone; it talks to the server through the same API the agents use.
The build stays at plain `tsc` and esbuild, so structure checks on the code keep working without a framework compiler; Svelte and Solid were set aside for needing their own compiler and checker.
Preact with signals is about 8 KB compressed and costs 1.1 to 1.35 times hand-written DOM code, and keyed rows keep their element, focus, and caret.
The academic editor adopted the same stack for its list and card views (its author's ruling, 2026-11-02), so interface parts could later move into a package both projects share.

## Decided after these

1. The workflow model: a workflow as data per project (steps, who acts at each, what moves a task on, what starts a session), so it stays adaptable.
