# Questions for the author: lodge at scale

**SCALE-1 · Disk space for the index** (answered: A, 2026-10-31 23:43; recorded as SCALE-1)

Question: how much disk may lodge's index take in a repository's git folder?

- A: about 240 MB at 160,000 record files: the parse cache (about 86 MB, from 8.6 MB at 16,008 files in `probes/codec.py`), the word table (52.8 MB in `probes/fts.py`), and four stored states of about 24 MB each (an estimate of 150 bytes of derived facts per record).
- B: about 160 MB, keeping two states instead of four; a third state, such as the one after a commit, is rebuilt in about 3 s at that size.

Recommendation: A. At 1,600 files the index is about 3 MB either way, and it is safe to delete at any time; four states cover the published state, the working state, and two commits without a rebuild.
