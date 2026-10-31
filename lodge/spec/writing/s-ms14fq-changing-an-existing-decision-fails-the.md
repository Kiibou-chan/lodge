---
id: s-ms14fq
kind: spec
title: "Check 5: changing an existing decision fails"
rests_on: [s-j70a0k]
---

An existing decision whose statement, quote, `decided_by`, links, or reasoning has changed fails the check, because decisions are immutable.
A correction, or a shorter reasoning, is a new decision that replaces the old one (LODGE-10).
Check 5 also refuses changes to a thread's published messages, `about`, or kind, and permits its state only to move from `open` to `closed`, with an appended closing message.
