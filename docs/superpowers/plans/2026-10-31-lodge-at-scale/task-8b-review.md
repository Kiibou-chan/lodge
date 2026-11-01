# Review of Task 8b and the Tasks 6 and 7 fix round (83ef70b, 9747155)

Status: complete.
Method: committed code read in `/var/tmp/lodge-review-t8b/wt` (detached at 83ef70b); probes and mutants run only there; one timing run each on `/var/tmp/lodge-bench/s90000`, read-only.

## Part A: Task 8b, correctness

### A1 Important: a folder replaced by a symbolic link to a folder is read through the link
`src/lodge/gitstore/identity.py:125` (`read_disk`, `os.lstat(path)`) with the overlay loop at `identity.py:53`.
`os.lstat` follows every component but the last, so after `lodge/decisions` becomes a link to another folder, the base paths below it are statted and read through the link.
`disk_tree` (`checkout.py:171`, `os.walk`) never descends a link and lists the link itself as one file.
Probe (`test_folder_replaced_by_symlink_to_copy`, `_to_other_content`, `test_attachments_folder_symlink`, all failing): the fast listing keeps `lodge/decisions/old.md` and `.gitkeep` and adds `lodge/decisions` as a file; the exact tree has only the link.
With a link to a folder outside the repository holding `old.md`, the fast listing carries that outside file's blob and `texts` returns its bytes, so a read prints a file the writers refuse to touch (`_refuse_links`).
Attachments: the fast listing keeps `lodge/attachments/d-aaaaaa/log.txt`, the exact tree has none.
No test replaces a folder by a folder link (`test_symbolic_link_agrees` links a file and an unused `folder-link`).
Fix: an overlay path counts only when every ancestor under `lodge/` is a real folder; `names()` already knows the real folders it entered, so return that set and treat any overlay path whose parent is not in it as deleted (an `lstat` per ancestor is the slower alternative).
Add the three probes as tests.

### A2 Important: `core.autocrlf` written without a value is read as false
`src/lodge/gitstore/attributes.py:45` and `:106` (`_config`, `_FALSE` containing `""`).
In a git configuration file a key with no value is true, and `git config --get core.autocrlf` prints an empty line with exit 0 for it, exactly as it does for `autocrlf =` (which is false).
Probe (`test_valueless_autocrlf`, failing): repository config `[core]` then a bare `autocrlf` line, `git checkout -- lodge/decisions/old.md` writes CRLF, `git status` is clean, the fast listing says the base blob and the exact tree says the CRLF blob.
Failure scenario: a developer whose configuration has the bare key gets reads of the committed text while the disk holds CRLF, silently, because the identity equals the clean identity.
Fix: ask `git config --type=bool-or-str --get core.autocrlf` (git 2.56 here prints `true` for the bare key, `false` for the empty string, `input` for input), and drop the empty-string case from `_FALSE`; add the bare key to `test_autocrlf_spellings`.
I did not check which git version introduced `bool-or-str`; fall back to treating an unparsable answer as converting.

### A3 Minor: a folder that cannot be listed but can be searched hides its base files from the exact tree only
`identity.py:110-118` (`except OSError: continue`) against `checkout.py:171` (`os.walk` with the same silent skip).
With `lodge/decisions` at mode 0o111, `os.walk` lists nothing below it, so the exact tree has no decisions; `diff-files` and `lstat` still see the files as clean, so the fast listing keeps all of them (probe `test_unreadable_dir_searchable`, failing; as root both agree).
Scenario: a half-restored backup; the exact read would show an empty store, the fast one shows the committed one.
Fix: `names()` returns the folders whose `scandir` failed and every base path below them joins the overlay as deleted.
Whether the fast answer is the better one is the author's call; the stated contract is agreement with `disk_tree`.

### A4 Minor: a gitlink under `lodge/` appears in the listing but not in the exact tree
`identity.py:100` (`blobs[path] = fields[2]` for every type), `listing.py:124`, against `trees.py:92-95` (non-blobs are `other`, text empty, still in `blobs`) and `checkout.py:171`.
Checkout probe (`test_gitlink_in_head`, failing): HEAD holds a gitlink at `lodge/decisions/sub`, the disk an empty folder there; the exact tree lists nothing, the fast listing lists the commit ID as a blob.
In branch mode `texts` of such a path asks `cat-file --batch` for a commit that is usually absent and raises `git cannot read the file` where `read_tree` gives empty text.
Unlikely in a lodge store; fix by taking only `blob` entries in `committed` and treating other modes as `read_tree` does.

### A5 Checked and found correct
Identity changes and the listing agrees (probes, each compared with `disk_tree` through the test module's `agrees`): racy same-size edits right after `git add` and after commit (15 + 30 rounds, fresh and reused store objects), mode-only `chmod` (ident unchanged, also staged), nested untracked `.gitattributes` with a CRLF rewrite, skip-worktree set and cleared on one store object, `reset --hard` and a branch switch on one store object, an untracked file added then removed on one store object (ident returns to the clean one).
Unreadable file: `git update-index --refresh` fails on it, so the entry stays stat-dirty and `diff-files` names it; no disagreement is reachable.
The ident text `path\0blob` lines cannot be ambiguous (paths hold no NUL, blobs no newline).
Branch mode mirrors `BranchStore.trees` step for step (fetch, resolve, `rewritten` before `accept`, published equals the tip unless a rewrite stands).
Caches: the flags and conversion keys take the index stat before and after the git call and compare source bytes, so the same-tick inode reuse case cannot serve a stale result.

### A6 Important: the property test cannot fail for three of the four detection channels
`tests/gitstore/test_identity_property.py:61-62` (operation `crlf` writes a root `.gitattributes` with `*.md text eol=crlf`) and `:49` (nothing ever removes it).
After the first `crlf` step, which every seed reaches in the first sequences, every record is an `.md` file, `Conversions.paths` returns all of them, and every path is read from disk whatever `diff-index`, `diff-files`, the flags, and the untracked walk say.
Mutants applied to `identity.py` in my scratch worktree, property test only, 200 sequences each:
- `diff-index` and `diff-files` calls removed (`identity.py:35`): passes, 15 s.
- `flagged.paths` not added to the overlay (`identity.py:33`): passes.
- `disk_paths - base_paths` replaced by an empty set (`identity.py:32`): passes.
- conversion paths removed (`identity.py:34`): fails at once.
The unit tests catch the first three (14, 3, and 12 failures), so nothing ships broken today, but the plan's property is the guard for the later tasks (Task 11 rewrites the walk) and it guards only conversions.
Fix: one line at the top of the `for sequence` loop, `(repo / ".gitattributes").unlink(missing_ok=True)`.
With it the unmutated test still passes (14.9 s) and all four mutants fail within the first sequence (0.5 to 1.8 s).

### A7 Minor: test gaps
`tests/gitstore/test_attributes.py` and `test_flags.py`: mutants that drop `ident` or `working-tree-encoding` from `_ATTRIBUTES` (`attributes.py:12`) survive the whole `tests/gitstore` identity, flags, and attributes files; so does dropping `flagged.attributes` from the sources (`attributes.py:84`), because the only index-only attributes file tested is the root one, which is always a source.
`test_cached_flags_and_conversions_keyed` (`test_flags.py:34-117`) is one test of about 80 lines holding five behaviours; a failure names none of them.
Fix: one parametrised test over the six attributes (`ident` needs `$Id$` in the record), one for an index-only `lodge/decisions/.gitattributes`, and split the long test per cache and per race.
(The `core.attributesFile` source line is equivalent to `git var GIT_ATTR_GLOBAL`, which already names that file; dropping it changes nothing.)

## Part B: Task 8b, practice and design

### B1 Minor: two parsers of `ls-tree` output and two readers of the disk, already diverging
`identity.py:79-101` (`committed`) against `trees.py:75-98` (`read_tree`), and `identity.py:122-137` (`read_disk`, `names`) against `checkout.py:155-180` (`disk_tree`, `_read`).
A4 and A1 are the two divergences found; the oracle tests narrow but cannot close the gap while the logic is written twice.
Fix: `read_tree` builds on `committed`'s output (blobs plus other kinds), and `disk_tree` and the overlay share one `read_disk`; the exact tree and the fast listing then differ only in how many paths they read.

### B2 Minor: `BranchListing` copies `BranchStore.trees` and reads its private attributes
`listing.py:49-94` (the `BranchSource` protocol names `_root`, `_common`, `_wait`, `_ref`, `_held`, `_rev`, `_needs_fetch`, `_fetch`, `_missing`) against `branch.py:49-71`.
Scenario: a later change to the fetch, held-lock, or acceptance order in `trees()` (the sequence is a safety rule for rewritten branches) is made in one place; indexed branch reads and in-memory reads then disagree silently, and `test_listing_modes.py` covers only two cases.
Fix: extract `BranchStore._tip() -> (tip, kept)` used by both methods; the plan's ten-line allowance for `branch.py` is met by moving the lines, not adding them.

### B3 Minor: `CheckoutIdentity.current` does five jobs in 52 lines
`identity.py:25-76`: base caching, name union, flag and conversion collection, two diff calls, overlay reading, ident.
The two `git diff` commands are built by a loop over a list whose second element changes the argument list (`identity.py:36-50`).
Fix: `_git_changed(root, rev)`, `_overlay(...)`, and `_ident(base, overlay)`.

### B4 Minor: `texts` raises `KeyError` for an unknown path, and the overlay text map grows for the life of the store
`listing.py:112` (`listing.blobs[path]`) gives a bare `KeyError` for an attachment or unknown path where every other port error is a `LodgeError`.
`listing.py:36` (`_disk_texts.update`) is keyed by blob and never trimmed; a long-lived store object (the viewer holds one) that sees many edits keeps every version of every edited file.
Fix: `LodgeError` naming the path; keep only the texts of the current listing pair.

## Part C: performance of the clean identity at 160,800 files

Measured on `/var/tmp/lodge-bench/s90000`, read-only, my worktree at 83ef70b, `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 GIT_ATTR_NOSYSTEM=1`, gc disabled, wrappers timing each stage (scratch `stages.py`, `prof.py`).
New object, clean: `identities()` 0.759 s (the report's 0.756); same object, second call: 0.477 s (0.470).
New object, by stage (the git calls are inside their stage; the total of all `git.run_bytes` is 0.185 s):

| Stage | Where | New object (s) | Same object (s) |
|---|---|---:|---:|
| `committed(HEAD)`: `ls-tree` 0.054 plus a Python loop over 160,800 lines | `identity.py:27`, `79-101` | 0.146 | 0 (cached by revision) |
| `committed(published)`: the same again, though published equals HEAD when the branch is pushed | `listing.py:35` | 0.143 | 0.142 |
| `names()`: `scandir` of 2,253 folders, 160,800 names | `identity.py:30`, `104-119` | 0.103 | 0.098 |
| `Conversions.paths`: two keys, each scanning 160,800 paths with `rsplit`, building a 160,800-element `frozenset`, plus 6 `git config` and `git var` calls | `attributes.py:41-101`, `:82-86` | 0.142 | 0.074 |
| `Flags.read`: `ls-files` 0.020 plus a Python loop over 160,800 lines | `flags.py:164-182` | 0.076 | 0 (cached by index stat) |
| `diff-index` 0.013 and `diff-files` 0.045 | `identity.py:36-50` | 0.058 | 0.058 |
| set unions and differences, `dict(base.blobs)`, sorting | `identity.py:29-34`, `64-72` | about 0.09 | about 0.09 |

Python start plus `import lodge.main` is a further 0.17 to 0.19 s per process (measured: bare `python -c pass` 0.02 s, `import lodge.main` 0.166 s by `-X importtime`).
A CLI read is a new process, so the process-local caches (flags, conversions, the base listing) never apply across commands; the cold row is the one a user gets.

### P1 Important: as planned, Tasks 10a to 11 cannot bring a read under 0.3 s
What the plan changes in this path: Task 11 replaces `names()` (0.10 s) with folder `stat` calls and `scandir` of changed folders, about 2,253 `lstat` calls, so 0.01 to 0.02 s.
That leaves about 0.66 s for the identity plus 0.17 s of start-up before Task 10a's lookups even begin.
Nothing in Tasks 10a, 10b, 10c, or 11 touches `committed`, the conversion key, the flags loop, or the mapping copies, and Task 10a's stored-state key needs only the two idents, never the mappings.
Even a rewrite that does only the necessary work has a floor: `diff-files` 0.045 s, `ls-files` 0.020 s, `diff-index` 0.013 s (each timed alone, three runs), about fifteen small `git` spawns at 2 to 3 ms, so about 0.12 s of git, plus 0.17 s of start-up is 0.29 s before any index lookup.
So 0.3 s at 160,000 files in a fresh process is out of reach by this design; Task 12's stop rule (the server question to the coordinator) is the honest outlet, and it will fire.
What is worth doing before then, each from the code:
1. Take both tree IDs with `rev-parse` (3 ms each) and build `Listing` mappings lazily in `listings()` (the port allows it: the plan says only that `listings()` returns the states `identities()` named); the stored-state hit never needs them.
   `committed(published)` is also redundant whenever published equals HEAD: memoise `committed` by commit ID in the store (`identity.py:79`, `listing.py:35`): minus 0.14 s cold, no behaviour change.
2. Task 11's folder rows, keyed by `base`, give the extra names without the base's names, so the overlay no longer needs `base_paths` at all on a hit (`identity.py:29`, `32`); say so in Task 11's text, since its interface still hands the walk the whole base.
3. Key conversions on the sources alone (config values, source bytes and stats, the index stat) and pass the paths to `check-attr` only on a miss; scan for nested `.gitattributes` in the names Task 11 already holds, not by `rsplit` over every path twice (`attributes.py:82-86`).
4. Parse `ls-files -t -v` by scanning the raw bytes for lines whose tag is not `H` (a compiled `re` over the buffer), not by decoding 160,800 items (`flags.py:171-179`).
5. Merge the six `config`/`var` calls into one `git config --list -z` plus `git var -l` (about 10 ms).
With 1 to 5 the estimate from these timings is 0.12 s of git plus 0.03 s of Python, which with start-up is about 0.32 s; lazy imports of `yaml` and the viewer (about 0.05 s of the 0.166 s) are what would bring it under 0.3 s, and nothing in the plan owns that.
I did not build these; the figures are sums of measured stages, not a measured result.

### P2 Important: any `core.autocrlf` value other than false makes every identity read every file, 3.2 s here, and no planned task changes that
`attributes.py:45` (`before.config[0].lower() not in _FALSE ... result = before.paths`), as d-dqpf59 requires, then `identity.py:53-63` reads and hashes all 160,800 files.
Measured once with this machine's own global git configuration (`core.autocrlf=input`): `identities()` 3.243 s against 0.759 s with the configuration isolated; the report's inherited-configuration row says 2.99 s.
`input` is common on Linux and macOS, and it is this author's setting, so every real read on her machine at this size is above the 3 s `changed` limit of Task 12, whatever the index does.
`git ls-files --eol` (git reading every file in C) takes 1.5 s here (two runs), so it halves the cost and does not remove it.
What would remove it is a stat-keyed content cache in lodge's index, `(path, ino, size, mtime_ns, ctime_ns)` to blob ID, so only files whose stat changed are read; the plan's Task 9 keys parses by `(path, blob)` and Task 11 caches folders only.
The decision stands as written (a CRLF file on disk is a different read from the committed LF text); the cost does not, and Task 12's stop will report it as a read above 3 s `changed`.
Fix: record the cost in Task 12's expectations now, and decide whether a per-file stat cache joins Task 11 (it would reuse the folder-row transaction).

## Part D: the Tasks 6 and 7 fix round (9747155)

Every finding is fixed or reported; the phrase tiers are right.
Evidence:
- Tiers (`ranking.py:57-76`): `found` (ID, family, citers), then `full` (contiguous run in title or statement), then `all_words` (every word, no run), then `partial`, each in `scored` order, a stable sort over `newest`, so ties are newest first.
  Mutants on the final `found` list, `tests/core/test_ranking.py` plus `tests/e2e/test_search_many.py`: dropping `all_words` fails 5 tests; moving it after `partial` fails 2 (the e2e ones); moving it before `full` fails 3.
  For a non-phrase query `all_words` is unreachable (the `full` test is the same as the all-words test), so word queries are unchanged; `lodge search --phrase "lines brief" --brief --limit 6` on this repository now lists d-e8pdqe and d-p60ka9 first, the two records the review named.
- The candidate property is unaffected: a record in `all_words` holds every query word, so it is a candidate.
- Task 6: I1 as above; M1 measured only, as the dispatch said (the report's per-query rebuild figures are 0.15 s for 15,895 candidates); M2 `parser.py:96-100` (`parse_known_args`, leftovers become queries only for `search`; I ran `search --brief berth crane`, `search search --limit 1 --brief phrase`, and `search search --bogus`: queries kept in order, the unknown option exits 2); M3 help strings; M4 `match`/`matches`; M5 `related` now ranks through `ranking.passes`, `when`, `score` and `_candidates`, and search.py's copies are gone; M6 one `tokens`; M7 `format_brief(status=...)`; M8 `dataclasses.replace`; M9 the property now has entries in three areas, replaced and upper-case IDs, an area filter, and the explicit reversed-phrase case with a count of 4.
- Task 7: M1 the guide names the three tiers; M2 as Task 6 I1; M3 `CODE.why` clause; M4 reworded (see D2); M5 `lodge thread ID` and the rewritten-branch clause (the file is still 25 lines); M6 `test_guide_read.py` now checks two `query:` headers and `CODE` first with its sibling second, and `test_wheel.py` lists `guide-read.md`; M7 `Lodge.show` takes `context: bool = True` with a docstring, and the viewer and the call-budget test pass `context=False` (`server.py:189`; the only other caller of `Lodge.show`).
- The Task 5 against Task 4 comparison is in the report (1.354 s and 1.562 s, outputs 241 and 458 bytes).
- My gate run in the review worktree: `UV_FROZEN=true sh scripts/check.sh` exit 0, 1,690 passed and 1 skipped in 82 s, `lodge check --gate` ok.

### D1 Minor: d-t2dsd3 leaves d-emtwbs current with a statement that is now partly false
`lodge show d-emtwbs`: "a phrase matches a record whose title or statement holds its words as a contiguous run"; d-t2dsd3 (`lodge show d-t2dsd3 --provenance`: scope `product`, work item the plan, no `replaces` or `narrows`) lists two more tiers under the same `--phrase`, and the header counts them as matches.
Scenario: an agent reading `lodge search phrase` finds both as current and cannot tell which holds.
Fix: have the coordinator's decision replace d-emtwbs's statement (or narrow it), restating the run rule as its first tier.
The scope `product` is right for a change in what the command prints; the CLAUDE.md rule for plan conflicts says `process`, so say in the ledger which applied.

### D2 Minor: the waiting sentence reads as two verbs without an object
`src/lodge/cli/guide-read.md:5`: "note and tell the author what waits for an agent".
An agent that is not in contact with the author (a subagent) has nobody to tell; the review offered "tell the coordinator" or "read what waits first".
Fix: "and report what waits for an agent to whoever started you".

## Files read
CLAUDE.md; the reviewer rules; the plan's Task 8b, 8a, 9, 10a, 10b, 10c, 11, 12; task-8b-report.md; task-6-review.md; task-7-review.md; d-t2dsd3, d-emtwbs through lodge; `src/lodge/gitstore/{identity,listing,flags,attributes,checkout,branch,accepted,published,trees,git}.py`; the diffs of 9747155 (src, tests, guide) and 83ef70b (ports, adapters, fakes, conftests); `src/lodge/core/ranking.py`, `words.py`; `tests/gitstore/{test_identity,test_identity_property,test_flags,test_listing_modes,conftest,repos}.py`; `tests/gitstore/test_attributes.py` by mutants only.

## Files not read
`tests/gitstore/test_attributes.py` and `test_flags.py` line by line (behaviour checked by mutants); `scripts/bench_store.py` and the timing script beyond its call list; the viewer; Tasks 9 to 12 code (not built); the raw timing JSONL; `tests/app` tests of the show and search changes beyond their diffs.
Probes and mutants: `/var/tmp/lodge-review-t8b/scratch/` (`probes/test_probe_review.py`, `probes/test_probe2_review.py`, `mut.sh`, `muts.json`, `stages.py`, `prof.py`, `once.py`); not committed.

## Counts
Blocking 0.
Important 5: A1 (folder link read through), A2 (valueless autocrlf), A6 (property test cannot fail), P1 (0.3 s unreachable as planned), P2 (autocrlf cost).
Minor 9: A3, A4, A7, B1, B2, B3, B4, D1, D2.
