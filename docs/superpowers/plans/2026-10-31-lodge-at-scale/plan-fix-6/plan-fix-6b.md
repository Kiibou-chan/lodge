# Plan fix 6b: the fast identity under the coordinator's rulings on review-codex.md

Status: complete.
Rulings applied: RAW-1 rejected and Task 11b dropped (no private stat cache of any kind); LAZY-1 not taken; Task 8c kept with the review's A1/R3, A2, A4/R13, and A6; Task 11 keeps FOLD-1; conversions read every file, accepted and reported apart; R11 probed (ruling 5).
Build measured: 83ef70b, `/var/tmp/lodge-plan-fix6/venv` (CPython 3.13.5, PyYAML 6.0.3 with libyaml, SQLite 3.47.1, git 2.56.0); store `/var/tmp/lodge-bench/s90000` read-only, one call at a time; R11 probes on a copy of `s900` under `/var/tmp/lodge-plan-fix6/scratch6b/r11`.
Scripts and raw output: `measure-6b/` beside this file; the earlier `measure/` still holds the plan fix 6 scripts this file cites.

## Verdict

- Without a conversion source (the configuration STOP-2 targets), 0.3 s `seen` at 160,000 files is reachable only narrowly, and only if R11 is settled by narrowing d-dqpf59.
  One fresh process doing everything a seen indexed read needs except the app's own lookups-to-text and printing measured 0.273 s best and 0.278 s median (`measure-6b/proto_seen.py`, best of nine); building only the named command's parser saves about 0.012 s (14.4 ms against 1.9 ms), leaving about 0.035 to 0.04 s for the app path and printing; Task 12 decides.
- With a conversion source (`core.autocrlf=input` here), every file is read (d-dqpf59, ruling 4): the identity alone is 3.148 s, so `seen` is about 3.4 s and `changed` well over 3 s; reported as its own row, not targeted.
- R11 can change printed output, so the narrowing is not proposed as safe: line-end conversions never change a read's output (0 of the 14 non-gate commands differ for a decision, an entry, an area, a thread, and every file), but a removed `ident`, `working-tree-encoding`, or length-preserving `filter` attribute does (6, 15, and 8 of 15 commands differ).
  The smallest exact rule that closes it is to read every working-tree file on every fast identity, conversions or not: 3.148 s with lodge's reader, at least 0.86 s even when git hashes the files in C; under it no read target is reachable in any configuration and Task 12's stop fires.
- So the targets turn on one decision, R11-A (exact, targets unreachable) or R11-B (narrowing, targets narrowly reachable without conversions).

## R11 probe (`measure-6b/r11_probe.py`, output `r11_probe.txt`)

Method: a copy of `s900`, isolated git configuration, `LODGE_INDEX=off`, a thread opened with `lodge ask` and committed, and `Marker $Id$ here.` appended to one decision's and one entry's statement and committed (git's clean form).
At 83ef70b every read takes exact trees, so the fast path's answer (git's index bytes A) and the exact answer (disk bytes B) are both produced by running lodge with A, then B, on disk, and comparing exit status, standard output, and standard error of 15 commands: `show` of a decision with `--reasoning --provenance`, of its code, and of an entry; `search` by one word, two words, a phrase, a code, and the marker word; `waiting`; `threads`; `thread`; `spec`; `spec --area`; `check`; `check --gate`.

| Disk bytes B against git's bytes A | Commands that differ |
|---|---|
| CRLF line ends, one decision | `check --gate` only |
| CRLF, one entry | `check --gate` only |
| CRLF, the area file | `check --gate` only |
| CRLF, the thread | `check --gate` only |
| CRLF, every file | `check --gate` only |
| `ident` expansion (`$Id: <40 hex> $`), one decision | 6: three `show`, `search CODE-57`, `check`, `check --gate` |
| `ident` expansion, one entry | 7: `show` of the entry, two searches, both `spec`, `check`, `check --gate` |
| `working-tree-encoding` UTF-16 with BOM, one decision | all 15 |
| a length-preserving filter (statement case swapped), one decision | 8: three `show`, three searches, `check`, `check --gate` |

Why line ends never matter: `split_document` normalises `\r\n` to `\n` before it splits header and body (`src/lodge/core/document.py:14-22`), thread messages are cleaned the same way (`core/threads.py:143`), and the thread parser's line offset counts `\n` only (`core/threads.py:46`); git's CRLF clean step removes exactly the `\r` before each `\n`, so the two texts normalise to the same string.
The one line that differs is the gate's note `uncommitted record changes in lodge/; commit them before you push` (`gitstore/published.py:12,44`): the exact gate compares the working tree's bytes with `HEAD`'s; the gate never takes the fast identity (d-q0tb8r), so this is not a fast-read divergence.
Why the others do: their disk text differs from git's text after normalisation, and nothing in the current state records that a conversion once applied.
A size rule (a stat-clean entry whose recorded size differs from its blob's size has other bytes on disk) closes `ident` and encodings but not length-preserving filters, so it is not exact, and its inputs cost 61 ms (`ls-files --debug`) plus 85 ms (`ls-files --format=%(objectsize)`) before parsing (`measure-6b/size_calls.txt`).
Reading every file is the only exact rule found: 3.148 s with lodge's reader (the autocrlf identity, plan fix 6), and `git hash-object --no-filters --stdin-paths` over the 160,800 paths 855 to 900 ms in one process, 906 to 1,040 ms split over 2 to 16 processes, so not faster in parallel (`measure-6b/hash_all.txt`); git's route also follows links and blocks on a FIFO, so it is not proposed.

## The seen read without conversions, measured as one process

`measure-6b/proto_seen.py`, run at `s90000` with `GIT_CONFIG_GLOBAL=/dev/null GIT_CONFIG_NOSYSTEM=1 GIT_ATTR_NOSYSTEM=1`, best of nine: 0.273 s best, 0.278 s median; `python -c pass` 19.8 ms and `python -c "import lodge.main"` 149.7 ms in the same series.
What it does: `import lodge.main`; `_parser()`; git's index stat; seven git calls started together (`rev-parse HEAD^{commit} HEAD:lodge`, `merge-base`, `diff-files`, `diff-index --cached`, `ls-files -t -v`, `config --list -z`, `var -l`) and collected; the index stat again, asserted equal; `rev-parse <merge base>:lodge`; the flag fast path; the 2,252 folder rows of Task 11 with an `lstat` per folder (scratch database built by `mk_folders.py`); the build digest; the index's lock, connection, five pragmas, state row, and one bucket (scratch database from `mk_hit.py`).
What it leaves out: Task 10a's decoding of rows into `Level1`, rendering, and printing.
Stages in five runs (`proto_seen_stages.py`, `proto_stages.txt`): import 122.5 to 127.1 ms; parser 16.3 to 19.7 ms; the git group 66.4 to 72.2 ms; published tree and flag scan 17.9 to 18.6 ms; folder rows 7.3 to 7.6 ms; digest and index hit 6.5 to 7.9 ms; with Python's own start about 19 ms and exit, the 0.273 s.
A parser holding only the named command, `show` with its arguments, builds in 1.9 ms against 14.4 ms for the full one (`parser_partial.txt`); Task 8c takes that, keeping `--help`, `--version`, and unknown commands on the full parser.
The review's sequential figure (CLI floor plus four git calls, 0.266 s) is consistent: starting the group together and skipping `ls-tree` is what this process adds.
Task 8c alone (before Task 11) still builds `HEAD`'s mapping for the walk (`ls-tree` 58.3 ms plus parsing 80.0 ms) and walks the names (83.4 ms), so its identity is estimated at about 0.34 s from those stages and the group; Task 11 removes both on a hit, giving the 0.07 s group plus 0.018 s and 0.0075 s above.

## What changed in the plan, and why

| Item | Change | Handle | Decision |
|---|---|---|---|
| RAW-1, Task 11b | Dropped, with every reference (Calls made 22, the Global Constraints amendment, the cost rows, Task 12's raw-index lines) | coordinator ruling 1; review R1, R4 | none |
| LAZY-1 | Dropped; Task 8c has no Part B; the floor stays 0.166 s, less the parser saving | coordinator ruling 2 | none |
| P1 items 1, 3, 4, 5 and the index-file race | Kept in Task 8c as plan fix 6 wrote them; on an unstable key after two retries the identity, `listings()`, and `texts()` all take one exact tree (review, section on the race fix) | `measure/race.py`; review's `race_review.py` | none |
| A1 and R3, folder links | Task 8c: one disk reader for `disk_tree` and the overlay, opening each folder with `O_NOFOLLOW | O_DIRECTORY` relative to its parent's descriptor and each file relative to its folder's; an overlay path whose folder is not a reachable real folder is deleted; the three A1 probes and a link swapped in during the walk as tests | review-t8b A1 (`identity.py:125`), review R3 probe `folder-link.txt` | none |
| A2, a bare `core.autocrlf` | `config_values`: a key with no value is true | review-t8b A2 | none |
| A4 and R13, gitlinks | `Committed` keeps each entry's kind: in checkout mode a non-blob base entry is always in the overlay, so the disk decides, as `disk_tree` does; in branch mode its text is empty and `texts()` asks `cat-file` for blobs only, as `read_tree` does; tests with an empty, a populated, and an absent submodule against the exact readers | review-t8b A4; review R13 | none |
| A6, the property test | `.gitattributes` removed at the start of each sequence | review-t8b A6 (four mutants) | none |
| The parser | Built for the named command only; `--help`, `--version`, and unknown names keep the full parser, and every help and error text is unchanged | 14.4 ms against 1.9 ms | none |
| R11 | Task 8c carries the decision's consequence, one of two texts | `r11_probe.txt` | R11-A or R11-B |
| Task 11 | FOLD-1 kept; folder rows taken with `lstat`, a folder that became a link or a file relisted from its parent, rows below a folder that is no longer a reachable real folder dropped (review R3) | review R3 | FOLD-1 |
| Conversion row | Task 12 reports the configuration with `core.autocrlf=input` apart, beside the targeted rows, not under the stop | ruling 4; identity 3.148 s | CONV-1 |
| The stop | d-26e6zj already places it after Task 11; with Task 11b gone no narrowing of its timing is needed, and its scope moves into CONV-1 | ruling 4 | CONV-1 |
| Expected cost | Rows rewritten from the measured process and stages; the review's R9 (the fallback row) is moot with Task 11b gone | `proto_seen.txt` | none |

## Decisions needed (proposed statements; none recorded, no `lodge add` run)

At most one of R11-A and R11-B is recorded; the targets turn on which.

- R11-A (scope `process`, for the coordinator; the smallest exact rule, which ruling 5 asks for since R11 can change output): "The fast identity reads and hashes every working-tree file under `lodge/` on every read, whether or not a conversion source is present now, since a conversion source removed after git wrote its index leaves no trace and can make git's index text differ from the disk's."
  Handles: `r11_probe.txt` (`ident`, encoding, and filter rows); cost 3.148 s per read at 160,000 files with lodge's reader, at least 0.86 s with git hashing in C; consequence: every read above 0.3 s in every configuration, Task 12's stop fires, and the server question goes to the coordinator.
- R11-B (scope `process`, for the coordinator, narrows d-dqpf59 and, for this case only, d-rs76ks): "With no conversion source present, the five indexed reads take a file that git's index records as stat-clean at git's index blob, as `git status` does; after a conversion source is removed without the file being touched or staged again, such a read prints git's index text, which differs from the disk's only for `ident`, `filter`, and `working-tree-encoding` histories and never for line ends, which lodge's parser normalises; the gate and `add` read every file exactly."
  Handles: `r11_probe.txt` (line-end rows: no read differs; the other rows: 6 to 15 commands differ); cost if wrong: an agent reads the committed text of a record whose disk bytes were converted by an attribute since removed, until the file is touched; the gate still sees the disk's bytes.
- CONV-1 (scope `process`, for the coordinator, records ruling 4 and narrows d-232gxs's targets): "Where a conversion source is present (`core.autocrlf` true or `input`, or an attributes source that converts), the fast identity reads every file it may convert (d-dqpf59), about 3.1 s at 160,000 files under `core.autocrlf=input`; that configuration is measured and reported beside the targets, not under them, and the stop on missed targets (d-26e6zj) applies to the configuration without conversions."
- FOLD-1 (scope `process`, a planner's call, narrows d-8kq2nk): "A folder row holds the folder's difference from the base tree, its names the base lacks with their kinds and the base's names it lacks, keyed by the base tree's ID and taken with `lstat`, so a read whose folders are unchanged takes none of the base's names and never follows a link."
- No product decision: nothing here changes what a command prints, except R11-B's named case, which is a correctness contract and so `process`.

## Risks and what is not measured

- The app path of an indexed hit (rows to `Level1`, rendering, printing) is not built; the measured process leaves it about 0.035 to 0.04 s after the parser saving.
- The changed read's phases beyond the identity remain the plan's estimates until Task 10c; the current mapping costs 0.14 s on a changed read (`ls-tree` 58.3 ms plus parsing 80.0 ms).
- The fd-relative disk reader changes `disk_tree` only when a folder is swapped for a link during the walk; the gate's results are otherwise unchanged, and its tests say so.
- Mmap writers (review R4) and the other limits of git's stat comparison stay as d-8kq2nk accepts them for git's own index; nothing here adds a stat cache of lodge's own.
