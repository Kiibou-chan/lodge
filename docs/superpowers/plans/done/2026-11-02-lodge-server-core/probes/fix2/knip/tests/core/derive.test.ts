import { expect, test } from "bun:test";
import { derive } from "#core";
import { NOW } from "./helpers.ts";
test("derive", () => {
  expect(derive(["a"])).toEqual(["a"]);
  expect(NOW).toBe("2026-10-29T12:00:00+01:00");
});
