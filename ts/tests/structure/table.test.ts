import { expect, test } from "bun:test";
import { CORE_NPM, PACKAGES, STORE_NPM } from "./table.ts";

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

test("store_npm_matches_ruling", () => {
  expect(STORE_NPM).toEqual(["kysely"]);
});
