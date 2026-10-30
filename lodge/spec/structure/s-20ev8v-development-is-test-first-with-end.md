---
id: s-20ev8v
kind: spec
title: "Development is test-first, with end-to-end tests per command"
---

Development is test-first, with pytest.
`core` is tested alone and fast, with no temporary files.
Each command has one end-to-end test against a temporary git repository with a bare remote, so pushing and a rejected push are exercised.
