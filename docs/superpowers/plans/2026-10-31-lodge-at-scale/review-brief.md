# Brief: review of the plan "lodge at scale"

Review `docs/superpowers/plans/2026-10-31-lodge-at-scale.md` (worktree `/home/kiibou/.cache/lodge-work/read-speed`, branch `read-speed`) against its brief (`brief.md` in this folder), the planner's report and probes (`plan-report.md`, `probes/`), the decisions it recorded (ledger `-progress.md` lists their IDs; read them with `uv run --frozen --quiet lodge show ID --reasoning`), `lodge spec`, and the code under `src/lodge/`.
Your angle is named in your dispatch.
Every finding: Blocking, Important, or Minor; a handle (plan task or section, and the code `file:line` or probe it conflicts with); a concrete failure scenario; the fix.
Verify claims by running them where you can (probes under `/var/tmp/lodge-bench`, native disk; the 160,000-file store `/var/tmp/lodge-bench` holds if the planner built it, else build what you need with `scripts/bench_store.py`), and say where you could not.
Change nothing in the worktree except your output file; scratch work goes under `/var/tmp/lodge-review-<your angle>/`; no network; never run `lodge add`.
Write your output file incrementally; end with the counts and the three most important findings, one line each.
British English, no em-dashes, one sentence per line.
