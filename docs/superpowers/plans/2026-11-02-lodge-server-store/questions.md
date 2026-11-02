# Questions for the author: plan 2 of the server build

**STORE-1 · who writes a thread message under your name** (answered: C, d-2v8vtk)

Question: may an agent session write your words into a thread as a message by you, as lodge 0.2 lets it with where and when, or do only you, signed in, write a message under your name?

- A: only you.
  A thread message under your name is always one you wrote; an agent that has your answer from a chat asks you to reply in lodge.
  An agent token that writes `by: <your name>` is refused with nothing written, and so is another person writing under your name.
- B: an agent may relay your words, with where and when, as in lodge 0.2.
  Your chat answer reaches the thread without you, and a message under your name is as trustworthy as the agent that wrote it, which the design stopped accepting for your decisions (SRV-2).

Recommendation: A.
A thread whose last message is yours no longer waits for you (`src/lodge/app/threads.py:139-145`), so a relayed answer moves work on without you, which is what SRV-2 rules out for decisions.

Answered: C, an option the coordinator added in the session (2026-11-02, d-2v8vtk): an agent may relay your words into a thread under your name, with where and when; the message is held, and the thread keeps waiting for you until you approve it signed in; a message you write signed in under your own name is not held, and one person writing under another's name is refused.
The plan applies it in Tasks 11 and 12c, on the hold machinery of Tasks 12a and 12b.
