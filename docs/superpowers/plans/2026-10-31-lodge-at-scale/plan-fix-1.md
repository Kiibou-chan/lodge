# Plan fix round 1

Reviews: `plan-review-opus.md` (correctness and design) and `plan-review-codex.md` (feasibility and performance).
Every Blocking, Important, and Minor finding was taken; none is parked.
The coordinator's rulings for this round are d-q051s2, d-q0tb8r, d-rs76ks, d-rvf532, d-ty4dks, d-vmpspc, and d-ytf272; the planner's calls are d-7e8zhd, d-ana6c0, d-c5a1y4, d-dqpf59, d-dxqxsn, d-emtwbs, d-faakge (replacing d-f3r5aq), d-her016, d-me8vm3, and d-26e6zj.

## Correctness and design review

| Finding | Change in the plan | Decision |
|---|---|---|
| B1, libyaml fallback changes check results | Task 3 rewritten: the C loader parses only headers a line guard admits as the writer's shapes; tests for every written header, the trailing tab, block scalars, a BOM, deep nesting, and a seeded, bounded fuzz comparing both loaders | d-q051s2 |
| B2, the checkout identity changes the gate's output | The gate and `add` keep exact trees; only the five indexed reads use the fast identity (Task 8b); canonical identity is the `HEAD` tree when nothing differs, so equal states keep Task 4's shortcut | d-q0tb8r, d-7e8zhd, d-ana6c0 |
| I1, global and system attributes missed | Task 8b's conversion sources come from `git var GIT_ATTR_GLOBAL GIT_ATTR_SYSTEM`, `core.attributesFile`, `info/attributes`, and every `.gitattributes`; test helpers set `HOME` and `XDG_CONFIG_HOME` | d-dqpf59 |
| I2, paths git trusts its index for | Assume-unchanged and skip-worktree entries join the overlay (`flags.py`); git's stat shortcuts are off through `-c` overrides; Task 8a hashes working-tree bytes itself | d-c5a1y4, d-q0tb8r |
| I3, published check results from a stored state | Task 10c stores each state's own statuses and problems by its ident alone and feeds `ChangeFacts`; the published snapshot is still assembled for checks 4 to 6; a test with a problem on the same path in both states | d-dxqxsn |
| I4, indexed results cannot equal in-memory results field for field | Task 10a defines equality on printed text, with empty `Read.statuses` and the viewer-only `Shown` fields at their defaults; the viewer never uses the read model | d-rs76ks |
| I5, candidates miss records the ranking accepts | Task 6's `needs_memory` sends function-word-only phrases and codes to memory; Task 6's property test checks `rank` over candidates equals `rank` over all; Task 10b's property test under random edits | d-emtwbs, d-rs76ks |
| I6, one shared index thrashes between builds | Task 9: one file per digest of source bytes, Python, PyYAML, libyaml, SQLite, and the schema number; pruning by count and a 1 GiB folder limit | d-rvf532, d-faakge |
| I7, a shell-quoted argument is not a phrase | Task 6: `--phrase` makes a phrase, a multi-word argument is all its words; Task 7's guide examples follow and its test checks them | d-ty4dks, d-emtwbs |
| I8, Tasks 8 and 10 are each two tasks | Task 8 split into 8a and 8b, Task 10 into 10a, 10b, and 10c | d-vmpspc |
| M1, expiry as text and a clock set back | Task 10a: a validity interval with both ends, compared as timezone-aware datetimes, tested forward and back | d-faakge |
| M2, errors not in place when output is a pipe | Task 5: standard output flushed before each error, with a test | none needed |
| M3, `cites` casefolds while `core.words` lower-cases | Task 5: `str.lower()` throughout, with a test on a character that casefolds differently | none needed |
| M4, no registry in `core/codec.py` | Task 9: `from_plain` takes the class mapping from its caller; `CORE_CLASSES` in core, app adds its own | none needed |
| M5, identical-state samples omit what the proof argues away | Task 4's test adds a future-dated decision, an unlisted import source, and a link-only change | none needed |
| M6, `synchronous=OFF` and a gate trusting the parse cache | Task 9: `synchronous=NORMAL`; the gate takes parses only by hashes of bytes lodge read, with a test holding a wrong parse | d-her016, d-q0tb8r |
| M7, the order of `stat`, listing, and listing time; the FUSE disk | Task 11: `stat`, then `scandir`, then the listing time; its tests run once on a FUSE disk, and the cache is disabled on a file system kind where they fail | none needed |
| M8, `(k already listed)` hides which records | Task 6: the query header names the records already printed above | none needed |

## Feasibility and performance review

| Finding | Change in the plan | Decision |
|---|---|---|
| F1, checkout identity loses the identical-state shortcut | Canonical identity: the `HEAD` tree ID when the overlay is empty, and an overlay entry equal to the base's blob is dropped; Task 8b tests touched and reverted files | d-ana6c0 |
| F2, git index flags hide changed source files | Flags join the overlay; the gate and `add` take nothing derived from the index; parse keys are hashes of bytes lodge read | d-q0tb8r, d-c5a1y4 |
| F3, configured conversions missed | As I1, plus `core.autocrlf` in every spelling git accepts, with a test per spelling | d-dqpf59 |
| F4, the superlinear work is not removed | Task 2 adds running pointers in `derive`, doubt propagation from the doubted set through reverse links, and an index of earlier decisions for `_dates`, each against a copy of today's function; `probes/shapes.py` measures three shapes at three sizes | none needed |
| F5, the deep-chain test misses crashes in the read path | Task 2: `rests_on_tree` and `derived_order` iterative; a 5,000-entry chain through `check_state`, `rests_on_tree`, `derived_order`, and `render_spec` | none needed |
| F6, broad searches cannot meet the budget | Searches over 5,000 candidates are measured and reported apart (Tasks 10b and 12); whether the 0.3 s target covers them is the coordinator's call, open | d-me8vm3 |
| F7, module ownership creates cycles and an incomplete front door | Leaf modules `core/filters.py`, `core/listing.py`, and `app/index_types.py`; `app/__init__.py` exports every type `gitstore` uses; a skeleton step with the structure tests and mypy before any test | none needed |
| F8, stored states lack the check facts Task 10 consumes | Task 10c's per-identity facts table | d-dxqxsn |
| F9, the codec cannot encode stored answers | Task 9's codec handles mappings and frozensets, with a round trip of a `Read` with statuses | none needed |
| F10, the listing migration leaves typed consumers without a source tree | `Store.trees()` stays; `Tree` gains blob IDs; the listing methods are added beside it | d-7e8zhd |
| F11, lock errors are also `DatabaseError` | Task 9: only `SQLITE_CORRUPT` and `SQLITE_NOTADB` rebuild, checked by `sqlite_errorcode`; a test with a lock held at opening | d-her016 |
| F12, no concurrency contract | Task 10a: one read transaction per read, one write transaction for a state with its eviction; interleaving tests | d-her016 |
| F13, time validity only forward | As M1 | d-faakge |
| F14, a C parse can change diagnostics | As B1: only guard-admitted headers reach the C loader; trailing tab and nesting tests | d-q051s2 |
| F15, the changed benchmark times only its first command | Task 1's `changed` mode restores a saved index and makes a distinct edit before each timed run | none needed |
| F16, package metadata is not an implementation identity | Task 9's digest covers lodge's source bytes, tested with a same-size, same-mtime change | d-faakge |
| F17, the stop precedes the optimisation | The stop moved to Task 12, after Task 11; Tasks 10a to 10c record provisional numbers | d-26e6zj |
| F18, the linearity test does not test linearity | Task 2's `_missing` test counts the union's construction instead of timing | none needed |
