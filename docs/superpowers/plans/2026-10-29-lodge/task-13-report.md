# Task 13 report: dogfooding and the public README

Status: DONE (no tag, as the ledger ruling says).

## Records added (all `decided_by: author`, through `lodge add` only, each after `--dry-run`)

ID · code · scope · title (21 records, all current)

- `d-49rmkb` · LODGE-1 · product · Where the data lives: records on their own branch
- `d-qsfjqa` · LODGE-2 · product · Decisions labelled as the author's are trusted
- `d-7m3rc1` · LODGE-3 · process · The repository is private on GitHub
- `d-y8p15p` · LODGE-4 · process · The repository is public, installed from a tag
- `d-ar0ker` · LODGE-5 · process · Input and output outside the git store
- `d-8nkamy` · LODGE-6 · product · An agent changing what the author confirmed is flagged
- `d-wc6bah` · LODGE-7 · product · Replacing an agent's change to an author's entry
- `d-gcz871` · - · product · The author browses lodge through a local web viewer
- `d-n30kqr` · - · product · Knowledge is read at three levels
- `d-vzvfg2` · - · product · lodge replaces the files that hold project knowledge
- `d-rkcb17` · - · product · lodge starts serverless, with storage behind one interface
- `d-dd17rs` · - · product · lodge has its own repository and the knowledge stays in the project it is about
- `d-7v4crf` · - · process · lodge is written in Python
- `d-y19d7r` · - · process · lodge keeps its own decisions in lodge
- `d-txv0mv` · - · product · The specification is a central part of lodge
- `d-pf8xm9` · - · product · Provenance is kept in the repository, not in transcripts
- `d-c6n1ng` · - · product · Guardrails are feedback, a check before merge, and quoted author decisions
- `d-yfkgx3` · - · product · The tool is named lodge
- `d-vxfdz7` · - · process · Engineering principles are enforced from the first commit
- `d-14vk9b` · - · product · lodge is a command-line tool with instructions, not an MCP server
- `d-9k0dfe` · - · product · lodge's three must-nots and six success measures

Quotes: her verbatim words from the brainstorm or the spec's list for items 1, 3, 4, 5, 7 to 12, and LODGE-1 to LODGE-7, `where: lodge brainstorm`, time where the spec gives one, otherwise `2026-10-29`; own repository, local viewer, and dogfooding have no verbatim words anywhere, so they carry the `Approved` fallback (`2026-10-29 14:26`).
LODGE-4 quotes the 14:21 sentence; the `A` at 14:22 is named in its reasoning.
LODGE-4 `narrows` LODGE-3 (the hosting stays, private becomes public).
The provenance and must-nots decisions carry one quote each; the other quoted words sit in their reasoning.
No specification entries were added: the brief asks for decisions only.

## Other changes

- `.lodge.toml` (`[store] mode = "checkout"`), `lodge/decisions`, `lodge/spec` from `lodge init`.
- `README.md` rewritten for a stranger (what it holds, install from a tag, init, reading, write path with `--dry-run` first and `--attach`, viewer, hook with the frozen-glob syntax stated without `fnmatch`, `.lodge.toml` keys, development).
- Version `0.1.0` in `pyproject.toml`, `uv.lock`, and the three tests that name it (changed first; two failed with `0.1.0.dev0`, then passed).
- `scripts/check.sh` gains `uv run lodge check --gate`.

## Verification

- `uv run lodge check --gate`: `ok`; `uv run lodge waiting`: `nothing waits for the author`.
- `grep -rn '~/\|/home/' README.md src -r` prints nothing; the same pattern and `her`/`she` find nothing in `lodge/` and the README.
- `sh scripts/check.sh`: green, 998 passed.

## lodge misbehaviour met

One defect, two observations; none blocked work.
- Defect: `uv run lodge search "" --status any` prints 20 of the 21 records with no note that it stopped (help says "empty lists all"; `limit: int = 20` at `src/lodge/core/search.py:46`). A reader taking the list for the whole store misses the 21st. Exact command: `uv run lodge search "" --status any | grep -c '^d-'` prints `20`.
- The "looks related" feedback on `add` is noisy: every later decision was told it looked related to three earlier ones, mostly through the shared word "lodge" or "project" (for example the name decision against the repository decision), and none was a real replace or narrow. Cost: about one feedback line per add, ignored by judgement.
- `--dry-run` names the draft decision by an ID in its feedback lines, and the real add mints a different one, so a draft that must name another new decision by ID has to be added first and the ID read from `lodge search` (done for LODGE-3 then LODGE-4). Expected from the design; the review's M1 fix (name the draft by its file in a dry run, one guide line) is not part of fix round 1.

## Fix round 1

Taken: I2, I3, and the code Minors; nothing under `lodge/` was touched (I1, M2, M3 wait for the author's decision); M4 waits for the tag.

- I2: `core.search_counted` returns the first `limit` IDs and the total; `Listed.more` carries what was left out; `lodge search` gains `--limit N` (positive whole number, default 20) and ends with `20 of 21 shown; narrow the query or give --limit 21` when cut; the viewer's search page says `20 of 21 shown; narrow the query.`; README names `--limit`. Tests: `tests/core/test_search.py`, `tests/app/test_reads.py` (21 decisions, `more == 1`), `tests/viewer/test_pages.py`, `tests/e2e/test_search_limit.py`.
- I3: `related` drops words found in more than a third of the current decisions (once there are five or more) and needs at least two distinct shared words with a candidate. Tests in `tests/core/test_search.py`: one shared word each from three decisions gives no note; five decisions all titled "Lodge ..." give none for a draft sharing only "lodge", and a twin sharing two content words is found.
- M1: the wording above is corrected (the dry run does print an ID, in feedback).
- Check: `sh scripts/check.sh` green, 1005 passed.
