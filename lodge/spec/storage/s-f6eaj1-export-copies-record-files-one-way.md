---
id: s-f6eaj1
kind: spec
title: "Export copies record files one way to git"
rests_on: [s-z1zvb4]
---

The server writes records as text files to git and commits them, one way only; the database never reads the copy back.
The target is the project's own repository or a separate repository.
The export holds specification entries, areas, decisions, record threads, and attachments in lodge 0.2's file layout, including `lodge/decisions/.gitkeep` and `lodge/spec/.gitkeep`.
Tasks, artefacts, and session reports stay out.
