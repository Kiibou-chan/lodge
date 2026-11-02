import { expect, test } from "bun:test";
import { rmSync, writeFileSync } from "node:fs";
import { layoutViolations, sizeViolations } from "./calls.ts";
import { plant } from "./plant.ts";

test("unknown_package", () => {
  expect(layoutViolations(plant({ "src/wrong/index.ts": "" })).join()).toContain(
    "unknown package wrong",
  );
});
test("missing_front_door", () => {
  const root = plant({ "src/app/a.ts": "" });
  expect(layoutViolations(root).join()).toContain("missing front door");
});
test("nested_folder", () => {
  expect(layoutViolations(plant({ "src/core/sub/a.ts": "" })).join()).toContain("nested folder");
});
test("imports_must_match_packages", () => {
  const root = plant({});
  writeFileSync(
    `${root}/package.json`,
    JSON.stringify({ imports: { "#wrong": "./src/core/index.ts" } }),
  );
  expect(layoutViolations(root).join()).toContain("imports does not match the packages");
  rmSync(root, { recursive: true });
});
test.each(["src/core/a.ts", "tests/core/a.ts"])("oversized_module %p", (path) => {
  expect(sizeViolations(plant({ [path]: "x\n".repeat(301) }))).toEqual([
    `${path}: 301 lines (limit 300)`,
  ]);
});
test("oversized_test", () => {
  expect(sizeViolations(plant({ "tests/core/a.ts": "x\n".repeat(301) }))).toHaveLength(1);
});
test("module_at_the_limit_passes", () => {
  expect(sizeViolations(plant({ "src/core/a.ts": "x\n".repeat(300) }))).toEqual([]);
});
