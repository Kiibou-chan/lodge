# Task 6b review: the viewer's write gate

Reviewed: commit 73af006 against 978fdfd (`git diff 978fdfd 73af006 -- src tests`), in a detached scratch worktree of 73af006, from the security angle first, then correctness against `task-6b-brief.md`, then practice.
Requirements read: `task-6b-brief.md`, `task-6b-report.md`, the Security, Must nots, Confirming, and Doubts sections of `docs/superpowers/specs/2026-10-31-lodge-viewer-interaction-design.md`, and d-7w5aq0 and d-a3h9f3 (`uv run --frozen --quiet lodge show ID --reasoning`).
Status: in progress; sections are filled as each pass finishes.

## Verification run

- `uv run --frozen --quiet pytest tests/viewer tests/e2e/test_view.py tests/test_structure.py -q` in the scratch worktree, sockets allowed: `120 passed`.
