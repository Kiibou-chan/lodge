---
id: s-5sgcxx
kind: spec
title: "Import checks the original and mapped states"
rests_on: [s-txrm4h]
---

The importer checks the store as a change from an empty state with its own `.lodge.toml`, read at a settings revision that defaults to the records revision.
After mapping, it checks the same change with the project's settings and owners.
It refuses a path that is not UTF-8 and publishes nothing if either check fails.
Attachments preserve their bytes, including bytes that are not UTF-8.
