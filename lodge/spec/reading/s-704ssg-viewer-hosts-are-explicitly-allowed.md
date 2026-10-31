---
id: s-704ssg
kind: spec
title: "Viewer hosts are explicitly allowed"
---

The viewer accepts the whole `Host` header only when it matches `127.0.0.1:PORT`, `localhost:PORT`, or a value supplied with repeatable `lodge view --allow-host HOST`.
A reverse proxy on another port is configured as `name:port`.
No machine name appears in code or committed settings.
