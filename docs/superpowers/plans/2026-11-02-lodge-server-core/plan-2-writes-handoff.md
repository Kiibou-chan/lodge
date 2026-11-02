# Plan 2 writes brief supplement

For the port of `app/writes.py`, carry the marker test of `isStale` from `ts/tests/core/applying.ts`: `"stale" in value && value.stale === true`.
Use it wherever Python tests `isinstance(p, StaleBase)` to classify a conflict (11-D-2).
The interface alone has no runtime value.
Do not add another front-door export without a ruling.

For `app/state.py` and `app/reads.py`, construct every result through `checkResult` (d-snrhjs).

Carried tests must be seen failing against mutations of the behaviour their titles name, rather than whole-function throws (5b-C-1 and 6-C-1).
