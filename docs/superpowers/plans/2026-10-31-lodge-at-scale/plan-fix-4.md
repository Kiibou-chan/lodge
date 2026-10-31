# Plan fix round 4

Recheck: `plan-recheck-3.md` (R1 Blocking, R2 and R4 Important, R3 and R5 Minor).
Every finding was taken; none is parked.
The coordinator's ruling for this round is d-e3stjn, which replaces the generations of d-gvz66f: one index file per build, cleared in place past the cap.
The planner's call is d-c6cegr (narrows d-4j98ph).

## The sweep for generations

| Place | Before | Now |
|---|---|---|
| Invariant 4 | a new generation renamed in past the cap | a clear in place in one `BEGIN IMMEDIATE` transaction raising `meta.epoch`; states rebuild lazily as cold reads |
| Call 10, call 21 | numbered generations | one file per build, cleared in place; old builds' files deleted after 7 days under the lock |
| Cost table | a rollover write about 3 s more than its read | the reads after a clear are cold reads, reported as such; the clear is timed in Task 9 |
| Task 9, files | `index-<digest>.<generation>.sqlite`, pruning by count, size, and 10 minutes untouched | `index-<digest>.sqlite` and a lock file never deleted; other builds' files after 7 days unwritten, under `flock(LOCK_EX \| LOCK_NB)`; readers hold `LOCK_SH` |
| Task 9, cap | a new generation through a temporary file and `os.link` | used pages against the cap; the clear deletes every ordinary table's rows and recreates the FTS table |
| Task 9, corruption | delete and recreate | only while this process's lock can be made exclusive without waiting |
| Task 9, tests | generation and pruning tests | `test_old_build_deleted_after_seven_days_under_the_lock`, `test_no_fcntl_deletes_nothing`, `test_cap_counts_used_pages`, `test_clear_keeps_a_readers_snapshot`, `test_two_writers_over_the_cap_clear_once`, `test_corrupt_file_held_by_another_reader_is_not_deleted` |
| Task 10a, `keep_state` | all units written when starting a generation | takes the build's epoch, and writes every unit and fact it used when the epoch moved; `test_keep_after_another_process_cleared` |
| Task 12 and the README | rollover read measured | cold reads in their own column under no stop; `rm -r` of the folder documented |

## Recheck findings

| Finding | Change in the plan | Decision |
|---|---|---|
| R1, two rebuilders share a temporary database | No temporary database and no link: the file is cleared in place | d-e3stjn |
| R2, ten minutes untouched does not prove no reader | No file a reader may hold is deleted without the lock: readers hold it shared, deletion takes it exclusive without waiting, and only after 7 days unwritten | d-e3stjn |
| R3, a changed and restored attributes file | The whole conversion key is compared before and after the git call; the change-and-restore test is in Task 8b | d-e3stjn, d-n6tqzq |
| R4, a rebuild inside the changed-read stop | The read after a clear is a cold read, reported as cold and under no stop; the replay's cold mode measures it, and Task 9 times one clear at full size | d-e3stjn |
| R5, cached published facts not carried into a rebuild | `keep_state` takes every unit and fact the build used, hits included, and writes them all when the epoch moved | d-c6cegr |
