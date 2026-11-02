import { expect, test } from "bun:test";
import { CORE_PACKAGE } from "#core";

test("bun_runs_typescript_tests", () => {
  expect(CORE_PACKAGE).toBe("core");
});
