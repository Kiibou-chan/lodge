# lodge as a server: feasibility and prior art

Research for `docs/superpowers/specs/2026-11-01-lodge-server-needs.md`, gathered 2026-11-01 and 2026-11-02.
Facts only, each with a source or a command; the details and every URL are in the two files beside this one.
Claude Code 2.1.312 on a Max plan, signed in with a claude.ai account, for every probe.

## Starting and using Claude Code cloud sessions

1. No public API starts, reads, or stops a cloud session; the documented routes are the CLI, scheduled tasks, and the apps.
2. `claude --cloud "<task>"` creates a session, prints its ID, its claude.ai link, and `claude --teleport <id>`, and exits 0, in about 6 seconds (probe, 2026-11-02).
3. It needs a terminal: without one it stops with `Error: --cloud requires an interactive terminal.`, so a program has to give it a pseudo-terminal (tmux worked).
   A folder the CLI has not seen before asks once whether to trust it.
4. `claude -p "<message>" --cloud <id> --output-format json` queues a follow-up and returns `{"ok":true,"session_id":…,"url":…}`; the session answered it (probe).
5. Reading back: `claude --teleport <id>` in a clean checkout of the same repository shows the whole conversation, and `/export <file>` there writes it as rendered text; teleport writes no local transcript file (probe).
6. Status and stopping exist only in the apps; no command reads whether a session is working or waiting, and none stops it.
7. Scheduled tasks can be fired by an API call with a per-task token, but their repository and prompt are fixed, and the call returns only the new session's ID and link.
8. Cloud sessions on one's own machines ("self-hosted environments", `--environment`) are for Team and Enterprise plans only, per the documentation (not probed).
9. The desktop app's own tools start, list, message, and export sessions, but only for a session inside the app, and not while it is driven over Remote Control (probe).
10. Terms: a third-party tool may not offer claude.ai sign-in, or collect, store, or relay a user's Claude credentials or session tokens; an end user may sign in to the unmodified Claude Code program with their own subscription, also where a platform hosts it (legal and compliance page).
11. Managed Agents in the Claude API offer a full session API (create, events, status, interrupt), billed per token and per session hour to an API key, not to a subscription.

## Prior art

Closest, all open source and self-hostable (details in the prior-art file):
- Delegatus (MIT, 35 stars): a board with Inbox, In progress, Waiting, and Done, build, review, and verify pipelines, a "Needs you" count with question forms, a phone board, and team sign-in by passkey; drives Claude Code and Codex.
- Kandev (AGPL-3.0, about 1,000 stars): a board with configurable multi-step workflows and a different agent per step, local, Docker, SSH, or cloud runtimes; sign-in experimental.
- Archon (MIT, about 23,800 stars): workflow graphs in YAML with approval gates and items that need attention, a worktree per run, a web console; optional sign-in.

Anthropic's own "Projects" (public beta on Pro, Max, and Ultra): one conversation starts a cloud session per task, an Overview groups them by state ("Ready for review", "Waiting on you"), and project memory holds decisions as files.
Its documentation says "A project belongs to one user. You can't share a project or its threads with another user."

Found in none of them: a decision record as an object of its own, a third-party server that starts Claude Code cloud sessions, and the combination of a configurable workflow, a question queue, sign-in for several users, and a phone-first interface.

## Not checked

Whether a teleported session can be read as structured events rather than rendered text, and how teleport behaves after a session has pushed a branch.
Seven smaller tools named in the prior-art file.

## A cloud session calling lodge

From the cloud environments page (https://code.claude.com/docs/en/cloud-environments.md), read 2026-11-02:
- Network access is per environment: None, Trusted (package registries, GitHub, cloud SDKs), Full, or Custom, where Custom lists one's own allowed domains.
- A network secret (Pro, Max, Ultra, Team, and Enterprise) is a key Anthropic's proxy adds as a header to requests for the hosts it names; the session never sees the key, and those hosts become reachable.
- Environment variables are readable by anyone who uses the environment.
- MCP connectors travel through Anthropic's servers rather than the session's network.
- So lodge has to be reachable from Anthropic's cloud on a public name; a server reachable only inside a private network is out of reach for cloud sessions.
