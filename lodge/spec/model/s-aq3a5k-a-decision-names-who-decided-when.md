---
id: s-aq3a5k
kind: spec
title: "A decision names who decided, when, and the work item"
---

A decision carries `decided_by`, which is `author` or the agent role that decided, such as `coordinator` or `advisor`, and a `date` in local time.
A process decision also carries `work_item`, the work item it rules on, as a plan path or a request id.
`quote` holds the author's words with where and when they were said, and is required when `decided_by` is `author`.
