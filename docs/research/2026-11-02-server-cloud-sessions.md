# Driving Claude Code cloud sessions from a self-hosted program

Research date: 2026-11-01. Sources are official docs on code.claude.com, platform.claude.com and claude.com, read through WebFetch. Items marked UNVERIFIED were not confirmed in a doc.

## Summary table

| Route | Exists | Program-drivable | Auth | Billing | Read output / status / stop |
|---|---|---|---|---|---|
| 1. Claude Code on the web via CLI (`claude --cloud`, `-p --cloud <id>`) | Yes | Partly: send a follow-up non-interactively; start on Anthropic-hosted not documented non-interactively | claude.ai login (`claude auth login`); no API key, no setup-token | Subscription | No |
| 1b. Self-hosted environments (`-p --environment ccpool_...`) | Yes, but Team/Enterprise only (public beta) | Yes, start and follow-up with JSON output | claude.ai OAuth token, not API key | Org Claude Code usage (Team/Enterprise seats) | Only via a Stop hook on the runner, not an API |
| 2. Scheduled tasks ("routines") + API trigger `/fire` | Yes (research preview; fire endpoint "experimental") | Yes, start only | Per-routine bearer token `sk-ant-oat01-...` | Subscription usage | No: returns session ID and URL, nothing else |
| 3. Agent SDK | Yes | Local process only; runs the Claude Code binary on your host | Docs: API key or cloud provider; claude.ai login NOT allowed for third-party developers | API pricing per docs' guidance | Not cloud sessions |
| 4. Managed Agents | Yes (beta) | Yes, full REST API | Console API key (`x-api-key`) | API: tokens at model rates + $0.08 per session-hour | Yes: status, events list, SSE stream, interrupt, archive, delete |
| 5. claude-code-action (GitHub Actions) | Yes | Indirectly (GitHub `workflow_dispatch`/repository events, GitHub-side API) | `ANTHROPIC_API_KEY` or `CLAUDE_CODE_OAUTH_TOKEN` (from `setup-token`) | API key = API billing; OAuth token = subscription | Result in run log or PR/issue comment; stop = GitHub cancel |
| 6. Multi-user | See per-route notes | No documented route for one server to start sessions under several users' subscriptions | Each user's own login required; storing or routing their credentials is restricted | n/a | n/a |

Bottom line for a Max-plan user: the only documented, subscription-billed, program-startable path is the routine API trigger (route 2). It can start a run with a text payload, against one pre-configured repo and prompt per routine. It cannot read output, query status, or stop. Driving full sessions (send, read, stop) from a server requires API billing (route 4), or a self-hosted environment, which Max does not get.

---

## Route 1: Claude Code on the web via the CLI

**Exists?** Yes. Start: `claude --cloud "<task>"` (`--remote` is a deprecated alias). Follow-up: `claude -p "<msg>" --cloud <session-id>`. Pull into terminal: `claude --teleport [id]`. Source: https://code.claude.com/docs/en/claude-code-on-the-web.md (sections "Start a cloud session from your terminal", "Send follow-ups from the CLI", "Continue a cloud session in your terminal").

**Driveable by a program?** Partly.
- Follow-up: yes. `claude -p "msg" --cloud <id> --output-format json` posts one message and exits. Output: `{ok, session_id, url}` or `{ok:false, session_id, error}`. `--output-format stream-json` is NOT supported with `--cloud <session-id>`. Accepts bare `session_...` or `cse_...` ID, or the claude.ai/code URL. Same doc.
- Start on Anthropic-hosted: NOT documented non-interactively. Headless doc: "Claude Code rejects `--bg`, and rejects `--cloud` with a task description, with an error naming the conflict." Source: https://code.claude.com/docs/en/headless.md. The testing page confirms: "`--cloud` is rejected with a session ID or URL, and in non-interactive runs when it carries a description. A bare `--cloud` is treated as absent." Source: https://code.claude.com/docs/en/self-hosted-environments-testing.md (section "`--environment` dispatch behavior").
- Read transcript, result, status, stop: NO CLI command or API documented. Read by opening the claude.ai/code URL in a browser, or `--teleport` into a local checkout (one-way, copies the session into the terminal). Archive and delete are UI-only (sidebar or session menu).

**Auth:** `claude auth login` with a claude.ai account. Docs: "`--cloud` requires an Anthropic account." Rejected: Bedrock, Vertex AI, Foundry; API key and Console sign-in ("Cloud sessions aren't available with this Console sign-in"; "API key authentication is not sufficient"). Org policy `allow_remote_sessions` must be on. Source: claude-code-on-the-web.md, sections "Send follow-ups from the CLI" and "Unable to get organization UUID".

**Billing:** Subscription. "It counts toward your plan's usage limits alongside the rest of your Claude and Claude Code usage, and there's no separate charge for the cloud VM." Plans: Pro, Max, Ultra, Team, and Enterprise with premium or Chat + Claude Code seats. Not available to organizations with Zero Data Retention, HIPAA configuration, or CMEK. Source: claude-code-on-the-web.md intro note.

**Capabilities (route 1 as a whole):** start with prompt and repo (current directory's GitHub remote at current branch; bundled upload when no GitHub remote); branch is the one pushed to GitHub, uncommitted local changes are not included ("Branch <name> is not on GitHub" warning); follow-up message; read result via browser or teleport; status, stop: not documented.

**Compliance API (admin only, not verified in detail):** https://platform.claude.com/docs/en/api/compliance/apps/sessions/remote/list.md ("List remote (cloud) sessions for compliance") and https://platform.claude.com/docs/en/manage-claude/compliance-sessions.md ("Retrieving session transcripts"). These are organisation-compliance endpoints, presumably Enterprise. Access requirements UNVERIFIED. Not a route for a Max user.

**Public REST API for claude.ai/code cloud sessions:** not found. No sessions endpoint on code.claude.com or claude.ai docs for starting or steering these sessions.

**URLs:**
- https://code.claude.com/docs/en/claude-code-on-the-web.md
- https://code.claude.com/docs/en/web-quickstart.md
- https://code.claude.com/docs/en/headless.md
- https://code.claude.com/docs/en/self-hosted-environments-testing.md

---

## Route 1b (coordinator questions a, b): self-hosted environments, `--environment`, `ccpool_` IDs

**Exists?** Yes, public beta, Team and Enterprise only. "Self-hosted environments are in public beta on Team and Enterprise plans and are off by default." An Owner turns on "Allow self-hosted environments" on the Cloud environments admin page. Source: https://code.claude.com/docs/en/self-hosted-environments.md ("Availability and limitations") and https://code.claude.com/docs/en/self-hosted-environments-quickstart.md ("Organization and roles").

**Consequence for a Max user:** the docs do not offer self-hosted environments on Max. Not available. Route closed for this user, confirmed from plan statements only (no explicit "Max not eligible" sentence seen; treat as "not offered on Max per plan statement").

**What it is:** environment = named group of runners (created on claude.ai admin page). Environment ID is `ccpool_...` in the CLI and docs ("`ccpool_...` ID"); API field name is `pool_id` ("In API fields... the environment appears as `pool`, and the environment ID is the `pool_id`"). Environment secret = the "environment key" shown once at creation, expires 365 days after creation, passed to the runner as a file. Source: quickstart "Set up manually".

**How a machine joins:** install Claude Code v2.1.224+ on a Linux or macOS host (Windows not supported as runner host). Command:
```
claude self-hosted-runner --environment-secret-file '/etc/claude/environment-secret' --base-dir '<writable-dir>'
```
Runner registers and polls for work (outbound HTTPS only; "Anthropic never connects into your network"). Runner exits by design after serving one session unless restarted or run under an orchestrator. Source: quickstart and self-hosted-environments.md ("How self-hosted environments work", "Network paths").

**Starting a session on it (non-interactive, documented):**
```
claude -p "<prompt>" --environment <ccpool_id> --output-format json
```
Run from a git checkout (repo auto-detected from `origin`); optional `--ref <branch>`. Prints one JSON line: `{"ok":true,"session_id":"session_...","title":"...","url":"...","pool_id":"..."}`; on failure `{"ok":false,"error":"..."}` with exit 1. Command exits without waiting for Claude's reply. `--output-format stream-json` not supported. Source: self-hosted-environments-testing.md ("Run the test loop", "`--environment` dispatch behavior").

**Follow-up:** `claude -p "<msg>" --cloud <session_id> --output-format json` (same as route 1).

**Read reply:** NOT via API. The docs' CI recipe installs a Stop hook on the runner that writes `last_assistant_message` to a local file, and the driver script reads the file. The docs say: "so the only calls to the Anthropic API are the two dispatches themselves." This works only where the driver runs on the runner host (or uses a POST variant on separate infrastructure). Source: self-hosted-environments-testing.md.

**Stop:** not documented for the environment path. Archive and delete via UI.

**Auth to dispatch:** claude.ai OAuth token. Docs: "Both `claude -p ... --environment` and `claude -p ... --cloud` authenticate with a claude.ai OAuth token; API keys, such as `sk-ant-xxxxx`, aren't accepted for either call." Long-lived CI host: run `claude auth login` once interactively; refresh-token grant "capped at 30 days from the initial login", so re-login every 30 days. Ephemeral CI: "There is no long-lived CI token for this today." `claude setup-token` does not cover it. Source: testing page, "Authenticate from CI".

**Billing:** "sessions in a self-hosted environment consume your organization's Claude Code usage the same way sessions in Anthropic-hosted environments do." Model inference defaults to api.anthropic.com with a session-scoped token; can be routed to Bedrock or Agent Platform. Source: self-hosted-environments.md ("Availability and limitations", "Network paths").

**Does it put cloud sessions on the user's own server?** Yes, that is the purpose. But: Team/Enterprise only, Owner must enable it, so not available to this Max user.

**URLs:**
- https://code.claude.com/docs/en/self-hosted-environments.md
- https://code.claude.com/docs/en/self-hosted-environments-quickstart.md
- https://code.claude.com/docs/en/self-hosted-environments-testing.md
- https://code.claude.com/docs/en/self-hosted-environments-reference.md (not read; CLI flag reference)
- https://code.claude.com/docs/en/self-hosted-environments-deploy.md (not read)

---

## Route 1c (coordinator question c): Remote Control and spawning sessions

**Exists?** Yes. `claude remote-control` (server mode) and `/remote-control`. Source: https://code.claude.com/docs/en/remote-control.md ("Start a Remote Control session").

**What it is:** runs on the user's own machine. "When you start a Remote Control session on your machine, Claude keeps running locally the entire time." Clients (claude.ai/code, Claude mobile app) connect to it. Sessions stay local, not cloud.

**Can a program on the server spawn and steer sessions?** Partly, and not by a documented API:
- Server mode can run several sessions: `--capacity <N>` (default 32), `--spawn same-dir|worktree|session`, `--permission-mode`, `--name`, `--continue`, `--session-id`. Sessions are created by clients connecting to the server (claude.ai/code or mobile), or by the pre-created session. No documented flag or endpoint lets a third-party program create or send a message to a session.
- Interactive sessions: "each Claude Code instance supports one remote session at a time."
- Protocol for third parties: none documented (grep of the page for "API", "program", "protocol": only infrastructure descriptions).

**Auth:** claude.ai full-scope login. Explicitly NOT: API key (`ANTHROPIC_API_KEY`, `ANTHROPIC_AUTH_TOKEN`, `apiKeyHelper`) and NOT `claude setup-token` / `CLAUDE_CODE_OAUTH_TOKEN`: "These tokens can only make model requests, so they can't establish Remote Control sessions. Run `claude auth login`..." Source: remote-control.md, "Remote Control requires a full-scope login token" troubleshooting entry. Authentication page confirms `setup-token` "can't establish Remote Control sessions". Source: https://code.claude.com/docs/en/authentication.md ("Generate a long-lived token").

**Billing:** plan required: "Subscription: available on Pro, Max, Ultra, Team, and Enterprise plans. API keys are not supported." Usage billing on the subscription is implied, not stated explicitly in the sections read (UNVERIFIED as explicit statement).

**Multi-user:** the server connects with one user's account; "Auto-connect signs in with your own claude.ai account, so a session it starts appears only in your own account's Claude apps and grants no one else access."

**URLs:** https://code.claude.com/docs/en/remote-control.md; https://code.claude.com/docs/en/authentication.md

---

## Route 2: Scheduled tasks ("routines") and the API trigger

**Exists?** Yes. Research preview: "Scheduled tasks are in research preview. Behavior, limits, and the API surface may change." Renamed from "routines", which "still appears" in some UI. Source: https://code.claude.com/docs/en/routines.md (returns "Automate work with scheduled tasks").

**Driveable by a program?** Start only.
- Endpoint: `POST https://api.anthropic.com/v1/claude_code/routines/{routine_id}/fire` (routine_id is prefixed `trig_`).
- Headers: `Authorization: Bearer sk-ant-oat01-...` (per-routine token, generated on claude.ai/code/routines, shown once); `anthropic-version: 2026-10-21` (any version from 2023-06-01 accepted); `Content-Type: application/json`.
- Body: optional `{"text": "..."}`, max 65,536 characters, freeform. Not parsed. Delivered inside a `<routine-fire-payload>` block labelled as untrusted; the saved prompt must reference it to act on it. Unknown fields ignored. There is NO repo, branch, prompt, or model field: those are fixed in the saved task.
- Response 200: `{"type":"routine_fire","claude_code_session_id":"session_...","claude_code_session_url":"https://claude.ai/code/session_..."}`. Returns once session is created; does not stream or wait.
- Errors: 400 (bad version header, text over limit, routine paused); 401 (token mismatch); 403; 404; 429 with `Retry-After`; 500; 503.
- No idempotency: "Each successful request creates a new session. There is no idempotency key."

**Read transcript, status, or stop via API:** NONE. "Token scope: One routine only; no read access." "There is no public API for token management." The scheduled-tasks page documents run history only in the UI and in `/schedule` in the CLI (`/schedule list|update|run`, and `/schedule why did my ...` which reads run logs, v2.1.227+). Run statuses are "Succeeded", "Failed", "Cancelled" shown on the web. No API for these documented.

**Auth:** per-routine bearer token, generated in the web UI (or via the trigger settings). Account: claude.ai on Pro, Max, Ultra, Team, or Enterprise. Scheduled tasks "belong to your individual claude.ai account." Source: https://code.claude.com/docs/en/routines.md ("Add an API trigger", "Trigger a scheduled task", "Where the name routines still appears"); https://platform.claude.com/docs/en/api/claude-code/routines-fire.md.

**Billing:** Subscription usage. Fire endpoint doc table: "Billing: Claude Code subscription usage on claude.ai" versus "Claude Platform usage". Runs "draw down subscription usage the same way interactive sessions do." When the subscription limit is hit, runs are rejected unless usage credits are on (metered overage).

**Limits (hourly):**
- Per routine: 30 fires/hour, shared across API fires, "Run now", and one-off re-arms.
- Per account: 100 API fires/hour across all routines.
- Scheduled runs: 100/hour per account.
- Schedule presets: no run more often than hourly (custom cron more often than hourly rejected).
- "None of these hourly limits has overage."
Source: routines.md "Usage and limits"; routines-fire.md "Rate limits".

**Other triggers:** schedule (preset or cron, UTC for 5-field cron, or one-off), GitHub events (PR, release, etc.). A task can combine several triggers. Source: routines.md.

**Requirement caveats:** GitHub connection must stay valid, or the task skips runs for up to 72 hours. Source: routines.md "Troubleshooting" or GitHub section. Paused subscription holds tasks.

**URLs:**
- https://code.claude.com/docs/en/routines.md (Automate work with scheduled tasks; sections "Add an API trigger", "Trigger a scheduled task", "Usage and limits")
- https://platform.claude.com/docs/en/api/claude-code/routines-fire.md ("Trigger a routine through the API", marked experimental)
- https://claude.ai/code/routines (creation UI)

---

## Route 3: Agent SDK

**Exists?** Yes. Python `claude-agent-sdk`, TypeScript `@anthropic-ai/claude-agent-sdk`. Source: https://code.claude.com/docs/en/agent-sdk/overview.md.

**Local only?** Yes. "A library that runs the Claude Code binary, ... in a process you operate." It runs the agent on the machine where your program runs; it does not start Anthropic-hosted cloud sessions. Cloud routing is not described on the SDK overview or quickstart. Cloud sessions are not in the SDK capabilities list (built-in tools, hooks, subagents, MCP, permissions, sessions, skills, plugins).

**Auth:** API key. Quickstart: "set your API key ... `export ANTHROPIC_API_KEY=your-api-key`", plus Bedrock, Claude Platform on AWS, Agent Platform (Vertex), Foundry options. Also the warning, verbatim: "Unless previously approved, Anthropic does not allow third party developers to offer claude.ai login or rate limits for their products, including agents built on the Claude Agent SDK. Use the API key authentication methods described in this document instead." Sources: https://code.claude.com/docs/en/agent-sdk/overview.md ("Get started" note) and https://code.claude.com/docs/en/agent-sdk/quickstart.md ("Set your API key" and the same note).

**Billing:** The SDK docs direct API-key authentication, so API billing. The docs do not state a subscription-billed SDK mode. Legal page: "Advertised usage limits for Pro, Max, and Ultra plans assume ordinary, individual usage of Claude Code and the Agent SDK." Source: https://code.claude.com/docs/en/legal-and-compliance.md.

**Driving subscription auth for personal use:** the legal page says "Nor does it prevent an end user from signing in to the unmodified Claude Code binary with their own Claude subscription", but this is not an explicit statement about personal scripts using the SDK. See Terms section below.

**Note on CLI-as-subprocess:** "To drive the same agent loop from a language other than Python or TypeScript, run the CLI as a subprocess with the `-p` flag and `--output-format json`." Source: agent-sdk/overview.md. Same terms restrictions apply, and `-p` runs on the local machine, not in the cloud.

**URLs:** https://code.claude.com/docs/en/agent-sdk/overview.md; https://code.claude.com/docs/en/agent-sdk/quickstart.md; https://code.claude.com/docs/en/headless.md.

---

## Route 4: Claude Managed Agents

**Exists?** Yes, beta. Header `managed-agents-2026-04-01`. Source: https://platform.claude.com/docs/en/managed-agents/overview.md.

**What it is:** "Pre-built, configurable agent harness that runs in managed infrastructure." Built-in tools: Bash, file operations, web search and fetch, MCP servers. The docs do NOT say it runs the Claude Code binary, the Claude Code CLI, or CLAUDE.md semantics. Treat it as a separate Anthropic harness (UNVERIFIED whether it equals Claude Code's cloud sessions; not the same product as claude.ai/code sessions).

**Environment:** Anthropic-managed cloud sandbox or self-hosted sandbox on your own infrastructure (https://platform.claude.com/docs/en/managed-agents/self-hosted-sandboxes; not read).

**Driveable by a program?** Yes, full REST API (`https://api.anthropic.com/v1/...`) plus SDKs and `ant` CLI. Operations (verified):
- Create agent once: `POST /v1/agents`; create environment: `POST /v1/environments`.
- Create session: `POST /v1/sessions` with `agent`, `environment_id`, optional `initial_events` (up to 50, starts running at once), optional `budget` (`max_list_cost` in cents as string, stops with `budget_reached`), optional `vault_ids`, optional `agent_with_overrides` (model, system prompt, tools).
- Resources (repo mount): `GET /v1/sessions/{id}/resources` shows `github_repository` resources with `url` and `checkout: {type: "branch", name}` or `{type: "commit", sha}`; `POST .../resources/{id}` rotates `authorization_token`. The creation path for a github_repository resource is NOT confirmed (the add-resource endpoint body documents only `file_id`). Source: https://platform.claude.com/docs/en/api/beta/sessions/resources.md.
- Send message: `POST /v1/sessions/{id}/events` with `{"events":[{"type":"user.message","content":[...]}]}`.
- Read transcript: `GET /v1/sessions/{id}/events` (list, paginated; api doc at https://platform.claude.com/docs/en/api/beta/sessions/events/list.md).
- Stream: SSE (path `/v1/sessions/{id}/events/stream` inferred from the endpoint name, UNVERIFIED; guide https://platform.claude.com/docs/en/managed-agents/events-and-streaming.md; not read in full).
- Status: `GET /v1/sessions/{id}`. Statuses: `idle`, `running`, `rescheduling`, `terminated`.
- Stop: send a `user.interrupt` event (only when running, per session-operations doc). No separate "stop" endpoint seen.
- Archive: `POST /v1/sessions/{id}/archive` (requires session idle). Delete: `DELETE /v1/sessions/{id}` (permanent, removes events and sandbox; requires idle).
- List sessions: `GET /v1/sessions` with `agent_id`, `limit`, `page` cursors.

Sources: https://platform.claude.com/docs/en/managed-agents/sessions.md; https://platform.claude.com/docs/en/managed-agents/session-operations.md; https://platform.claude.com/docs/en/api/beta/sessions/resources.md.

**Auth:** Claude Console API key via `x-api-key` header, plus `anthropic-version` and `anthropic-beta: managed-agents-2026-04-01`. "A Claude API key from the Claude Console." claude.ai subscription login not accepted. Source: overview.md ("Beta access").

**Billing:** API, not subscription. "Claude Managed Agents is billed on two dimensions: tokens and session runtime." Tokens at standard model rates. Session runtime: $0.08 USD per session-hour, accruing only while status is `running` (not idle). Source: https://platform.claude.com/docs/en/about-claude/pricing.md ("Claude Managed Agents pricing"). Batch discount does not apply.

**Data:** not ZDR- or HIPAA-eligible; transcripts persist until deleted. Source: overview.md ("Beta access").

**Multi-user:** no statement found on per-end-user accounts in the pages read (UNVERIFIED). Lead only: beta headers `user-profiles-2026-03-24`, `user-profiles-2026-09-04`, and `ce-user-management-2026-07-13` appear in the API header list; docs not read. Workspace selection is by the `anthropic-workspace-id` header (documented); whether sessions are isolated per end user is not stated.

**URLs:**
- https://platform.claude.com/docs/en/managed-agents/overview.md
- https://platform.claude.com/docs/en/managed-agents/sessions.md
- https://platform.claude.com/docs/en/managed-agents/session-operations.md
- https://platform.claude.com/docs/en/managed-agents/events-and-streaming.md (not read in full)
- https://platform.claude.com/docs/en/api/beta/sessions/resources.md
- https://platform.claude.com/docs/en/api/beta/sessions/events/list.md (listed, not read)
- https://platform.claude.com/docs/en/about-claude/pricing.md

---

## Route 5: GitHub Actions (claude-code-action)

**Exists?** Yes. https://github.com/anthropics/claude-code-action (GitHub Action, `anthropics/claude-code-action@v1`). Docs: https://code.claude.com/docs/en/github-actions.md.

**Runs where:** GitHub-hosted runners (consume GitHub Actions minutes). Not Anthropic's cloud sessions. Source: github-actions.md ("Manage costs").

**Auth:** two secrets. `ANTHROPIC_API_KEY` (API billing) or `CLAUDE_CODE_OAUTH_TOKEN` generated by `claude setup-token` "authenticates with your Claude subscription, available on Pro, Max, Ultra, Team, and Enterprise plans." Source: github-actions.md ("Manual setup", step 2). Billing statement: "If you authenticate with an OAuth token, runs use your Claude subscription instead of API billing." Source: github-actions.md ("Manage costs"). Note: "an OAuth token is tied to the subscription of the person who ran `claude setup-token`" and API key is recommended for a shared repository secret. Source: github-actions.md ("Set up for an organization").

**Driveable by a program?** Indirectly. Any GitHub event can trigger it, including `schedule` and `workflow_dispatch`-style triggers via GitHub's API. The docs say "You can also give the Claude Code GitHub Action a prompt to run automatically on any GitHub event." A program would trigger via GitHub's API (not an Anthropic API). Specific `workflow_dispatch` example not in the page read (UNVERIFIED for that trigger type specifically, though GitHub-standard).

**Capabilities:** Start with a prompt (automation mode when `prompt` input given), or `@claude` mentions (interactive mode). Output: "By default, results appear in the workflow run log rather than a comment." Can post comments if the prompt directs it. Repo/branch: the workflow's checkout. Follow-up: a new workflow run, or an `@claude` comment. Status: GitHub Actions run status. Stop: GitHub run cancel (GitHub-side, not documented in Anthropic docs). Transcript: run log.

**Limit:** the Action runs as the Claude GitHub App; "Who can trigger runs" write-access check applies; bot actor rejected unless listed.

**URLs:** https://code.claude.com/docs/en/github-actions.md; https://code.claude.com/docs/en/github-actions-cloud-providers.md (not read).

---

## Route 6: Multi-user (one server, several users' accounts)

- Claude Code on the web and CLI cloud sessions: authenticated as one claude.ai account per machine (`claude auth login`). A server running sessions for several users would need each user's login. Docs prohibit third-party developers from collecting, storing, or intermediating Claude.ai credentials or routing requests through subscription credentials on behalf of their users. See Terms section.
- Scheduled tasks (routines): "belong to your individual claude.ai account. They are not shared with teammates." One token per routine. Multi-user means one routine per user, each with its own token, created under each user's account. No documented admin-level API to create routines for others.
- Self-hosted environments: runner is locked to the first session's owner (user account); "a runner serves one owner at a time". Sessions are owned per user. Team/Enterprise only.
- Remote Control: "Auto-connect ... grants no one else access."
- Managed Agents: Console API key, workspace-scoped. Multi-user isolation or per-end-user accounting is not documented in pages read (UNVERIFIED). Billing is the operator's API bill.
- Claude Tag (Slack) runs cloud sessions for a team under an organisation-managed agent: https://claude.com/docs/claude-tag/overview. Not checked; it is an org-level product, not a route for a personal server.
- Compliance API: admin-level session listing and transcripts for organisations (https://platform.claude.com/docs/en/api/compliance/apps/sessions/remote/list.md). Not checked beyond title.

---

## Terms: may a third-party tool use a subscription OAuth login to drive Claude Code programmatically?

Source: https://code.claude.com/docs/en/legal-and-compliance.md ("Authentication and credential use", "Can customers offer Claude Code in their products?"), plus agent-sdk/overview.md and agent-sdk/quickstart.md notes.

Quoted, verbatim from the legal page:
- "OAuth authentication is intended exclusively for purchasers of Claude Free, Pro, Max, Ultra, Team, and Enterprise subscription plans and is designed to support ordinary use of Claude Code and other native Anthropic applications."
- "Developers building products or services that interact with Claude's capabilities, including those using the Agent SDK, should use API key authentication through Claude Console or a supported cloud provider. Anthropic does not permit third-party developers to offer Claude.ai login into their own applications, or to route requests through Free, Pro, Max, or Ultra plan credentials on behalf of their users. Moreover, developers may not collect, store, or intermediate Claude.ai credentials or session tokens, sign-in to a Claude account must complete through Anthropic's own flow."
- "Nor does it prevent an end user from signing in to the unmodified Claude Code binary with their own Claude subscription, including where a platform hosts Claude Code as described under..."
- "Customers may not pay for, resell, or intermediate Claude usage on their end users' behalf."
- "Claude Code must be installed and run as published by Anthropic" (binary must not be modified).
- "Advertised usage limits for Pro, Max, and Ultra plans assume ordinary, individual usage of Claude Code and the Agent SDK."
- "Anthropic reserves the right to take measures to enforce these restrictions and may do so without prior notice."

Assessment (not a legal opinion):
- Clearly prohibited: a product or service that lets other people's requests run on the operator's subscription login; storing or relaying users' claude.ai tokens; using the Agent SDK in a product with claude.ai login.
- Ambiguous and NOT addressed explicitly: one person scripting their own unmodified `claude` CLI (`claude -p`, `--cloud`) from their own server with their own subscription login. The docs' "end user ... own subscription" clause and the "ordinary, individual usage" assumption point towards single-user personal use being tolerated, but no doc says so for programmatic drivers. Verify with Anthropic (contact-sales link on the legal page) before relying on it.
- Documented and sanctioned for subscription auth without a browser: `claude setup-token` (one-year, inference-only, `CLAUDE_CODE_OAUTH_TOKEN`), used by claude-code-action (route 5). It cannot start or steer cloud sessions, nor run Remote Control. Source: authentication.md ("Generate a long-lived token").
- Documented and sanctioned for start-only subscription automation: routine fire tokens (route 2), purpose-built for "alerting systems, CI pipelines, and internal tools".
- Cloud session control with a headless server: the testing page says the cloud-session scope "is capped server-side at 30 days" and the CLI refresh grant "capped at 30 days from the initial login", so a server must be re-logged-in every 30 days. Source: self-hosted-environments-testing.md ("Authenticate from CI").

---

## Coordinator follow-up answers (a), (b), (c)

(a) `claude --cloud` non-interactive: Partly. Follow-up send works with `-p --cloud <id> --output-format json`. Starting a new hosted session with `-p` plus a description is rejected ("rejects `--cloud` with a task description"). The only documented non-interactive start is `-p "<prompt>" --environment <ccpool_id> --output-format json`, which needs a self-hosted environment. No `stream-json`. No documented way to read output or status except the Stop-hook workaround on the runner. Sources: headless.md; self-hosted-environments-testing.md; claude-code-on-the-web.md.

(b) Self-hosted environments (`ccpool_`): an environment is a named group of runners, created on claude.ai (or by an Owner-token API call), with an environment key passed to `claude self-hosted-runner --environment-secret-file ... --base-dir ...`. Runners poll outbound and execute sessions on the user's host; model inference still goes to api.anthropic.com. Lets cloud sessions run on your own server, but Team/Enterprise only (public beta, Owner-enabled), so not available on Max. Sources: self-hosted-environments.md; quickstart; testing.

(c) Remote Control: no. It exposes the user's local `claude` to claude.ai/mobile clients, with `--capacity` and `--spawn` options. No documented API for a third-party program to spawn or steer sessions. Requires full claude.ai login (not `setup-token`, not API key). Source: remote-control.md; authentication.md.

---

## Not found / could not confirm

- Public REST API for claude.ai/code cloud sessions (start, read, status, stop): not found in code.claude.com or claude.ai docs read.
- Transcript read or session status via routine token: not found (token has "no read access").
- Stop API for routines or claude.ai cloud sessions: not found.
- Non-interactive hosted (Anthropic-cloud, not self-hosted) start via `claude -p`: not documented; explicitly rejected with a description.
- Whether Managed Agents runs the Claude Code binary: not stated; UNVERIFIED.
- Managed Agents: multi-user / per-end-user isolation: not found in pages read.
- Managed Agents: github_repository resource creation call: not confirmed (only read/rotate endpoints seen).
- Remote Control: explicit billing sentence: not seen.
- Self-hosted environment for Max plan: not offered per plan statements; no explicit "Max not eligible" sentence seen.
- Whether a personal, single-user, server-run `claude -p` with own subscription login is permitted: not addressed explicitly.
- Compliance API access requirements: UNVERIFIED.
- Local CLI flags from the coordinator's `claude --help` (2.1.312: `--cloud [description|session_id|url]`, `--environment`, `--bg`, `--from-pr`, `claude remote-control`): consistent with docs for `--cloud`, `--environment`, `--bg` (rejected under -p), `remote-control`; `--from-pr` not checked.

## Doc URLs read (all under the given domains)
- https://code.claude.com/docs/en/claude-code-on-the-web.md
- https://code.claude.com/docs/en/web-quickstart.md (listed only)
- https://code.claude.com/docs/en/routines.md (scheduled tasks page)
- https://platform.claude.com/docs/en/api/claude-code/routines-fire.md
- https://code.claude.com/docs/en/remote-control.md
- https://code.claude.com/docs/en/self-hosted-environments.md
- https://code.claude.com/docs/en/self-hosted-environments-quickstart.md
- https://code.claude.com/docs/en/self-hosted-environments-testing.md
- https://code.claude.com/docs/en/agent-sdk/overview.md
- https://code.claude.com/docs/en/agent-sdk/quickstart.md
- https://code.claude.com/docs/en/headless.md
- https://code.claude.com/docs/en/legal-and-compliance.md
- https://code.claude.com/docs/en/authentication.md
- https://code.claude.com/docs/en/github-actions.md
- https://platform.claude.com/docs/en/managed-agents/overview.md
- https://platform.claude.com/docs/en/managed-agents/sessions.md
- https://platform.claude.com/docs/en/managed-agents/session-operations.md
- https://platform.claude.com/docs/en/api/beta/sessions/resources.md
- https://platform.claude.com/docs/en/about-claude/pricing.md

## Probes run 2026-11-02 00:06 to 00:10 (Claude Code 2.1.312, Max, claude.ai login)

- Desktop app tool `start_session` with `target: "cloud"`: refused while the author is on Remote Control ("you can start a session only on a message typed in the desktop app").
- `claude --cloud "<task>"` in a tmux pane (TTY): one-time workspace trust prompt for a new folder, then printed `Created cloud session: <title>`, `View: https://claude.ai/code/session_01L2Rtd6Rz3g2coZUrJdwnAE?...`, `Resume with: claude --teleport <id>`, and exited 0 within 6 s. No TUI interaction needed beyond trust.
- Same without a TTY (`</dev/null`, piped stdout): `Error: --cloud requires an interactive terminal.` exit 1. So a pseudo-terminal (tmux, `script`) is required.
- `claude -p "<msg>" --cloud <id> --output-format json`: `{"ok":true,"session_id":...,"url":...}` exit 0; the session answered it.
- `claude --teleport <id>` in a clean clone (tmux): showed the whole conversation (both replies), branch checkout failed because the session pushed nothing. No local `.jsonl` transcript was written (searched ~/.claude/projects).
- In the teleported TUI, `/export probe-export.txt` wrote the rendered conversation (prompts, replies, tool summaries) as text: 1,007 bytes. Rendered text, not structured events.
- Probe session left on claude.ai: session_01L2Rtd6Rz3g2coZUrJdwnAE ("Cloud sessions probe").
