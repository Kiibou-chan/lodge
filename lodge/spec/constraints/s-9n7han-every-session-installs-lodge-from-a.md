---
id: s-9n7han
kind: spec
title: "Every session installs lodge from a tag of its public repository"
---

Every session that needs lodge, cloud children included, installs it from a tag of its public repository with `uv tool install git+https://github.com/Kiibou-chan/lodge@<tag>` (LODGE-4).
No credential, setup script, or second attached repository is needed.
Attaching lodge as a session repository would not reach the child sessions that the first user's coordinator starts, because each of them gets one repository.
