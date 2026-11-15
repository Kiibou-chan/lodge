# Questions for the author: plan 4 of the server build

**IMP-1 · who the export names in `decided_by`** (answered: A, d-b61590)

Question: when the export writes a decision you made, or a thread message of yours, does it name you as a person, or write `author` as lodge 0.2 does?

- A: it names you as a person, as the design says (line 78, "the export writes the person").
  A project with several people keeps who decided in the export.
  lodge 0.2 reading the export renders the same `lodge spec`, but its `lodge check` fails check 3 on every confirmation you made, and `lodge show` no longer says a decision was confirmed by you (probe 3).
  A thread holding a message of yours becomes unreadable to lodge 0.2, which reads `by: <your name>` as an agent's message whose `when` must be a full time stamp (probe 7).
- B: it writes `author` for the project's owner, in `decided_by` and in a thread message's `by`, and names any other person.
  For a project with one person the export is then a lodge 0.2 store byte for byte, which `lodge check` passes, and a store survives import and export unchanged.
  With several people, the other people's confirmations fail lodge 0.2's check as under A.

Recommendation: B.
The design also asks that the export read like a lodge 0.2 store (line 284), and under A a project's own `lodge check --gate` on its exported copy fails from the first confirmation.
The person can be named in the export later, when a project has a second person, without touching any record on the server.

Answered 2026-11-02: A, "it's okay if lodge 0.2 can't read this... no one needs the backwards compat" (author decision d-b61590).
The plan follows A with no lodge 0.2 compatibility: the export keeps lodge 0.2's file layout, and lodge 0.2's check, `lodge spec`, and `lodge waiting` need not read it cleanly (probe 7).
