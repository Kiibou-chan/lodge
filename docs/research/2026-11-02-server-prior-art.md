# Prior art survey (as of 2026-11-01)

Dates: GitHub API `pushed_at` / latest release, read 2026-11-01. "Unverified" marks anything not read from a source.

## 1. Vibe Kanban (BloopAI)
- URL: https://github.com/BloopAI/vibe-kanban ; announcement https://vibekanban.com/blog/shutdown
- Licence: Apache-2.0 (https://github.com/BloopAI/vibe-kanban, GitHub API https://api.github.com/repos/BloopAI/vibe-kanban). Open source.
- Self-host: yes; README links a Docker self-hosting guide for a "Vibe Kanban Cloud instance", SSH remote deployment, `VK_ALLOWED_ORIGINS` for reverse proxies (https://github.com/BloopAI/vibe-kanban).
- Agents: Claude Code, Codex, Gemini CLI, GitHub Copilot, Amp, Cursor, OpenCode, Droid, CCR, Qwen Code (README).
- Tasks/workflow: kanban issues, create/prioritise/assign; "workspace" per issue = own branch, terminal, dev server; inline diff comments sent back to agent. Fixed board model; no configurable multi-stage workflow stated (README; configurability unverified).
- Per-task threads: workspace per issue with agent session; multi-session per workspace unverified.
- Human questions: none dedicated stated (diff review feedback only).
- Decision records: none stated.
- Mobile: README lists `mobile-testing.md` only; no mobile UI claim verified.
- Multi-user: "privately or with your team", assignment (README); auth details unverified.
- Git: worktree per workspace (`.vibe-kanban-workspaces`), PRs via `gh` with AI description (README).
- Status: company bloop shut down, announced 2026-04-10: remote services (issues, comments, projects, orgs) removed after 30 days; project continues as community-maintained open source, local architecture (https://vibekanban.com/blog/shutdown). Last push 2026-10-29; latest release v0.1.44-20260424091429 (2026-04-24); 28.5k stars (GitHub API).

## 2. Paseo (getpaseo)
- URL: https://github.com/getpaseo/paseo (docs https://paseo.sh/docs). README states Apache-2.0 (README "License" section); GitHub API reports NOASSERTION because LICENSE has a custom preamble (API https://api.github.com/repos/getpaseo/paseo/license). Open source.
- Self-host: yes; "local server called the daemon", `npm install -g @getpaseo/cli`; optional E2E-encrypted relay for device pairing, or direct TCP / Tailscale / VPN (README).
- Agents: Claude Code, Codex, Copilot, OpenCode, Pi, Antigravity, Muse Code (README). Local CLIs on the daemon machine; no cloud-session launch stated.
- Tasks/workflow: no task board or workflow engine in README; unit is an agent session, each in its own git worktree; agents can create worktrees and launch other agents; plugins extend UI/agent lifecycle (README).
- Per-task threads: per-agent session timeline (README); no task-level multi-session grouping stated.
- Human questions: agents' permission requests answered in clients (plugin API "answer permissions", README); no dedicated question queue stated.
- Decision records: none stated.
- Mobile: native iOS and Android app, "the full app" (README).
- Multi-user: not stated; README says "no ... forced log-ins" (single-owner design); unverified beyond that.
- Git: worktree per agent, diff review, PR opening in app (README).
- Status: last push 2026-11-01; v0.14.0 (2026-10-29); 22.7k stars (GitHub API).

## 3. Kandev (kdlbs)
- URL: https://github.com/kdlbs/kandev ; docs under https://github.com/kdlbs/kandev/tree/main/docs/public
- Licence: AGPL-3.0 (GitHub API https://api.github.com/repos/kdlbs/kandev). Open source. Self-hosted: single Go binary with embedded web UI; Docker, k8s docs, run-as-a-service (README).
- Agents: Claude Code, Codex, GitHub Copilot, Gemini CLI, Amp, OpenCode, Cursor, Devin and about 15 more via ACP adapters (README). Runtimes: local process, Docker, SSH remote, cloud executors such as sprites.dev (README). Claude Code cloud sessions not mentioned.
- Tasks/workflow: kanban and pipeline views; workflows are configurable multi-step pipelines with automated transitions on events (enter step, message, agent turn complete), mixing a different agent per step; five shipped templates (Kanban, Plan & Build, ...); custom workflows; export/import as YAML (README; https://github.com/kdlbs/kandev/blob/main/docs/workflow-tips.md). Sub-tasks spawned by agents, multi-repo tasks (README).
- Per-task threads: task has agent sessions/chat and sub-tasks resume from the parent's session (README); multiple sessions per task exist (session tabs seen in https://github.com/kdlbs/kandev/blob/main/docs/audits/session-clarification-consolidation-2026-10-13.md).
- Human questions: "clarification" overlay where agent asks multiple-choice questions with custom answer (seen only in test-audit doc above; user docs unverified); review gates; plan step stops for human edit (workflow-tips.md). "Office mode" (experimental) adds inbox/approvals (README).
- Decision records: repo itself keeps `docs/decisions/` ADRs for its own development (https://github.com/kdlbs/kandev/tree/main/docs/decisions); product feature for decision records: none found.
- Mobile: responsive web UI with phone-specific sheets, remote access via Tailscale/Cloudflare Tunnel (https://github.com/kdlbs/kandev/blob/main/docs/public/mobile-remote-access.md). No native app.
- Multi-user: opt-in "Authentication & users" feature toggle, labelled experimental, disabled in every shipped profile; email + password, 30-day sessions, admin/member/guest roles, per-user private workspaces, team sharing (https://github.com/kdlbs/kandev/blob/main/docs/public/authentication.md). OIDC/SSO "later"; PATs for scripts; trusted-proxy header support mentioned (same doc).
- Git: worktree per task, multi-repo worktrees and per-repo PRs; GitHub/GitLab/Jira/Linear/Sentry/Azure DevOps issue import (README).
- Status: last push 2026-11-01; v0.98.0 (2026-10-23); 1.0k stars (GitHub API).

## 4. Delegatus (Latand)
- URL: https://github.com/Latand/delegatus ; guide https://github.com/Latand/delegatus/tree/main/docs/guide
- Licence: MIT (GitHub API https://api.github.com/repos/Latand/delegatus). Open source. Self-hosted: `bunx delegatus-cli`, Docker image `ghcr.io/latand/delegatus` (README). Created 2026-07-03.
- Agents: Claude Code and Codex run orchestrator and pipeline stages; Copilot runs single agents only (README). Runs on the user's machine with their CLI accounts; two machines can share a board ("linked installs", https://github.com/Latand/delegatus/blob/main/docs/guide/team.md). No Claude Code cloud sessions mentioned.
- Tasks/workflow: per-project orchestrator agent opens tasks on a board (Inbox, In progress, Waiting, Done); each task runs a pipeline of up to 8 stages (roles builder, reviewer, verifier, architect, visual critic) with verdicts pass/fail/needs-decision, fail edges back to the builder, a review-round budget and exhaustion policies `advance`, `stop-after-fix`, `park` (https://github.com/Latand/delegatus/blob/main/docs/guide/pipelines.md). Stage definitions and role presets are configurable per pipeline via API/MCP (https://github.com/Latand/delegatus/blob/main/docs/pipelines.md); a per-project editable workflow template UI is unverified.
- Per-task threads: every agent conversation (Claude, Codex, Copilot) readable as a chat with cross-search; a task's card shows its agents and pipelines, builder and reviewer conversations side by side (README).
- Human questions: first-class: "Needs you" count across projects covers a question, plan to approve, permission prompt, decision; orchestrator sends a form with a recommended answer per question, also pushed to Telegram (README; https://github.com/Latand/delegatus/blob/main/docs/guide/concepts.md).
- Decision records: durable decision record store not found; "Decisions" tab is the question form; "memory" stores learned rules for later agents (https://github.com/Latand/delegatus/blob/main/docs/guide/memory.md; contents unverified).
- Mobile: board columns become swipeable tabs, hold a card to move it; reached via Tailscale (README; https://github.com/Latand/delegatus/blob/main/docs/guide/phone.md). Also voice and Telegram bot.
- Multi-user: opt-in Team: owner invites by one-time 7-day link; sign-in by passkey, Telegram bot, or approval from a signed-in device; activity log of who answered/started what; plus a shared access key for network reach (https://github.com/Latand/delegatus/blob/main/docs/guide/team.md). Without a team set up there is no sign-in at all.
- Git: worktree and branch per pipeline, PR at the end, optional auto-merge on review pass (README).
- Status: last push 2026-11-01; v2.0.0 (2026-10-27); 35 stars (GitHub API). Anonymous daily install ping, opt-out (README). Small project.

## 5. Nuphos (nuphos)
- URL: https://github.com/nuphos/nuphos
- Licence: Apache-2.0 (README "License"; GitHub API reports NOASSERTION). Open source. Self-host: Docker Compose (MongoDB, S3-compatible storage, backend, one runtime), Railway, Helm chart; one team per deployment; managed runtime provisioning and backups not available self-hosted (README).
- Agents: Claude Code and Codex via ACP adapters, using the user's own subscriptions (README). Session can move between local, own remote machine, or Nuphos-managed cloud runtime (README); Claude Code cloud sessions not mentioned.
- Tasks/workflow: none found. Unit is a chat session ("room"); triggers (cron / webhook) start turns; GitHub and Linear panes in desktop app (README). No board, no workflow stages.
- Per-task threads: sessions are the unit; several people can join one session and steer together (README).
- Human questions: not stated beyond interactive chat.
- Decision records: none; team-wide memory built in (README).
- Mobile: native iOS app (self-hostable endpoint); Android app only for Nuphos Cloud, self-hosted endpoints "not yet supported" (README).
- Multi-user: yes, teams; email sign-in works against any backend; Google sign-in only via Nuphos Cloud (README). Slack/Discord integration.
- Git: GitHub/GitLab/Linear integrations; worktree-per-session not stated (unverified).
- Status: last push 2026-11-01; v0.101.0 (2026-11-01); 335 stars (GitHub API).

## 6. Multica (multica-ai)
- URL: https://github.com/multica-ai/multica ; docs https://multica.ai/docs ; self-hosting https://github.com/multica-ai/multica/blob/main/SELF_HOSTING.md
- Licence: "source-available" in README; Apache-2.0 plus additional conditions (Part I of LICENSE): no hosted service to third parties and no embedding in a sold product without a commercial licence; internal use within one organisation allowed (https://github.com/multica-ai/multica/blob/main/LICENSE, read via GitHub API). Not OSI open source.
- Self-host: Docker Compose or Helm (README). Also a hosted cloud at multica.ai.
- Agents: Claude Code, Codex, Cursor, Copilot, Kimi, OpenCode, Antigravity, MiniMax Code and more, run by a daemon on a machine you control ("runtime") (README, SELF_HOSTING.md). Steer a running agent mid-run for Claude Code, Codex, Grok, Kiro (README). Claude Code cloud sessions not mentioned.
- Tasks/workflow: issue tracker where agents are assignees like teammates; projects, squads (agents and people with a leader routing work), skills (playbooks), autopilots (cron), review gates ("work lands in review, not in main") (README). User-defined multi-stage workflows not found; unverified.
- Per-task threads: issue with comments plus per-run execution log with timestamped tool calls; separate chat (README https://multica.ai/docs/tasks, unread beyond README).
- Human questions: agents "raise blockers", Inbox pings when an agent needs a call (README).
- Decision records: README says "the intent, the run, the decisions, and the diff stay connected to the same issue"; no separate decision-record entity verified.
- Mobile: iOS/iPad app builds from source, not on App Store yet; web and desktop apps (README).
- Multi-user: workspaces, roles owner/admin/member, per-member access scopes to agents. Sign-in: email verification code (Resend) or code in backend logs; optional Google (`GOOGLE_CLIENT_ID`); signup controls (SELF_HOSTING.md).
- Git: GitHub, GitLab, Gitea, Forgejo integration (README); worktree-per-run not verified.
- Status: last push 2026-11-01; v0.7.2 (2026-10-30); 54.5k stars (GitHub API).

## 7. Cyrus (cyrusagents; Linear/GitHub/Slack-driven agent)
- URL: https://github.com/cyrusagents/cyrus
- Licence: Apache-2.0 (README, GitHub API https://api.github.com/repos/cyrusagents/cyrus). Open source for the community edition; Pro & Team plans configured via hosted dashboard app.atcyrus.com, where networking and integrations come from the vendor's cloud (README).
- Self-host: yes ("End-to-End Self-Hosted (Community)" with own Linear OAuth app, GitHub App, Slack App; manual guide docs/SELF_HOSTING.md) (README). Runs as a process on a machine you control; no web UI of its own: Linear/GitHub/GitLab/Slack are the UI.
- Agents: Claude Code, Codex, Cursor, Gemini, Opencode (README); BYOK.
- Tasks/workflow: tasks are the tracker's issues assigned to the agent; the agent's own workflow is not user-configurable beyond config.json (https://github.com/cyrusagents/cyrus/blob/main/docs/CONFIG_FILE.md, not read).
- Per-task threads: one Git worktree and session per issue, activity streamed into the Linear agent session (README).
- Human questions: "rich interactions like dropdown selects and approvals" in Linear/GitHub (README).
- Decision records: none. Mobile: whatever the tracker's mobile app provides (inferred; unverified). Multi-user: the tracker's own users.
- Git: worktree per issue; PRs/MRs via GitHub or GitLab CLI (README).
- Status: last push 2026-11-01; v0.2.73 (2026-09-30); 882 stars (GitHub API).

## 8. OpenHands "Agent Canvas" (OpenHands)
- URL: https://github.com/OpenHands/OpenHands ; self-hosting https://github.com/OpenHands/OpenHands/blob/main/docs/SELF_HOSTING.md
- Licence: MIT for the repo's LICENSE file (read via GitHub API); the OpenHands Enterprise offering is separate and its licence is unverified. Open source core.
- Self-host: yes. README now presents the repo as "Agent Canvas: the self-hosted developer control center for coding agents and automations"; runs locally, in Docker sandboxes, on VMs, with several switchable "agent backends" (README). Also OpenHands Cloud and Enterprise (README).
- Agents: OpenHands agent, Claude Code, Codex, Gemini CLI, Pi, OpenCode, any ACP agent (README). Backends: local, remote, cloud; not Claude Code cloud sessions.
- Tasks/workflow: conversations plus "automations" (schedule or webhook triggered, e.g. decomposing GitHub issues into tasks, reports to Slack) (README). No kanban or staged pipeline found.
- Per-task threads: one conversation per run, persisted; backend can be switched without losing focus (README).
- Human questions: not stated (conversation only). Decision records: none. Mobile: not stated.
- Multi-user: self-hosted Canvas uses a single shared API key (`LOCAL_BACKEND_API_KEY`, X-Session-API-Key header) behind nginx; docs say sizing is for "a single user" (SELF_HOSTING.md). A team can share one Agent Server (README). Per-user accounts are not part of the self-hosted Canvas as far as read; Enterprise unverified.
- Git: workspace per conversation; worktrees recommended manually to avoid conflicts when conversations share a host directory (README).
- Status: last push 2026-11-01; v1.34.0 (2026-10-27); 92k stars (GitHub API).

## 9. Nimbalyst (formerly Crystal)
- URL: https://github.com/nimbalyst/nimbalyst ; predecessor https://github.com/stravu/crystal (description "Crystal is now Nimbalyst"; last push 2026-02-26, v0.3.5, MIT, 3.1k stars; GitHub API)
- Licence: MIT (README, GitHub API). Open source. Not a server: desktop app (macOS, Windows, Linux) plus iOS companion; no self-hosted multi-user server (README).
- Agents: Codex, Claude Code; OpenCode and Copilot alpha; Gemini provider (README).
- Tasks/workflow: session kanban board of agent sessions; task trackers (plans, bugs, features, todos) stored as markdown in the repo that agents read/update; "workflows in slash commands"; no configurable stage pipeline found (README).
- Per-task threads: parallel sessions, each in its own git worktree, linked to files they touched; search and resume (README).
- Human questions: iOS app shows "which agents need you", reply to questions by text or voice, push notifications (README).
- Decision records: none stated; plain files on disk in the repo.
- Design/mocking: built-in WYSIWYG editors for markdown, mockups with annotations, Mermaid, Excalidraw, data models, with red/green diff review of agent edits (README). The same app, so design and implementation are not split across places.
- Mobile: iOS companion app only (README).
- Multi-user: README mentions a collaboration sync protocol (`packages/collab-protocol`) whose server (wss://sync.nimbalyst.com, a Cloudflare Worker) is "a separate project" not in the repo; self-hostability of that server unverified.
- Git: worktree per session, commit and branch management in app (README).
- Status: last push 2026-10-31; v0.81.7 (2026-10-16); 2.0k stars (GitHub API).

## 10. Claude Squad (smtg-ai)
- URL: https://github.com/smtg-ai/claude-squad
- Licence: AGPL-3.0 (GitHub API). Open source. Terminal app (`cs`, tmux-based), local only, single user; no server or web UI (README).
- Agents: Claude Code, Codex, Gemini, Aider and other local agents (README).
- Tasks/workflow: one instance per task; no board or stages (README).
- Per-task threads: one isolated git workspace and tmux session per task; review changes before applying (README).
- Human questions, decision records, mobile, multi-user: none stated.
- Git: separate workspace (worktree) per task, checkout before pushing (README).
- Status: last push 2026-08-20; v1.0.20 (2026-08-20); 8.7k stars (GitHub API). Quiet for about 10 weeks as of 2026-11-01.

## 11. Backlog.md (MrLesk)
- URL: https://github.com/MrLesk/Backlog.md
- Licence: MIT (README, GitHub API). Open source. Not a server: local CLI, terminal kanban, and `backlog browser` local web board; "no server, no account, no telemetry" (README).
- Agents: any MCP/CLI-capable assistant: Claude Code, Gemini CLI, Codex, Kiro, Cursor (README). It does not start agent sessions.
- Tasks/workflow: every task is a Markdown file in the repo with acceptance criteria, definition of done, milestones, dependencies; three review checkpoints (spec, plan, code) as convention, not an enforced configurable workflow engine (README). Completed tasks stay in Git as a record of what was attempted and why.
- Per-task threads: task file holds plan and notes; one task = one context window = one PR as convention (README). No thread UI.
- Human questions: none dedicated. Decision records: `backlog search` covers "tasks, docs & decisions" (README), so decisions exist as a document type; format not read.
- Mobile: not stated (local web UI). Multi-user: via git only; no auth (README).
- Git: tasks live in the repo; cross-branch task state is handled via git; worktree/PR automation not stated.
- Status: last push 2026-10-29; v1.55.3 (2026-10-23); 7.2k stars (GitHub API).

## 12. Sculptor (Imbue)
- URL: https://github.com/imbue-ai/sculptor
- Licence: MIT per GitHub API; README says external contributions are not being taken on at scale and "it's not truly open source until the community is involved" (README). Treat as source-visible research preview.
- Not a server: desktop app for macOS (Apple Silicon) and Linux; no multi-user, no self-hosted server (README).
- Agents: Claude Code and Pi integrated; any terminal agent runnable (README).
- Tasks/workflow: workspaces (isolated worktrees of the repo) with several agents per workspace; bundled workflow skills (spec, mocks, fix-bug) as slash commands, not a configurable stage engine (README).
- Per-task threads: chat per agent in a workspace (docs/help/chat.md, docs/help/agents.md, not read). Human questions, decision records, mobile: none stated.
- Git: worktree per workspace, in-app change review, commit, GitHub PR tracking (README).
- Status: last push 2026-11-01; sculptor-v0.49.0 (2026-10-21); 242 stars (GitHub API).

## 13. Terragon (terragon-oss) -- shut down
- URL: https://github.com/terragon-labs/terragon-oss
- Licence: Apache-2.0 (GitHub API). README: "open-source snapshot of Terragon at the time of shutdown" (snapshot notice dated 2026-01-16), no maintenance (README). Last push 2026-02-10; no releases (GitHub API 404 on releases/latest); 261 stars.
- Was a hosted cloud background-agent service: agents (Claude Code, Codex, Amp, Gemini) in sandbox containers, branch per task, auto PRs, `terry` CLI for local takeover, MCP server for task creation, automations, Slack/GitHub @-mentions, real-time browser task status (README). Self-hosting it needs Postgres, Redis, Stripe CLI (dev setup in README); not a supported product.
- Included as stale reference; useful as a design precedent for the "cloud sandbox plus local handoff" idea.

## 14. Archon (coleam00)
- URL: https://github.com/coleam00/Archon ; docs https://archon.diy
- Licence: MIT (README, GitHub API). Open source. Self-hosted: one install, SQLite default or PostgreSQL; Docker Compose + Caddy, VPS guides (README; docs deployment pages in repo `packages/docs-web/src/content/docs/deployment/`). Sends anonymous telemetry events (README).
- Agents: Claude Code, Codex, Pi via their CLIs/SDKs with own accounts (README).
- Tasks/workflow: the closest on workflow: YAML workflow graphs in `.archon/workflows/` with nodes for agent prompts, loops (`until_bash`, fresh context), scripts, `wait` approval gates with forms, `when:` conditions; bundled `sdlc` pack goes issue -> plan -> implement -> specialist review -> fix -> CI -> merge queue; per-repo custom workflows (README). Task = run of a workflow; issues come from GitHub.
- Per-task threads: each run has an event log and transcript; runs get a worktree each (README). Multi-session grouping per task not stated.
- Human questions: first-class: a run pauses as one "attention item" with what/why/recommendation/choices; answer in web console (`archon serve`), terminal (`archon workflow attention`), or Slack/Telegram/Discord/GitHub adapters (README).
- Decision records: approvals are logged per run; a separate decision-record store not found. Answers are written into the issue as scope (README).
- Mobile: no mobile UI claim; chat adapters (Slack, Telegram, Discord) serve as the remote channel (README).
- Multi-user: optional web login via Better Auth (`DATABASE_URL`, `BETTER_AUTH_SECRET`), server-side API gate; or trusted identity header `X-Archon-User` from a reverse proxy (https://github.com/coleam00/Archon/blob/main/packages/docs-web/src/content/docs/deployment/reverse-proxy.md). Multi-user mode exists (telemetry doc names it); roles/permissions unverified.
- Git: worktree per run, PRs via `gh`, merge queue with review-verdict and CI gate (README).
- Status: last push 2026-10-31; v0.13.2 (2026-10-29); 23.8k stars (GitHub API).

## 15. Paperclip (paperclipai)
- URL: https://github.com/paperclipai/paperclip ; docs https://docs.paperclip.ing
- Licence: MIT (GitHub API; README "Open source. Self-hosted. No Paperclip account required"). A cloud waitlist exists (README).
- Self-host: Node.js server + React UI, Docker, Tailscale/private-network bind for remote access (README).
- Agents: OpenClaw, Claude Code, Codex, Cursor (+Cloud), Gemini CLI, OpenCode, Pi, Hermes, Grok Build, Kimi Code; any process or HTTP endpoint (README). Aimed at running a "company" of agents (org chart, budgets, goals), explicitly "Manage business goals, not pull requests" (README): a different framing from a per-project dev task server.
- Tasks/workflow: task manager with approvals and review gates, routines and workflows; agents claim tickets; per-project workflow stages user-defined: unverified.
- Per-task threads, human questions: approvals and review gates; "chime in when needed" (README); dedicated question queue unverified.
- Decision records: none found (audit trail, run history). Mobile: README has a "Mobile Ready" feature section (line 156; text not fully read). Multi-user: two deployment modes (trusted local / authenticated), human roles and permissions, company memberships, invite flows; SSO/RBAC listed in the "Agentic OS" pillar (README; whether SSO ships in self-hosted OSS is unverified).
- Git: optional isolated execution workspaces (git worktrees, operator branches) (README).
- Status: last push 2026-11-01; v2026.1023.0 (2026-10-24); 109.9k stars (GitHub API).

## 16. Anthropic Claude Code cloud sessions and Projects (hosted; read for completeness since the author targets cloud sessions)
- URLs: https://code.claude.com/docs/en/claude-code-on-the-web ; https://code.claude.com/docs/en/claude-projects.md ; self-hosted environments https://code.claude.com/docs/en/self-hosted-environments (linked from the first page, not read)
- Not open source; hosted by Anthropic. Sessions can be routed to an organisation's "self-hosted environment" (runner on own infra) (claude-code-on-the-web). Needs claude.ai account; unavailable through Bedrock/Vertex (same page).
- Agent: Claude Code only.
- Cloud sessions: start from claude.ai/code, mobile Code tab, desktop, `claude --cloud`; `--teleport` pulls a session into a terminal (one-way); follow-ups by `claude -p "..." --cloud <id>`; sessions persist after closing the laptop; Team/Org visibility sharing; Auto-fix for PRs via the Claude GitHub App (claude-code-on-the-web). GitHub required for clone/PR in Anthropic-hosted environments.
- Projects (public beta on Pro/Max/Ultra, not Team/Enterprise): one ongoing conversation that starts a thread per task; each thread is usually a cloud session, or a session on the user's own machine via Remote Control; "Overview" pane groups threads by state: Ready for review, Waiting on you, Working, Landing, Idle, Resolved; project memory (decisions, pitfalls as files, `MEMORY.md` index) and project instructions up to 16,000 characters; phone and desktop notifications; usable from phone (claude-projects.md).
- Limits stated there: "A project belongs to one user. You can't share a project or its threads with another user"; no organisation-level controls in beta; a thread belongs to one project (claude-projects.md, Limitations).
- Workflow configurability: none beyond project instructions and memory; Git: branch and PR per thread via GitHub.
- Status: docs as read 2026-11-01 (WebFetch of the pages above).

## 17. Linear agents (issue tracker with agent integration)
- URLs: https://linear.app/docs/agents-in-linear ; https://linear.app/developers/agent-interaction
- Not open source, not self-hostable (hosted SaaS; self-hosting not mentioned on either page, treated as unverified-no). Agents are third-party apps installed from the Integrations Directory by workspace admins; they are not billable seats (docs page above). Which agents ship (Cursor, Codex, Devin, etc.): not on these pages; unverified.
- Tasks/workflow: Linear issues with the tracker's own states; assign ("delegate") an issue or @mention the agent; agent workflow is whatever the agent app does. Workspace- and team-level guidance text for agents (docs page).
- Per-task threads: an `AgentSession` per run, with activity types thought, action, elicitation, response, error; session states pending, active, error, awaitingInput, complete, stale (developers page).
- Human questions: first-class `elicitation` activity; the user's reply arrives as a `prompt` activity (developers page). Agent Plan API (session-level checklist) in technology preview.
- Decision records: none (issue comments and documents). Mobile: Linear has mobile apps (not verified on these pages). Multi-user: workspace members, admins choose which teams can access an agent.
- Git: agents open PRs; branch/worktree handling is up to the agent app (docs page). Cyrus (entry 7) is a self-hostable example of such an agent.

## 18. GitHub Copilot cloud agent (hosted)
- URL: https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-coding-agent (page now describes "Copilot cloud agent" and "Copilot in the cloud")
- Not open source; hosted by GitHub. Actions-based sessions can use custom compute and self-hosted runners; cloud sandbox sessions cannot (same page). Works only with GitHub-hosted repositories.
- Agents: Copilot; page does not mention Claude, Codex or Agent HQ (unverified whether other agents can be chosen; model choice depends on plan).
- Tasks/workflow: start from Copilot home, panel in file/issue/PR, dashboard, or the repository's Agents tab; GitHub Mobile is a client for starting and continuing sessions; one branch per session and one PR per task; Agent Merge ("Watch and fix") for failed workflows and conflicts; fixed workflow, not configurable (same page).
- Per-task threads: session with logs of work and tools; sessions and PRs shareable with teammates with repository access (same page).
- Human questions: iteration happens in the session before a PR; PR-comment-driven iteration not described on this page. Decision records: none. 
- Multi-user: repository permissions; read-only without write access; SSO requirements for org data (same page). New experience from 2026-10-28 for paid plans (same page).

## 19. OpenAI Codex cloud (hosted)
- URL: https://learn.chatgpt.com/docs/cloud (redirected from https://developers.openai.com/codex/cloud)
- Not open source for the cloud service; not self-hostable (self-hosting not mentioned on the page; unverified).
- Agent: Codex. Start from ChatGPT web, mobile and desktop apps, CLI, Slack, Linear; environments hold dependencies, secrets, network settings; each task gets its own workspace; commit or open a PR; follow-up changes on a task; environment access "Only me" or whole organisation (page above). Branch handling, thread continuity, plans: not on the page.

## 20. Hosted agents, short entries (all closed source, none self-hostable as a server; dates not on the pages)
- Cursor cloud agents (formerly Background Agents), https://cursor.com/docs/cloud-agent : isolated cloud VMs; start from iOS app, cursor.com/agents, desktop, Slack, Linear, API, or @cursor on GitHub/Bitbucket PR or issue; own branch per agent, PRs per repo, screenshots/videos/log artifacts; "Self-Hosted Machines" option runs tool execution on own hardware; team members can see agents, read-only unless an admin enables team follow-ups. Agent: Cursor's own.
- Devin, https://docs.devin.ai/get-started/devin-intro : starts from Linear/Jira tickets, Slack/Teams, web app, API, CLI; session with shell, IDE, browser; user can follow and take over; draft PRs; Individual and Teams plans. Mobile, self-hosting, VPC: not mentioned on the page (unverified).
- Google Jules, https://jules.google/docs : GitHub-only; select repo and branch, prompt, "Give me a plan", plan reviewed and approved before code changes; notifications when finished or needs input; experimental; mobile/pricing not on the page.
- Conductor, https://www.conductor.build : Mac-only app (per the page), parallel Claude Code, Codex, Cursor agents in isolated workspaces, review and merge; latest release linked 0.92.0; open-source status, mobile, team features not stated on the page (unverified; likely closed).
- Claude Squad, Sculptor, Terragon, Nuphos: see entries above (10, 12, 13, 5).

## 21. Open-Inspect (ColeMurray/background-agents)
- URL: https://github.com/ColeMurray/background-agents ; auth doc https://github.com/ColeMurray/background-agents/blob/main/docs/AUTH.md
- Licence: MIT (GitHub API). Open source. "Self-host" = deploy your own: control plane on Cloudflare (README architecture diagram), sandboxes elsewhere (provider not read); single-tenant only, teams add access control not tenant isolation (README). Modelled on Ramp's Inspect (README).
- Agents: Claude (API key or connected subscription via the Claude Agent harness), OpenAI Codex, xAI Grok, OpenCode Zen (README). Sandboxed cloud dev environments, not local machines.
- Tasks/workflow: sessions started from web UI, Slack, GitHub PRs, Linear, webhooks; scheduled and event-driven automations (GitHub events, Sentry); parallel sub-tasks in separate sandboxes; no board and no stage workflow (README).
- Per-task threads: a session each; "multiplayer sessions" where several people collaborate in real time (README).
- Human questions, decision records, mobile: not stated.
- Multi-user: teams, workspace roles, session visibility Workspace/Team/Private; sign-in with GitHub and/or Google, admitted by GitHub username, verified email, email domain, or GitHub organisation membership (docs/AUTH.md).
- Git: PRs with commit attribution to the prompting user (README).
- Status: last commit 2026-10-31 (GitHub API commits); no releases (404); 3.4k stars.

## Sign-in options for a self-hosted multi-user server
- Passkeys / WebAuthn: operator needs HTTPS (secure context only), a stable relying-party ID matching the domain, server-side verification of challenge and origin, and storage of each user's public key; plus a recovery path (https://developer.mozilla.org/en-US/docs/Web/API/Web_Authentication_API). Delegatus ships passkeys with an owner recovery command (https://github.com/Latand/delegatus/blob/main/docs/guide/team.md).
- GitHub sign-in: register an OAuth app (or GitHub App) and supply client ID, client secret, and callback URL; GitHub's flow is OAuth 2.0, and the page read does not describe OpenID Connect (https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps). Access rules (username, org membership) are then the operator's own, as in Open-Inspect (https://github.com/ColeMurray/background-agents/blob/main/docs/AUTH.md).
- Google OIDC: Cloud Console project, OAuth client ID and secret, exact registered redirect URIs, consent screen; restrict by the `hd` claim, not by email domain (https://developers.google.com/identity/openid-connect/openid-connect).
- Tailscale identity headers: Tailscale Serve (HTTPS certificates enabled in the tailnet) adds `Tailscale-User-Login`, `-Name`, `-Profile-Pic` for tailnet traffic, strips client copies, absent on Funnel and for tagged devices; the app must listen on localhost only so nobody can forge the headers (https://tailscale.com/kb/1312/serve). Every user must be on the tailnet; Archon documents the same trusted-header pattern with `X-Archon-User` (https://github.com/coleam00/Archon/blob/main/packages/docs-web/src/content/docs/deployment/reverse-proxy.md).
- Magic links: operator supplies outbound email (SMTP or an email API) and a sender domain with deliverability set up; links are single-use and expire (Better Auth default 5 minutes) (https://www.better-auth.com/docs/plugins/magic-link). Multica's email codes need a Resend key (https://github.com/multica-ai/multica/blob/main/SELF_HOSTING.md).

## Method notes
- Fetched 2026-11-01/02 one request at a time; no HTTP 429 encountered on any site. GitHub data via authenticated `gh api` (rate limit not reached).
- Descriptions from WebFetch are summarised by a small model; README quotes were read directly via `gh api` for entries 2-15, 21. Hosted-vendor entries (16-20) rest on a single docs page each.
- Not checked: Open Session (tellahq/opensession), Garcon, intentic, MultiCC, Pragma, Cezar, qm, Emdash, Superset/Paradev, Mux (desktop apps or small projects seen in https://github.com/andyrewlee/awesome-agent-orchestrators); metadata only: superset-sh/superset (pushed 2026-11-01, v2.0.3), generalaction/emdash (Apache-2.0, v1.2.10 2026-10-30), coder/mux (AGPL-3.0, v0.32.1 2026-10-27).
- Gaps worth noting: no tool found with a persistent decision-record entity as a first-class object (Backlog.md has "decisions" documents, Kandev keeps ADRs for its own repo, Claude Projects keeps "decisions" in memory files); none found that start Claude Code cloud sessions from a third-party server (Claude Code's own `--cloud` and `claude -p --cloud <id>` exist: https://code.claude.com/docs/en/claude-code-on-the-web).
