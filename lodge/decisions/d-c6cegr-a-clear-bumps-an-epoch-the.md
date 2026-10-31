---
id: d-c6cegr
kind: decision
title: "A clear bumps an epoch, the cap counts used pages, and a keep after a clear writes everything it used"
scope: process
decided_by: planner
date: 2026-10-31T23:39:24+01:00
narrows: [d-4j98ph]
work_item: "docs/superpowers/plans/2026-10-31-lodge-at-scale.md"
---

The cap is measured as used pages, `(page_count - freelist_count) × page_size`, so a cleared file under it is not cleared again.
A clear increments `meta.epoch`; a build records the epoch with its cache hits, and a `keep_state` that finds another epoch writes every parse unit and every fact the build used, hits included.
The clear empties ordinary tables with `DELETE` and recreates the FTS table, so no FTS row is deleted by key.

## Reasoning

The coordinator's ruling d-e3stjn of the fourth fix round: after a clear, hits taken before it name units that are gone, so a keep with misses alone would break a state's completeness; the third recheck's R5 asks for facts hits to be carried the same way.
Cost if wrong: one keep after a clear writes a full state.
