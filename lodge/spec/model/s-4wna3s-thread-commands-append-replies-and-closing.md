---
id: s-4wna3s
kind: spec
title: "Thread commands append replies and closing messages"
---

`lodge ask REF --kind doubt|question --by ROLE FILE` opens a thread, `lodge reply q-xxxxxx --by ROLE FILE` appends a message, and `lodge close q-xxxxxx --by ROLE` closes it.
Closing appends a message by the closer; without text, its text is empty and reads show "closed by" its writer, never invented words.
