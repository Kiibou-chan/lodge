# Task 5 fix round 2 report

The mapped-writer catch now has a regression that detects attribution to the wrong stage.
Both import test files share `zeroTwoCopy()` in `ts/tests/app/zero-two-copy.ts`, and the cast beside `.find(...)` has a comment explaining why the first message supplies a `by` line.

## Regression evidence

`mapped_writer_failure_is_at_the_server_stage` calls `prepareImport` with an owner containing a newline and the same owner in `people`.
It expects stage `server`, no prepared files, and exactly four check 1 problems at the three author decisions and the author thread.
It asserts the full refusal sentences, including `decided_by: U+000A cannot be written in a header` for decisions and `by: U+000A cannot be written in a header` for the thread.

Before restoring the implementation, the mapped catch was temporarily mutated from `mappedProblems.push(` to `writerProblems.push(`.
The new test failed with expected `server`, received `lodge 0.2`, ending `0 pass`, `18 filtered out`, and `1 fail`.
Restoring `mappedProblems.push(` made the same test pass with `1 pass`, `18 filtered out`, `0 fail`, and `4 expect() calls`.
The mutation is absent from the final diff.

## Source-writer catch

The source-writer `ValueError` catch remains as defensive code without a new test because its failure conditions are excluded by the preceding source parse and check.
The loop handles parsed author decisions and threads with at least one author message, using the same default `{author}` people set for parsing and source writing.
Header strings have already passed `readStr` and its unreadable-character check, while identifiers, dates, enums, and codes have passed their narrower readers.
The multiline decision quote text permits exactly the line breaks and tabs also permitted by its writer.
Decision parsing splits out the first reasoning heading and trims the statement and reasoning, so the writer's statement-heading refusal cannot fire on that parsed statement.
Thread parsing requires sequential messages, valid metadata, and non-empty bodies except for a closing message, and the writer escapes message-like body headings before parsing back with the same people set.
Consequently, unchanged parsed values satisfy the writer's header and read-back requirements; non-canonical source bytes can produce a differing render, already covered by the decision and thread writer-refusal tests, but do not cause a writer exception.
The mapped writer can throw because the supplied owner has not passed those source readers, which the new regression exercises directly.

## Validation

- Focused import tests: `29 pass`, `0 fail`, and `126 expect() calls` across two files.
- The first TypeScript gate found a formatting error in the new test; targeted Biome formatting corrected it.
- The next gate found a widened `kind` literal in the expected problem array; `as const` corrected its type.
- Final `sh scripts/check-ts.sh`: exit 0, with `1892 pass`, `0 fail`, and `6564 expect() calls` across 171 files, including type, dependency, unused-code, and structure checks.
  Biome reported 30 informational diagnostics and no errors.
- `sh scripts/check.sh`: exit 0, including `1399 passed`, the lodge gate, the TypeScript gate, and the differential comparison with `0 differences`.
- `git diff --check`: exit 0.

No earlier briefs, reports, reviews, plan wording, ledger entries, dependencies, or structure rules changed.
