---
id: s-7m3smc
kind: spec
title: "Auto mode needs the install authorised"
---

Auto mode blocks the install as code from outside until the author authorises it in that session.
An authorisation in the spawning session's prompt is enough: a fresh child session with no human message before it installed lodge and ran it.
Whether an instruction in the repository's `CLAUDE.md` or a settings allow rule can authorise the install has not been tested.
