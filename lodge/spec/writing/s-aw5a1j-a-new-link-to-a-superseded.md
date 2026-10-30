---
id: s-aw5a1j
kind: spec
title: "A new link to a superseded record fails the check"
---

A record added in this change that links to a replaced decision or a retired entry fails the check, unless the link is through `replaces`, or through `changes` with `retire`.
Older records keep their links, and reads show each target's status beside them.
