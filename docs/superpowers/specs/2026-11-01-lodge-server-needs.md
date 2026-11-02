# lodge as a server: needs

Status: needs gathered from the author on 2026-11-01, for discussion; nothing here is decided as a record yet.
The author's own words are quoted; the rest restates them.

## Direction

lodge becomes a server product that holds the records itself, instead of reading them from files in git.
Asked whether the server or git holds the records, the author answered "Server I would say."
The author's picture of it: "a dev environment for SD tasks with agents which closely integrates the workflows we have (flexibly) and provides tools for me and the agents to work more transparently and effectively."
The name stays lodge.

## Needs

1. Tasks, workflows, and questions get a proper interface, for the author and for agents.
2. Interaction is threaded: each question and each task has its own thread, "so context stays local and not in one broad chat", and every thread is backed by one or more agent sessions.
3. Work runs either on the server itself, or locally with the server as coordinator, with "any set of clients connected and working", as an existing editor's sessions already coordinate across machines.
4. The server can run locally as well as remotely; for development it runs locally for now, and a remote host follows later.
5. Authentication is required, since the server will be reachable beyond one machine.
6. Cloud agent sessions must be able to reach it.
7. On a phone, the author can do everything a computer allows "wherever it is practical", coding excepted: an installable app or at least a mobile-friendly web interface.
8. A browser interface is acceptable; a desktop application earns its place if it also runs the local server.
9. A code editor in the product "could be interesting" at some point.

## Workflow

A workflow spans "how the whole project is coordinated and run to how each task is done".
The author: "Conceptually the workflow is fine, but again everything is in files and chats. Interaction is only through chats."
What is needed instead: "A UI that would make the state of each task and Dev part etc explicit and easy to interact with in a way that concerns are also separated (mocking and design is done somewhere else than implementation for example)."
The workflow is adaptable, not fixed: "On the one hand I like opinionated tooling but I also don't know if this is the best way to do this and I'm sure that it does not fit every project. So it should be adaptable/not fixed."
What went wrong with mocking was not that it mixed into implementation: "mocks got lost. And also sometimes I was mocking together with a session that also did coordination and that was annoying because of the other messages in between."
A lost mock "was not commited or pushed and got lost when the session got lost. No session could find it again."
Mocks are often visual.
A mock's course, in the author's words: "I go through with a session working on the mock until I'm satisfied. Maybe I show it to someone else to get an opinion. Then it is sent for developement and implemented."
After implementation the mock stays: "it is needed at least until development is finished but should still exist because maybe something was missed or I want to see why something was done in some way. Usually the implementation is not perfectly 1:1 what's in the mock and if that's something I do want then consulting the mock is helpful."
What moves a task on stays as in lodge's own build process: a plan goes to build once its reviews show no Blocking or Important findings, a task is done once its review passes or its fix round is rechecked, a ruling that changes the specification goes to the author, agent entries wait for her confirmation, and code reaches `main` only on her go; a mock moves on when she is satisfied and sends it to development.
Asked what is missing from that or does not work, the author: "that's fine".

## Sessions

Starting agent sessions is flexible as well: "I think the tool would start it or suggest starting it, if it runs on the server or on a machine connected to it should be flexible."
lodge also works the other way round with cloud agent sessions: "Ideally this can also interact with Claude cloud sessions, spawning and using them."
Once a cloud session runs, it talks to lodge itself, "via a public API and tools", so lodge reads a session's state and results from what the session reports rather than from Claude Code.
The author: "Tailscale funnel should work for that. And using a mailbox branch in a repo is also an option."

## Tasks and code

Code stays in git; what lodge shows about a task's code comes from git itself (branches, commits, merges, diffs, from a clone on any host), from what sessions report through the API, and from a host such as GitHub only for pull requests and its CI.
The author asked: "Does it have to be state on github or would it be state recorded by the session(s) too?"
The model is the desktop app's: "claude desktop does something a bit like this where sessions record current tasks and check them etc"; asked whether lodge should work that way, the author: "Yes I think so."
A session's report is its word; lodge checks what it can itself (the commit exists, the branch is merged, a gate rerun by the runner is green).
Agreed for the design (the author: "yes"), built in this order, the first three first:

1. A session's artefacts (a mock, a report, a review) are uploaded to the task, not left in the session's folder.
2. A new session starts from the task's steps, artefacts, and decisions, not from a chat summary.
3. Every session's open question goes into one waiting list across projects, answerable from a phone.
4. A session's task list starts from the project's workflow, so lodge sees a skipped step.
5. A step a session reports is shown apart from a step lodge has checked.
6. Usage is totalled per task and step, and a session that stopped reporting or a task in its third fix round is flagged.

## Users

lodge is for other people too: "Collaboration on projects sounds interesting. But also generally other people being able to use this would be good."

## Relation to other work

The product stays separate from an existing editor for academic writing that shares much of this ground (threads backed by sessions, agent backends, knowledge records, coordination between sessions); sharing logic between the two should be considered.
lodge was written in Python because of its first constraints; reimplementing it in another language "might be appropriate", in parts at least, since the move to a server changes those constraints.

## Open points

1. Workflow: which concerns get a place of their own; so far mocking, as described under Workflow; asked for another kind of work that went wrong the same way, the author: "I don't think so".
2. How tasks and decisions relate to code: answered, see Tasks and code.
3. Architecture and language: decided, see `2026-11-02-lodge-server-architecture-options.md`.
