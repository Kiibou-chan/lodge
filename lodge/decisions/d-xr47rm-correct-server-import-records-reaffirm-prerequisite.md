---
id: d-xr47rm
kind: decision
title: "Correct server import records: reaffirm prerequisite group 1"
scope: product
decided_by: coordinator
date: 2026-11-15T06:03:58+01:00
changes:
  - {entry: s-wb086g, action: edit}
  - {entry: s-w46592, action: edit}
  - {entry: s-7pfk9d, action: edit}
  - {entry: s-y019g9, action: edit}
  - {entry: s-fns8m3, action: edit}
  - {entry: s-5sgcxx, action: edit}
  - {entry: s-chdc8y, action: edit}
  - {entry: s-cssfnb, action: edit}
  - {entry: s-yaz279, action: edit}
  - {entry: s-yv40f3, action: edit}
work_item: "docs/superpowers/plans/2026-11-02-lodge-server-import.md"
numbers:
  - {value: "3", handle: "docs/superpowers/specs/2026-11-02-lodge-server-design.md:298, build order item 3; docs/superpowers/specs/2026-11-02-lodge-server-design.md:304 for sign-in steps 1 and 7"}
---

The listed claims still hold because their specific prerequisites remain supplied after the correction and splits.

## Reasoning

These reaffirmations accompany the Task 11c review correction in the same add, retaining each unchanged claim.
The prerequisite sources below explain why it still holds.
s-wb086g (Only the deciding person clears their review flag) needs A decision names its deciding person or agent role, still supplied by s-ava922: On the server, `decided_by` names a person or an agent role.
s-w46592 (The browser receives live updates through server-sent events) needs The browser app uses the agents' API, still supplied by s-ksg593: From build step 3, the browser app uses the same API as the agents; The server build follows seven ordered steps, still supplied by s-pks1qn: step 3 retains interface views.
s-7pfk9d (An artefact view includes versions and its thread) needs Artefact uploads are versioned task attachments, still supplied by s-cf0qph: From build step 2, an artefact is a file a session or person attaches to a task, such as a mock, report, review, or brief; Each artefact has its own thread, still supplied by s-xakcm0: From build step 2, an artefact has its own thread, keeping mock discussion apart from coordination; The browser app uses the agents' API, still supplied by s-ksg593: From build step 3, the browser app uses the same API as the agents; The server build follows seven ordered steps, still supplied by s-pks1qn: step 3 retains interface views.
s-y019g9 (The browser carries forward the viewer's record pages) needs The browser app uses the agents' API, still supplied by s-ksg593: From build step 3, the browser app uses the same API as the agents; The server build follows seven ordered steps, still supplied by s-pks1qn: step 3 retains interface views.
s-fns8m3 (The browser provides a project workflow view) needs A workflow defines a project task's steps, still supplied by s-tprwhs: From build step 5, a workflow defines the steps a task goes through in its project; The browser app uses the agents' API, still supplied by s-ksg593: From build step 3, the browser app uses the same API as the agents.
s-5sgcxx (Import checks the source state with source settings) needs The owner imports a store into an empty project, still supplied by s-txrm4h: The importer reads a lodge 0.2 store at a revision from a git repository on the server's machine.
s-chdc8y (Import checks the mapped state with project settings) needs The owner imports a store into an empty project, still supplied by s-txrm4h: The importer reads a lodge 0.2 store at a revision from a git repository on the server's machine; Import checks the source state with source settings, still supplied by s-5sgcxx: The importer checks the store as a change from an empty state with its own `.lodge.toml`, read at a settings revision that defaults to the records revision.
s-cssfnb (A failed source or mapped check publishes nothing) needs The owner imports a store into an empty project, still supplied by s-txrm4h: The importer reads a lodge 0.2 store at a revision from a git repository on the server's machine; Import checks the source state with source settings, still supplied by s-5sgcxx: The importer checks the store as a change from an empty state with its own `.lodge.toml`, read at a settings revision that defaults to the records revision; Import checks the mapped state with project settings, still supplied by s-chdc8y: After mapping, the importer checks the same change from an empty state with the project's settings and owners.
s-yaz279 (Import changes only author attribution) needs The owner imports a store into an empty project, still supplied by s-txrm4h: The importer reads a lodge 0.2 store at a revision from a git repository on the server's machine.
s-yv40f3 (Import refuses paths that are not UTF-8) needs The owner imports a store into an empty project, still supplied by s-txrm4h: The importer reads a lodge 0.2 store at a revision from a git repository on the server's machine.
No other related decision is narrowed or replaced; these unchanged claims retain their specific prerequisites, and the main corrective decision names the section corrections.
