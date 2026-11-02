import { expect, test } from "bun:test";
import { cruise, plant } from "./plant.ts";
import { CORE_NPM } from "./table.ts";

test("core_importing_app", async () => {
  const found = await cruise(plant({ "src/core/a.ts": 'import "#app";', "src/app/index.ts": "" }));
  expect(found.some((v) => v.startsWith("allowed-imports:"))).toBe(true);
});
test("adapter_importing_adapter", async () => {
  const found = await cruise(
    plant({ "src/cli/a.ts": 'import "#store";', "src/store/index.ts": "" }),
  );
  expect(found.some((v) => v.startsWith("allowed-imports:"))).toBe(true);
});
test("import_past_front_door", async () => {
  const found = await cruise(
    plant({
      "src/app/a.ts": 'import "#core"; import "../core/check.ts";',
      "src/core/check.ts": "",
    }),
  );
  expect(found.some((v) => v.startsWith("front-door:"))).toBe(true);
});
test("relative_import_leaving_its_package", async () => {
  const found = await cruise(plant({ "src/app/a.ts": 'import "../core/index.ts";' }));
  expect(found.some((v) => v.startsWith("front-door:"))).toBe(true);
});
test("test_importing_past_front_door", async () => {
  const found = await cruise(
    plant({ "tests/a.ts": 'import "../src/core/x.ts";', "src/core/x.ts": "" }),
  );
  expect(found.some((v) => v.startsWith("front-door:"))).toBe(true);
});
test("cycle_between_modules", async () => {
  const found = await cruise(
    plant({ "src/core/a.ts": 'import "#app";', "src/app/index.ts": 'import "../core/a.ts";' }),
  );
  expect(found.some((v) => v.startsWith("no-circular:"))).toBe(true);
});
test("cycle_within_a_package", async () => {
  const found = await cruise(
    plant({ "src/core/a.ts": 'import "./b.ts";', "src/core/b.ts": 'import "./a.ts";' }),
  );
  expect(found.some((v) => v.startsWith("no-circular:"))).toBe(true);
});
test("core_importing_node_builtin", async () => {
  const found = await cruise(plant({ "src/core/a.ts": 'import "node:fs";' }));
  expect(found.some((v) => v.startsWith("core-imports:"))).toBe(true);
});
test("core_importing_node_builtin", async () => {
  const found = await cruise(plant({ "src/core/a.ts": 'import "fs";' }));
  expect(found.some((v) => v.startsWith("core-imports:"))).toBe(true);
});
test("core_importing_bun_builtin", async () => {
  const found = await cruise(plant({ "src/core/a.ts": 'import "bun:sqlite";' }));
  expect(found.some((v) => v.startsWith("core-imports:"))).toBe(true);
});
test("core_importing_other_npm_package", async () => {
  const found = await cruise(plant({ "src/core/a.ts": 'import "typescript";' }));
  expect(found.some((v) => v.startsWith("core-imports:"))).toBe(true);
});
test("app_importing_builtin", async () => {
  const found = await cruise(plant({ "src/app/a.ts": 'import "node:path";' }));
  expect(found.some((v) => v.startsWith("app-imports:"))).toBe(true);
});
test("child_process_outside_git", async () => {
  const found = await cruise(plant({ "src/cli/a.ts": 'import "node:child_process";' }));
  expect(found.some((v) => v.startsWith("process-confinement:"))).toBe(true);
});
test("sqlite_outside_store", async () => {
  const found = await cruise(plant({ "src/cli/a.ts": 'import "bun:sqlite";' }));
  expect(found.some((v) => v.startsWith("sqlite-confinement:"))).toBe(true);
});
test("fs_outside_git_and_cli", async () => {
  const found = await cruise(plant({ "src/store/a.ts": 'import "node:fs";' }));
  expect(found.some((v) => v.startsWith("file-confinement:"))).toBe(true);
});
test("fs_outside_git_and_cli", async () => {
  const found = await cruise(plant({ "src/api/a.ts": 'import "fs/promises";' }));
  expect(found.some((v) => v.startsWith("file-confinement:"))).toBe(true);
});
test("http_outside_api", async () => {
  const found = await cruise(plant({ "src/cli/a.ts": 'import "node:http";' }));
  expect(found.some((v) => v.startsWith("network-confinement:"))).toBe(true);
});
test("unresolvable_import", async () => {
  const found = await cruise(plant({ "src/cli/a.ts": 'import "missing-package";' }));
  expect(found.some((v) => v.startsWith("not-to-unresolvable:"))).toBe(true);
});
const confinedTree = cruise(
  plant({
    "src/git/index.ts": 'import "node:fs"; import "node:child_process";',
    "src/cli/index.ts": 'import "fs";',
    "src/store/index.ts": 'import "bun:sqlite";',
    "src/api/index.ts": 'import "node:http";',
    "src/core/a.ts": CORE_NPM.map(
      (name) => `import "${name === "@noble/hashes" ? `${name}/sha2.js` : name}";`,
    ).join("\n"),
    "src/app/index.ts": "",
    "src/hook/index.ts": "",
    "src/main.ts":
      'import "#core";import "#app";import "#git";import "#cli";import "#store";import "#api";import "#hook"',
  }),
);
test("confined_io_is_allowed_where_ruled", async () => {
  expect(await confinedTree).toEqual([]);
});
test("main_may_import_every_package", async () => {
  expect(await confinedTree).toEqual([]);
});
test("core_may_import_yaml_and_noble_hashes", async () => {
  expect(
    await cruise(plant({ "src/core/a.ts": 'import "yaml"; import "@noble/hashes/sha2.js";' })),
  ).toEqual([]);
});
test("tests_and_scripts_may_use_files", async () => {
  expect(
    await cruise(
      plant({ "tests/core/a.test.ts": 'import "node:fs";', "scripts/a.ts": 'import "node:fs";' }),
    ),
  ).toEqual([]);
});
test("package_may_not_import_main", async () => {
  const found = await cruise(plant({ "src/core/a.ts": 'import "../main.ts";', "src/main.ts": "" }));
  expect(found.some((v) => v.startsWith("allowed-imports:"))).toBe(true);
});
test("source_cannot_escape_to_tests", async () => {
  expect(
    await cruise(
      plant({ "src/core/a.ts": 'import "../../tests/helper.ts";', "tests/helper.ts": "" }),
    ),
  ).toContain("front-door: src/core/a.ts -> tests/helper.ts");
});
