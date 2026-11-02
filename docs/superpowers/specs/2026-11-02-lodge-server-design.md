# lodge server design

Status: approved by the author, 2026-11-02 13:52 ("Approved"); her questions SRV-1 and SRV-2 answered.
Sources: the needs (`2026-11-01-lodge-server-needs.md`), the architecture decisions (`2026-11-02-lodge-server-architecture-options.md`), and the research (`../../research/2026-11-02-server-feasibility.md`).
Quotes are the author's; **[my call]** marks a choice made in writing this document, for her to check.
The first design (`2026-10-29-lodge-design.md`) and the viewer design (`2026-10-31-lodge-viewer-interaction-design.md`) stay the authority for what records mean; this document changes where they live and adds what surrounds them.

## Intent

lodge becomes "a dev environment for SD tasks with agents which closely integrates the workflows we have (flexibly) and provides tools for me and the agents to work more transparently and effectively."
Today the workflow works, "but again everything is in files and chats. Interaction is only through chats."
What goes wrong because of that, in her experience:

- Work made in a session is lost with the session: a mock "was not commited or pushed and got lost when the session got lost. No session could find it again."
- Unrelated work shares one conversation: mocking "together with a session that also did coordination [...] was annoying because of the other messages in between."
- The state of a task lives in ledger files and chats, so she sees it only by asking a session.
- Hand-over between sessions runs through chat summaries, per-session state files, and a mailbox branch of request and acknowledgement files.

## Goals

1. Every task's state is explicit and can be acted on in one interface, by her, by other people, and by agents.
2. Each task and each question has its own thread, backed by one or more agent sessions, "so context stays local and not in one broad chat".
3. What a session makes (a mock, a report, a review) belongs to the task and outlives the session.
4. A new session starts from the task's steps, artefacts, and decisions, not from a chat summary.
5. Every open question from every session is in one waiting list, answerable from a phone.
6. The workflow is data per project, "adaptable/not fixed", with lodge's own build process as the default.
7. lodge starts sessions, or suggests starting them, on the server, on a connected machine, or as a Claude Code cloud session.
8. What a session reports is shown apart from what lodge has checked.
9. Decisions, specification entries, areas, threads, and confirmations keep the meaning the first two designs gave them.
10. Other people can use it, alone or together on a project.

## Non-goals for now

- A code editor in the product (need 9, "could be interesting"): later.
- The mock shown beside a screenshot of the built result (item 8 of the code options): later, since each project must say how its app starts.
- A desktop application: the browser app installs on a phone and a computer; a desktop shell earns its place only if it also runs the local server (need 8).
- Postgres and a second server process: SQLite until lodge needs them (ARCH-3).
- Anthropic's Managed Agents API: billed per token to an API key, not to a subscription (research, item 11).
- Self-hosted cloud environments: Team and Enterprise only (research, item 8).
- Hosts other than GitHub for pull requests and CI: git-level features work on any host; a GitLab connector follows when a project needs it.

## Must nots

The first design's three stay: never show wrong information, never let an agent quietly rewrite a decision she made, never become a third copy that costs more upkeep than it saves.
Added for the server:

4. Never offer claude.ai sign-in, or collect, store, or relay anyone's Claude credentials or session tokens (research, item 10); lodge starts the unmodified `claude` program, signed in by its user on that machine.
5. Never show a session's claim as a checked fact.
6. Never put a secret where others can read it: not in a cloud environment's variables, not in a repository, not in a URL.
7. Never merge into a project's main branch without a person's go.

## Constraints

- Public repository: no personal paths, names of machines, or specifics of any project using lodge, in code, tests, or documents.
- TypeScript throughout: server, runner, interface, and the `lodge` command; the runner and the command ship as single binaries built with `bun build --compile` (ARCH-2).
- SQLite, behind a storage port, through a typed query builder that also speaks Postgres (ARCH-3).
- The interface is Preact with `@preact/signals`, built with plain `tsc` and esbuild (ARCH-4).
- Today's structure rules carry over: `core` stays pure (no clock, randomness, file, or network; time and randomness through ports), modules stay small, imports go through front doors, and the rules are checked in the test run (LODGE-5) **[my call]**: enforced with a dependency checker over the TypeScript import graph.
- Test-first, and today's Python tests are the specification of the behaviour that carries over.
- `claude --cloud` needs a terminal (research, item 3), so the runner gives it a pseudo-terminal.
- A cloud session reaches lodge only on a public name (research, last section); while lodge runs locally that name is a Tailscale Funnel.
- A network secret belongs to a cloud environment, not to one session, so every cloud session in that environment presents the same token; a cloud session's identity therefore comes from the session ID lodge gives it in its prompt, checked against the task it was started for, not from its token.

## The model

Everything lodge stores is an event in one append-only table; every other table is built from the events and can be rebuilt (ARCH-3).
A record of the first design never changes once written, as now.

### Carried over unchanged in meaning

Specification entries, decisions, areas, threads (doubts and questions), confirmations, levels, review flags, codes, and links, as the first design and the viewer design define them.
What changes is where they live: in the server's events, not in files in git.

- `decided_by` names a person or an agent role; "the author" becomes the person who decided, one of the project's owners **[my call]**, so a project with several people keeps who decided.
- A person's decision is written only through that person (SRV-2, 2026-11-02 13:38: "B"): a session drafts it with the person's quote, the draft waits in that person's waiting list, and it becomes a current decision when they approve it; until then it is not current.
  This replaces LODGE-2's "trust the label" for the server, since a signed-in person is a place an agent cannot reach, so must-not 2 is enforced rather than only shown.
- A review flag on a person's decision clears only when that person confirms, not when another owner does **[my call]**.
- The importer maps 0.2's `decided_by: author` to the project's first owner, and the export writes the person **[my call]**.
- The check runs on every write, and a write that fails it is refused with the same feedback `lodge add` gives today **[my call]**; the "published state" of `lodge check --gate` becomes the server's current state.
- A record no longer waits on a branch merge to exist: it is current from the moment it is written, wherever the work is.
  A decision made for work that is later abandoned stays, and a later decision replaces it, as today for any decision.

### New objects

- **Project**: its repository (one or more), its members and their roles, its workflow, and its export target.
- **Workflow**: the steps a task goes through in this project (see Workflow as data).
- **Task**: a unit of work in a project, at one step of its workflow at a time, with its assignee, threads, artefacts, sessions, decisions, and code links.
  A work item of today (a plan, or one task of a plan) is a task; a plan's tasks are tasks under it **[my call]**: one level of nesting, no deeper.
  The planner session creates the child tasks through the API from the plan; the parent waits at its build step until every child is done.
- **Session**: one agent session working on a task, local or cloud, with its status, its reported steps, and its usage.
- **Artefact**: a file a session or a person attaches to a task: a mock, a report, a review, a brief.
  Each upload is a new version; nothing is overwritten.
- **Waiting item**: a question waiting on a person, from a thread, a session, or a step that needs a go.
- **Person**: someone who signs in, with passkeys, and the projects they belong to.

## Workflow as data

A project has one workflow per kind of task, by default `plan` and `task` **[my call]**; a workflow is a document lodge holds; each change to it is an event with who changed it and when, so the history of the process is kept as the history of decisions is **[my call]**.
Each step says:

- **Who acts**: a person or role (`owner`, a named member) or an agent role (`planner`, `builder`, `reviewer`, and so on).
- **What moves a task on**: a person's go, a review with no findings above a threshold, a check lodge runs, or the next step's start.
- **What starts a session**: lodge starts one, lodge suggests one, or someone starts one by hand.
- **Where it runs**: the server, a named machine's runner, any runner, or the cloud.
- **What it takes and gives**: the artefact kinds it needs and the ones it must leave on the task.
- **Where it goes on failure**: the step a task returns to when what moves it on fails, such as a review with findings sending it to `fix` **[my call]**; the workflow is a list of steps with named back-edges, not a free graph.
- **Its checklist**: the items a session working at this step is expected to report, such as brief, build, and report; a missing item is flagged.

Reviews report their findings through the API as part of the review artefact, each with a severity (Blocking, Important, Minor), so `no_findings_above` is read from findings rather than from a verdict.
A move driven by a session's review is shown as reported, not checked (must-not 5).
A fix round is one entry into a `fix` step, which is what "a task in its third fix round" counts.
The default workflows are lodge's own build process with a mocking step before planning, as she described both:

```yaml
plan:
  - name: mock
    acts: owner                     # a person with a session
    gives: [mock]
    moves_on: go                    # "until I'm satisfied", then "sent for development"
  - name: plan
    acts: planner
    takes: [mock]
    gives: [plan]
  - name: plan-review
    acts: reviewer
    gives: [review]
    moves_on: no_findings_above: minor
    on_fail: plan-fix
  - name: plan-fix
    acts: planner
    moves_on: next
    then: plan-review
  - name: build                     # waits until every child task is done
    moves_on: children_done
  - name: review                    # the whole-branch review
    acts: reviewer
    gives: [review]
    moves_on: no_findings_above: minor
    on_fail: fix
  - name: fix
    acts: builder
    then: review
  - name: merge
    acts: owner
    moves_on: go                    # code reaches main only on her go
task:                               # children of a plan, in order on the plan's branch
  - name: build
    acts: builder
    starts: lodge
    takes: [brief, plan, mock]
    gives: [report]
    checklist: [failing test seen, tests pass, committed, pushed]
  - name: review
    acts: reviewer
    gives: [review]
    moves_on: no_findings_above: minor
    on_fail: fix
  - name: fix
    acts: builder
    then: recheck
  - name: recheck
    acts: rechecker
    gives: [review]
    moves_on: no_findings_above: minor
    on_fail: fix
```

The exact syntax is left to the builder; the fields above are the content.
lodge tracks which workflow step a task is at; a session reports its own to-do items under that step, as the desktop app's task list, and each item may name the commit or branch it produced.
A checklist item never reported, or a step skipped, shows on the task (item 4).

## Tasks

A task page shows, at a glance: the step it is at, who acts now, what moves it on, its sessions and their status, its artefacts, its open threads, its decisions, and its code.
Tasks of a project are shown as a board, one column per step, with a plan's child tasks inside the plan's card **[my call]**.
A person moves a task on with a go, or sends it back with a reason that becomes a message in its thread.

## Sessions

### Starting

The runner on each machine belongs to the person who registered it and runs only sessions for tasks assigned to that person, under that person's own `claude` sign-in: the terms forbid running other people's requests on one person's subscription (research, item 10).
A session lodge starts by itself goes to a runner of the task's assignee; with none online, it becomes a waiting item for the assignee.
The runner connects out to the server and holds the connection open **[my call]**: a WebSocket.
When a step starts a session, the server asks a runner to start it, with:

- the task's brief: its step, its artefacts, its decisions, and its open threads, as one text the session reads first (goal 4);
- a session ID and, for a local session, a token scoped to the project and the task;
- the agent: Claude Code, Codex, or a cloud session.

A cloud session starts through `claude --cloud "<brief>"` in a pseudo-terminal; follow-ups go through `claude -p "<message>" --cloud <id> --output-format json` (research, items 2 to 4).
The cloud environment needs lodge's public name in its allowed domains and lodge's project token as a network secret; lodge's setup page says so, and lodge never sets either itself.

### Talking with a session

Decided by the author (SRV-1, 2026-11-02 13:34): "C".
A session lodge starts is talked to inside lodge: the task's thread, or the artefact's, is the conversation.
The runner keeps a local session open as `claude -p --input-format stream-json --output-format stream-json` and relays messages both ways, so a mock can be worked on from a phone.
A cloud session receives messages through `claude -p "<message>" --cloud <id>`; its replies appear in lodge only as the session reports them, through a hook at each stop **[my call]**; whether a cloud session's hook can read its own transcript is not checked.
A session a person starts in Claude Code is talked to there, and only reports to lodge.
This lifts the viewer design's exclusion of a live chat with an agent, for the server; the security of it rests on the sign-in and session tokens below.

### Reporting

A session reports to lodge through the API: its steps and their state (as the desktop app's task list), its status, its artefacts, its questions, and its usage.
lodge does not read a session's state from Claude Code; there is no command for it (research, item 6).
Most of this is sent without the agent's effort **[my call]**: lodge ships Claude Code hooks, as it ships `lodge hook` today, that report a heartbeat after each tool call, the status at each stop, and the usage read from the session's own transcript.
Whether a cloud session's transcript is readable by a hook is not checked; if not, usage is shown as unknown for cloud sessions.

### Three ways in

1. The `lodge` command, talking to the server.
2. An MCP server with the same operations, for local sessions only; cloud sessions use the `lodge` command, since MCP connectors travel through Anthropic's servers and the network secret does not reach them (research, last section), and "I don't think I can install additional mcp servers in cloud environments".
3. A mailbox branch in the project's repository, for a session with no network to lodge.
   lodge fetches it, applies each message as the API call it names, and marks what came this way.
   It carries no token **[my call]**: lodge accepts a mailbox message only for a session it started on that repository, so push access to the branch plus a known session ID is the authority.

## Artefacts

An artefact is uploaded to its task through the API (goal 3); a session's folder is never where it lives.
lodge shows images and PDFs inline and HTML mocks in a sandboxed frame without access to lodge's own origin **[my call]**, since a mock carries its own scripts.
An artefact has its own thread, so a conversation about a mock is not mixed with coordination.
A mock stays after the task it fed is done: it is "needed at least until development is finished but should still exist because maybe something was missed or I want to see why something was done in some way."
The task built from a mock links to it, so the mock is one step from the built result and the decisions taken in building it.
An artefact can be shared for an opinion with a person outside the project through a link that shows only that artefact and its thread **[my call]**.

## The waiting list

One list across every project a person belongs to: questions in threads, questions sessions raise, steps waiting on a go, and agent decisions waiting for confirmation (today's `lodge waiting`).
Each item shows what is asked, the options if the asker gave them, and enough of the task to answer without opening it.
An answer goes back to the asking session as a message.
The list is the phone's first screen **[my call]**, and a new item can raise a push notification.

## Claimed and checked

A step a session reports is shown as reported.
lodge marks it checked when it has confirmed it itself:

- a commit or branch the session names exists in the repository;
- a branch is merged;
- the project's gate, rerun by a runner on the commit the session names, passes.

The interface shows the two apart, and a step that moves a task on can require a checked state rather than a reported one.

## Usage and stuck work

Usage from session reports is totalled per task and per step.
lodge flags a session that has not reported for a project-set time, and a task in its third fix round.

## Code and git

Code stays in git.
lodge keeps a clone of each project repository and reads branches, commits, merges, and diffs from it, on any host.
Decision IDs in commit messages link commits and decisions both ways, as the commit messages of lodge itself already cite them.
For GitHub, a connector reads pull requests and CI, and can merge on a person's go.
From a task: see its branches and diff, start a session on its branch (a review, a fix), comment on a line of the diff (the comment becomes a thread), and merge on a go.

## People and sign-in

People sign in with passkeys and join a project through an invitation link.
Roles per project **[my call]**: `owner` (decides, confirms, gives the go to merge, changes the workflow) and `member` (works on tasks, answers questions, raises doubts).
Each local session gets its own token, scoped to its project and task and revoked when the session ends; cloud sessions share their environment's project token (see Constraints).
A runner holds a machine token issued when a person registers the machine.

## Interface

A browser app, installable on a phone and a computer, using the same API as the agents (ARCH-4).
Live updates through server-sent events **[my call]**.
Views:

1. The waiting list.
2. A project's board of tasks by step.
3. A task: steps, sessions, threads, artefacts, decisions, and code.
4. An artefact, with its versions and its thread.
5. The specification and decisions, carrying over the current viewer's pages (outline, areas, records, threads, confirming).
6. The project's workflow.

On a phone everything except reading diffs at length is meant to work ("wherever it is practical", need 7).

## Export to git

The server writes its records out as text files into a git repository and commits them, one way only; the database never reads the copy back (architecture options, "Export to git").
The target is the project's own repository or a separate one ("It should support a separate repo.").
It holds what a lodge 0.2 store holds (specification entries, areas, decisions, and threads on records) in today's file layout, so the export reads like a lodge 0.2 store; tasks, artefacts, and session reports stay out **[my call]**.
It runs after writes, batched to at most one commit a minute **[my call]**.

## Moving from lodge 0.2

An importer reads a lodge 0.2 store from a git repository and writes its records as events, keeping IDs, dates, codes, and `imported_from`.
lodge 0.2 stays usable until a project has moved; the hook's advice changes from "use `lodge add`" to "use the server" for a project that has moved.

## Build order

The author agreed items 1 to 3 of the session features first; the core has to exist before them **[my call]** for the rest of the order:

1. The core in TypeScript: records, the check, threads, confirmations, the events table, the API, and the `lodge` command at parity with lodge 0.2, its tests carried over; the importer; export to git.
2. Tasks, session reporting, artefacts, hand-over briefs, and the waiting list (items 1 to 3), with the hooks that report.
3. The interface: waiting list, task page, artefacts, then the board and the specification views.
4. The runner, starting local sessions, then cloud sessions.
5. Workflow as data, claimed and checked, usage and stuck work (items 4 to 6).
6. Code views and the GitHub connector.
7. Sign-in for several people, invitations, roles, and sharing an artefact.

Until step 7, one person signs in; passkeys come in step 1 **[my call]**, since the server is reachable beyond one machine from the first Funnel.

## Open

- How approving a drafted decision works in the interface; the author: "we should think about how exactly that interaction then works in the UI (but probably at a later point)".


## Left to the builder

- The workflow document's syntax.
- The API's shape (REST or RPC), within one API for the interface, the command, and the MCP server.
- Libraries for passkeys, the query builder (Drizzle or Kysely), and the dependency checker.
- The mailbox branch's file layout.
- How the board and the task page look, within the views above; a mock goes to the author before the interface is built, through the mocking step.
