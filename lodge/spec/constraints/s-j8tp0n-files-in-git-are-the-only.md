---
id: s-j8tp0n
kind: spec
title: "The active store is the source of truth"
---

For a project on lodge 0.2, files in its git repository are the source of truth, and any index is disposable.
For a project on the server, its events are the source of truth, and derived tables can be rebuilt.
The export to git is a one-way copy that the database never reads back.
