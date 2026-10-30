---
id: s-qkcp0s
kind: spec
title: "A cloud session can install lodge from the public tag"
---

A cloud session image has Python 3.13 and uv, api.github.com and pypi.org answer, and git traffic goes through a session proxy scoped to the repositories the session holds.
The proxy still lets a fresh session that holds only the first user's project install lodge from the public tag, so the fallbacks of publishing lodge to PyPI or of attaching lodge to each child session are not needed.
