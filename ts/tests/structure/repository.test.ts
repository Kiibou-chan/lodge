import { expect, test } from "bun:test";
import { resolve } from "node:path";
import { callViolations, layoutViolations, sizeViolations } from "./calls.ts";
import { cruise } from "./plant.ts";

test("repository_has_no_violations", async () => {
  const root = resolve(import.meta.dir, "../..");
  expect(await cruise(root)).toEqual([]);
  expect(callViolations(root)).toEqual([]);
  expect(layoutViolations(root)).toEqual([]);
  expect(sizeViolations(root)).toEqual([]);
});
