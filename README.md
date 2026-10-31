# lodge

lodge is a knowledge tool for software built by agents with a human in the loop.
It holds a project's decisions, specification entries, and threads as files in git, and gives agents one defined way to read and write them.
The author of the project browses the same knowledge without a session, in a local web viewer.

## What it holds

- A **decision** records a change and why, with a scope (`product` or `process`), who decided, and the entries it changes, replaces, or narrows.
  A decision is immutable once published, its reasoning included; a correction or a shorter reasoning is a new decision that replaces it.
- A **specification entry** says what holds now, in one paragraph, and belongs to an **area**, a named group with a title, an intro, and the order of its entries.
  Entries are rewritten in place, and each change to one names the decision behind it.
  An entry lists the entries it depends on in `rests_on`.
- A **thread** records a doubt or question about a decision or specification entry, with messages and an open or closed state.
  Published messages are immutable, and replies are appended.
  Open doubts mark records as "in doubt", and open questions as "question open"; doubts also propagate through dependencies.

Decisions and specification entries are read at three levels, so a default read stays short:

1. The statement, status, who decided, the date, and any flag.
2. The reasoning, read only when asked for.
3. The provenance: the author's own words where the author decided, the handle of each number, links both ways, and attachments.

The check runs eight checks before publishing:

1. Records parse, their file names match their IDs, and new decisions have valid dates and import history.
2. Links and attachments resolve, codes are unique, dependencies do not name themselves, and published records remain present.
3. Author decisions have the author's quote, and only author decisions confirm.
4. Specification changes have a decision in the same change, with the appropriate action, and import sources are allowed.
5. Published decisions and thread history remain immutable, messages are only appended, and closed threads stay closed.
6. New links do not narrow or confirm replaced decisions, change retired entries, or add dependencies on retired entries.
7. Each area lists exactly its current entries, once each.
8. Dependencies have no cycles.

A thread can fail checks 1, 2, and 5: malformed content or a mismatched file name, an unresolved target or a missing published thread, or a rewritten history or invalid closure.
Advice, such as a statement over its length guidance, is feedback and never a refusal.

## Install

lodge needs Python 3.12 or later and [uv](https://docs.astral.sh/uv/).
Install it from a tag of this repository:

```sh
uv tool install git+https://github.com/Kiibou-chan/lodge@<tag>
lodge --version
```

## Set up a repository

Run `lodge init` at the root of a git repository.
It creates `lodge/decisions` and `lodge/spec` and stages them.
Threads are stored under `lodge/threads` when first written.
Settings are optional and live in `.lodge.toml` at the same root; see below.

## Reading

```sh
lodge search WORDS          # level-1 blocks, by words, ID, or code
lodge show REF              # level 1; add --reasoning or --provenance
lodge spec                  # areas by rank, entries after their dependencies
lodge threads               # open doubts and questions
lodge thread q-xxxxxx       # one thread and its messages
lodge waiting               # waiting for an agent, then waiting for the author
lodge check                 # every check, against the published state too
```

A REF is an ID such as `d-y8p15p` or a code such as `ITEM-1`.
`search` filters by `--kind`, `--scope`, `--status`, `--area`, and `--by`.
It lists 20 records unless `--limit` says otherwise, and says how many it left out.
The specification puts ranked areas first, by rank and name, then unranked areas by name.
Within each area, entries follow the entries they rest on, using the written order to break ties; `--area NAME` selects one area.
`waiting` has two groups: open threads whose last message is by the author wait for an agent; agent decisions awaiting confirmation and open threads whose last message is by an agent wait for the author.
Read through lodge, never by opening record files.

## Writing

Never edit a record file by hand; decisions, entries, and areas go through `lodge add`, and thread messages use the commands below.
`lodge guide` prints the rules for agents, so a project's `CLAUDE.md` can point at it instead of copying it.

1. `lodge id s` prints a new ID for each new specification entry, so a decision can name it.
2. Write each record as a draft file outside `lodge/`: Markdown with a YAML header, the body being the statement and `## Reasoning` starting the why.
   To edit, start from `lodge draft REF` or `lodge draft area:NAME`.
3. Run `lodge add --dry-run FILE...` first.
   It applies the drafts and runs the checks without publishing, so the feedback can be acted on while the decision can still change.
4. Run `lodge add FILE...` with the decision and every entry it changes together.
   lodge fills in the ID and the date.

An entry declares dependencies with `rests_on: [s-xxxxxx]`.
A decision changing only that list uses `changes: [{entry: s-xxxxxx, action: link}]`.
Other entry changes alongside `link` need another decision in the same add listing the entry with `edit` or `create`.
When an entry still holds after a dependency changes, record an `edit` decision with unchanged entry text and explain why in its reasoning.

A decision draft:

```
---
kind: decision
title: "Keep whole transcripts"
scope: product
decided_by: coordinator
changes: [{entry: s-4kq1zm, action: create}]
---
Transcripts are kept whole.
```

To keep evidence such as a log with a decision, list `attachments: [name]` in the header and run `lodge add --attach FILE DRAFT`.
Give `--attach` once per file; each file must be UTF-8 text, and the add must create exactly one decision.

`decided_by: author` is for the author's decisions only, and needs `quote: {text, where, when}` with the author's words verbatim.
An agent that changes what the author decided or confirmed raises a flag, shown as "awaiting the author", until the author confirms it with a decision that has `confirms: [d-xxxxxx]`.

Threads take message text from a UTF-8 file:

```sh
lodge ask ITEM-1 --kind doubt --by coordinator .drafts/message.txt
lodge ask ITEM-1 --kind question --by coordinator .drafts/message.txt
lodge reply q-xxxxxx --by coordinator .drafts/message.txt
lodge close q-xxxxxx --by coordinator .drafts/closing.txt
lodge reply q-xxxxxx --by author --where "project discussion" --when "2026-10-31 10:00" .drafts/author.txt
```

Use `--by author` only for the author's words verbatim, with `--where` and `--when` recording their source and time.
The CLI requires both options for author messages.
A closing file is optional, and its text may be empty; other messages must contain text.
Message text loses a CR before each LF and surrounding whitespace, preserving everything else.
Answer a doubt with a decision whose reasoning names the thread, then reply naming that decision; agents close threads only when the author asks.
Thread commands stage like `add` in checkout mode, and commit and push in branch mode.

In checkout mode, the default, `add` stages the files in the working tree, and they travel with the commit that implements the change.
In branch mode, `add` commits to a branch of its own and pushes it.
Reads, the viewer, and `lodge check` compare with the published state as well, so an edited published decision shows as failing everywhere.
`lodge check --gate` and `lodge add` are the ones that refuse, and the gate publishes nothing it fails.
In branch mode the gate runs inside `lodge add`, so a push to the branch by hand skips it.
A rewrite of the branch is detected only by a clone that read the branch before the rewrite, normally the author's own, since every fresh clone accepts the tip it first sees.
The exit codes are 0 for done, 1 for a failed check or a store that changed under the command, and 2 for a usage or environment problem.

## The viewer

```sh
lodge view              # http://127.0.0.1:8787/
lodge view --port 9000
```

The local viewer offers search with the same filters as the command line, each record at level 1 with reasoning and provenance one click away, links in both directions, a timeline, and both waiting groups.
The specification offers "As written" and "By dependency" views, and record pages show their dependencies.
The author can enter "Your words" and choose "Confirm" for a decision or the decisions behind an area.
Record pages offer "Raise a doubt" and "Ask a question", and threads offer replies and "Close".
Viewer writes use `author`, `where` `lodge viewer`, and the clock's minute as `when`, in `YYYY-MM-DD HH:MM` format.

Each viewer process mints a fresh token, embedded in forms and required on writes.
Writes also require an allowed `Host` and an `Origin` matching an allowed address over HTTP or HTTPS.
The default allowed addresses are `127.0.0.1:PORT` and `localhost:PORT`.
For a proxy, repeat `--allow-host HOST` to allow additional `name:port` addresses, for example `lodge view --allow-host proxy:443`.
The server still binds to `127.0.0.1`.

In checkout mode, viewer writes stage their files and attempt to commit exactly those paths, using the checkout's git identity and hooks, while leaving other staged work staged.
They remain staged on the configured base branch, with detached HEAD, during a merge, rebase, cherry-pick, or revert, if the index stays locked after a retry, or if git cannot commit.
The page reports the outcome; a commit failure's detail appears in the terminal running the viewer.
In branch mode, writes commit and push to the configured branch.
It uses the same parser and checks as the command line, so it cannot disagree with them.

## The hook

Add the hook to a project's Claude Code settings (`.claude/settings.json`, not the user-level file) so that an agent which edits a record file by hand is told what to use instead.
The feedback is advice, never a block.

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write|MultiEdit",
        "hooks": [{ "type": "command", "command": "lodge hook post-tool-use" }]
      }
    ]
  }
}
```

It fires for a hand edit of a record file under `lodge/` (not `lodge/attachments/`), and of any file matching a `frozen` glob in `.lodge.toml`.
The repository is the one that holds the edited file, so an edit in another worktree counts, and the hook stays silent in a repository where `lodge init` has not been run.
A glob is relative to the repository root, with no leading slash.
`*` and `?` stay within one folder, `**` crosses folders, and square brackets are not special.
In branch mode there is no record file in the working tree, so only the frozen globs apply.
Edits made through `Bash` are not noticed in this version.

## Settings

`.lodge.toml` at the repository root is optional.
Every key has a default, and an unknown key is an error.

```toml
[store]
mode = "checkout"          # "checkout" or "branch"
branch = "lodge"           # branch mode: the branch that holds the records
remote = "origin"          # where the branch is fetched from and pushed to
base = "main"              # checkout mode: the branch `lodge check --gate` compares with
max_staleness_seconds = 60 # branch mode: how old a fetch may be before a read fetches again
commit_trailer = "..."     # branch mode: an optional trailer added to each commit message

[length]                   # guidance; feedback above it, never a refusal
title_chars = 100
decision_statement_words = 80
spec_statement_words = 150
reasoning_words = 1000

[import]
sources = ["docs/choices.md"]   # files that an imported record may name in `imported_from`

[hook]
frozen = ["docs/choices.md", "docs/verdicts.md"]
```

## Development

```sh
uv sync
sh scripts/check.sh   # format, lint, types, unused code, tests, and lodge's own check
```

The code is in `src/lodge`, in packages with one front door each: `core` (pure), `app`, `gitstore`, `cli`, `viewer`, and `hook`, wired together in `main.py`.
A structure test, run with the others, enforces the allowed imports, no cycles, and a module size limit.
lodge keeps its own decisions in this repository, in `lodge/`.

No licence has been chosen yet.
