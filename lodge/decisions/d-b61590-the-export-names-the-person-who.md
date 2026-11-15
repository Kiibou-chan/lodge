---
id: d-b61590
kind: decision
title: "The export names the person who decided, with no compatibility with lodge 0.2"
scope: product
decided_by: author
date: 2026-11-02T19:33:21+01:00
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
quote: {text: "it's okay if lodge 0.2 can't read this... no one needs the backwards compat", where: "lodge build session", when: "2026-11-02T19:32:42+01:00"}
numbers:
  - {value: "0.2", handle: "pyproject.toml, version"}
  - {value: "1", handle: "docs/superpowers/plans/2026-11-02-lodge-server-import/questions.md, IMP-1"}
---

The export writes the person who made a decision or a thread message by name, as the design says, and need not stay readable by lodge 0.2.

## Reasoning

Asked as IMP-1 (`docs/superpowers/plans/2026-11-02-lodge-server-import/questions.md`): option A, the person by name, against option B, `author` for the project's owner so that lodge 0.2 reads the export.
The author answered that no one needs the export to stay readable by lodge 0.2.
