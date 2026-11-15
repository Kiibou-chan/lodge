import { expect, test } from "bun:test";
import { callViolations } from "./calls.ts";
import { plant } from "./plant.ts";

test.each(["isAuthor", "parseThread", "writeThread"])("people_required_outside_core %s", (name) => {
  for (const pkg of ["app", "store", "api"]) {
    for (const call of [`${name}()`, `${name}(value)`, `core.${name}(value)`]) {
      expect(callViolations(plant({ [`src/${pkg}/a.ts`]: call }))).toEqual([
        `src/${pkg}/a.ts:1: ${name} requires explicit people`,
      ]);
    }
    expect(
      callViolations(plant({ [`src/${pkg}/a.ts`]: `${name}(value, snapshot.people)` })),
    ).toEqual([]);
  }
  expect(callViolations(plant({ "src/core/a.ts": `${name}(value)` }))).toEqual([]);
});
