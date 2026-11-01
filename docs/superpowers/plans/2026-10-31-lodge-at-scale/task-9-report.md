# Task 9 build report

## Task 8a fix round

All six Minor findings in task-8a-review.md are addressed.
Committed gitlinks now key their empty text with `blob_id(b"" )`, agreeing with the key for empty text on disk.
The regression test uses a gitlink in the committed tree and a FIFO at the same disk path.
`Tree.blobs` now documents keys and the empty mapping on derived trees from writes, threads, and apply; these trees omit keys because their files changed, so consumers must parse unkeyed files directly.
`disk_tree` documents its exact-byte keys, and `read_tree` names its fetched entries `blob_paths`.
The three mislabelled case ID patterns now name their actual instants, and Task 4's stale status header is replaced with its resolved status.
`blob_id` is SHA-1 only, now explicit in its docstring.
In a SHA-256 repository committed and disk keys differ for equal bytes, which only misses cache reuse; exact reads remain correct.
No algorithm change was made for SHA-256.

New test command before implementation: `uv run --frozen pytest tests/gitstore/test_tree_blobs.py::test_gitlink_keys_the_empty_text_read -q`.
Failing output, with temporary paths omitted:

```text
> assert committed.blobs[path] == disk.blobs[path] == blob_id(b"")
E AssertionError: commit object ID != e69de29bb2d1d6434b8b29ae775ad8c2e48c5391
FAILED tests/gitstore/test_tree_blobs.py::test_gitlink_keys_the_empty_text_read
1 failed in 0.54s
```

Fix-round validation: 52 focused tests passed in 0.44 s.
`UV_FROZEN=true sh scripts/check.sh` passed: 618 files formatted, Ruff clean, strict mypy on 236 files, Vulture clean, 1,691 tests passed and 1 skipped in 78.10 s, and `lodge check --gate` printed `ok` with the recorded storage-order note.
