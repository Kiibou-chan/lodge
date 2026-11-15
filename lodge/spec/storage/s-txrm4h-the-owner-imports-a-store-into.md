---
id: s-txrm4h
kind: spec
title: "The owner imports a store into an empty project"
rests_on: [s-z1zvb4, s-ava922]
---

The importer reads a lodge 0.2 store at a revision from a git repository on the server's machine.
Only the signed-in owner of a project with one owner may import into it, and the project must be empty.
The importer publishes records as events through that owner's store, preserving IDs, dates, codes, and `imported_from`, and writing no settings.
