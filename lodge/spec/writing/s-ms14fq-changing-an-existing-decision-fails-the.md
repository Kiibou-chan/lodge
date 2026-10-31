---
id: s-ms14fq
kind: spec
title: "Check 5: changing an existing decision fails"
rests_on: [s-j70a0k]
---

An existing decision whose statement, quote, `decided_by`, links, or reasoning has changed fails the check, because decisions are immutable.
A correction, or a shorter reasoning, is a new decision that replaces the old one (LODGE-10).
