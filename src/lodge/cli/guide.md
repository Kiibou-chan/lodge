# lodge: the guide for agents

lodge holds a project's decisions and specification entries.
A decision records a change and why, with a scope, who decided, and the entries it changes.
An entry says what holds now, in one paragraph, and belongs to an area.
An area is a named group with a title, an intro, and the order of its entries.
Read through lodge, never by opening record files.

## Reading

`lodge search WORDS`, `lodge show REF`, `lodge spec [--area A]`, and `lodge waiting` read.
A REF is an ID or a code such as ITEM-1.
`show` gives level 1: the statement, status, who decided, the date, and flags.
`--reasoning` adds level 2, the why; for an entry it lists the decisions that changed it, so show one of them with `--reasoning` for its why.
`--provenance` adds level 3: the author's quote, numbers, work item, attachments, and links both ways; ask for levels 2 and 3 only when the task needs them.
"awaiting the author" means an agent changed something the author decided or confirmed, so do not treat it as settled.
A `problem:` line names a file lodge cannot read, and a record flagged `fails check` fails a check, such as a published decision edited by hand; tell the author.
A line saying the lodge branch was rewritten is for the author too; only the author accepts it, with the git command it names.

## Writing

Never edit record files by hand.
1. `lodge id s` gives the ID of each new entry, so the decision can name it.
2. Write drafts, Markdown with a YAML header, outside `lodge/`; the body is the statement, and `## Reasoning` starts the why.
3. To edit, start from `lodge draft REF` or `lodge draft area:NAME`, whose `base:` lodge checks.
4. Run `lodge add --dry-run FILE...` first: feedback can only be acted on before publishing, since a published decision is immutable.
5. Run `lodge add FILE...` with the decision and every entry it changes together; lodge fills `id` and `date`.
In checkout mode `add` stages the files, so commit them with your work; in branch mode it publishes them.
The gate on a branch runs inside `lodge add`, so a push to the branch by hand skips it.
A dry run marks new IDs `(provisional)`: the real add mints new ones, so never write them into another draft.

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

An entry draft has `kind: spec`, `id`, `area`, and `title`; an area draft has `kind: area`, `name`, `title`, and `order`.
A new entry needs its area, and a new area needs an area draft in the same add.
Actions in `changes` are `create`, `edit`, and `retire`.
A correction, or a shorter reasoning, is a new decision with `replaces: [d-xxxxxx]` or `narrows: [d-xxxxxx]`, never an edit.
A number in a statement needs `numbers: [{value: "40 %", handle: "a command, or a record and key"}]`.
To keep evidence such as a log, list `attachments: [<name>]` in the one new decision and run `lodge add --attach PATH FILE...`.
lodge stores each text file at `lodge/attachments/<decision id>/<name>`, the name being the file's own, so `--attach ../out/runs.log` is `attachments: [runs.log]`; repeat `--attach` for more.
lodge dates a new decision at this machine's clock and waits up to three seconds for the newest decision's second to pass; a decision dated further ahead is not waited for and a change related to it fails check 1; tell the author.
`feedback:` and `note:` lines are advice; `check` lines are a gate, and nothing is published until they are gone.

## Quoting the author

`decided_by: author` is for the author's decisions only, with `quote: {text, where, when}`.
The text is the author's words verbatim, with where and when they were said; never paraphrase.
Without their words it is not the author's decision, so record it under your own role; a role that contains the word author is refused.
The author's confirmation of an agent decision is an author decision with `confirms: [d-xxxxxx]`.

Exit codes: 0 done, 1 check failed or the store changed under you (add again), 2 usage or environment.
