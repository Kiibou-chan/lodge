import { expect, test } from "bun:test";
import { CORE_NPM, PACKAGES } from "./table.ts";

test("package_edges_match_ruling", () => {
  expect([...PACKAGES]).toEqual([
    ["core", []],
    ["app", ["core"]],
    ["store", ["app", "core"]],
    ["git", ["app", "core"]],
    ["api", ["app", "core"]],
    ["cli", ["app", "core"]],
    ["hook", ["app", "core"]],
    ["main", ["core", "app", "store", "git", "api", "cli", "hook"]],
  ]);
  expect(CORE_NPM).toEqual(["yaml", "@noble/hashes"]);
});
