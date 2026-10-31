---
id: s-q42qd7
kind: spec
title: "Viewer writes require a startup token"
---

Every viewer write is a `POST` carrying a token minted when the viewer starts and embedded in its pages.
A request without the token is refused, and token comparison takes constant time.
