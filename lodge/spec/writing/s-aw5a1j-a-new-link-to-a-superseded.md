---
id: s-aw5a1j
kind: spec
title: "Check 6: a new link to a superseded record fails"
rests_on: [s-j70a0k]
---

A record added in this change that links to a replaced decision or a retired entry fails the check, unless the link is through `replaces`, or through `changes` with `retire`.
Older records keep their links, and reads show each target's status beside them.
Check 6 also refuses an entry edited in this change that newly rests on a retired entry.
