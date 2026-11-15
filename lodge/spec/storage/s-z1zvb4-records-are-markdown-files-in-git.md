---
id: s-z1zvb4
kind: spec
title: "Records live in git files or server events"
---

lodge 0.2 keeps records as Markdown files with YAML headers in git, one record per file, behind a storage interface.
On the server, records live as events in one append-only SQLite table.
Each event that writes a record holds its path and file bytes; other tables are derived from events and can be rebuilt.
