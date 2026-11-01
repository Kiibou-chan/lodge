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

## Relation to other work

The product stays separate from an existing editor for academic writing that shares much of this ground (threads backed by sessions, agent backends, knowledge records, coordination between sessions); sharing logic between the two should be considered.
lodge was written in Python because of its first constraints; reimplementing it in another language "might be appropriate", in parts at least, since the move to a server changes those constraints.

## Open points

1. Workflow: which concerns get a place of their own, and whether the workflow is a fixed set (plan, review, build, recheck) or defined per project.
2. Who starts sessions: the server itself, or each client, reporting in.
3. How tasks and decisions relate to code, which stays in git: branches, merges, and review.
4. Who uses it: the author and her agents only, or other people too.
5. Architecture and language, proposed once the points above are settled.
