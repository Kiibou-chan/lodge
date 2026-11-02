import { expect, test } from "bun:test";
import { cruise, plant } from "./plant.ts";
import { CORE_NPM } from "./table.ts";

test("core_importing_app", async () => {
  const found = await cruise(plant({ "src/core/a.ts": 'import "#app";', "src/app/index.ts": "" }));
  expect(found.sort()).toEqual(["allowed-imports: src/core/a.ts -> src/app/index.ts"]);
});
test("adapter_importing_adapter", async () => {
  const found = await cruise(
    plant({ "src/cli/a.ts": 'import "#store";', "src/store/index.ts": "" }),
  );
  expect(found.sort()).toEqual(["allowed-imports: src/cli/a.ts -> src/store/index.ts"]);
});
test("import_past_front_door", async () => {
  const found = await cruise(
    plant({
      "src/app/a.ts": 'import "#core"; import "../core/check.ts";',
      "src/core/check.ts": "",
    }),
  );
  expect(found.sort()).toEqual(["front-door: src/app/a.ts -> src/core/check.ts"]);
});
test("relative_import_leaving_its_package", async () => {
  const found = await cruise(plant({ "src/app/a.ts": 'import "../core/index.ts";' }));
  expect(found.sort()).toEqual(["front-door: src/app/a.ts -> src/core/index.ts"]);
});
test("test_importing_past_front_door", async () => {
  const found = await cruise(
    plant({ "tests/a.ts": 'import "../src/core/x.ts";', "src/core/x.ts": "" }),
  );
  expect(found.sort()).toEqual(["front-door: tests/a.ts -> src/core/x.ts"]);
});
test("cycle_between_modules", async () => {
  const found = await cruise(
    plant({ "src/core/a.ts": 'import "#app";', "src/app/index.ts": 'import "../core/a.ts";' }),
  );
  expect(found.sort()).toEqual([
    "allowed-imports: src/core/a.ts -> src/app/index.ts",
    "front-door: src/app/index.ts -> src/core/a.ts",
    "no-circular: src/app/index.ts -> src/core/a.ts",
  ]);
});
test("cycle_within_a_package", async () => {
  const found = await cruise(
    plant({ "src/core/a.ts": 'import "./b.ts";', "src/core/b.ts": 'import "./a.ts";' }),
  );
  expect(found.sort()).toEqual(["no-circular: src/core/a.ts -> src/core/b.ts"]);
});
test.each([
  ["src/core/a.ts", "node:fs"],
  ["src/core/a.ts", "fs"],
])("core_importing_node_builtin %p %p", async (path, name) => {
  const found = await cruise(plant({ [path]: `import "${name}";` }));
  expect(found.sort()).toEqual(
    [`core-imports: ${path} -> fs`, `file-confinement: ${path} -> fs`].sort(),
  );
});
test("core_importing_bun_builtin", async () => {
  const found = await cruise(plant({ "src/core/a.ts": 'import "bun:sqlite";' }));
  expect(found.sort()).toEqual([
    "core-imports: src/core/a.ts -> bun:sqlite",
    "sqlite-confinement: src/core/a.ts -> bun:sqlite",
  ]);
});
test("core_importing_other_npm_package", async () => {
  const found = await cruise(plant({ "src/core/a.ts": 'import "typescript";' }));
  expect(found.sort()).toEqual([
    "core-imports: src/core/a.ts -> node_modules/typescript/lib/typescript.js",
  ]);
});
test("app_importing_builtin", async () => {
  const found = await cruise(plant({ "src/app/a.ts": 'import "node:path";' }));
  expect(found.sort()).toEqual(["app-imports: src/app/a.ts -> path"]);
});
test("child_process_outside_git", async () => {
  const found = await cruise(plant({ "src/cli/a.ts": 'import "node:child_process";' }));
  expect(found.sort()).toEqual(["process-confinement: src/cli/a.ts -> child_process"]);
});
test("sqlite_outside_store", async () => {
  const found = await cruise(plant({ "src/cli/a.ts": 'import "bun:sqlite";' }));
  expect(found.sort()).toEqual(["sqlite-confinement: src/cli/a.ts -> bun:sqlite"]);
});
test.each([
  ["src/store/a.ts", "node:fs"],
  ["src/api/a.ts", "fs/promises"],
])("fs_outside_git_and_cli %p %p", async (path, name) => {
  const found = await cruise(plant({ [path]: `import "${name}";` }));
  expect(found.sort()).toEqual(
    [`file-confinement: ${path} -> ${name.replace("node:", "")}`].sort(),
  );
});
test("http_outside_api", async () => {
  const found = await cruise(plant({ "src/cli/a.ts": 'import "node:http";' }));
  expect(found.sort()).toEqual(["network-confinement: src/cli/a.ts -> http"]);
});
test("unresolvable_import", async () => {
  const found = await cruise(plant({ "src/cli/a.ts": 'import "missing-package";' }));
  expect(found.sort()).toEqual(["not-to-unresolvable: src/cli/a.ts -> missing-package"]);
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
  expect(found.sort()).toEqual([
    "allowed-imports: src/core/a.ts -> src/main.ts",
    "front-door: src/core/a.ts -> src/main.ts",
  ]);
});
test("source_cannot_escape_to_tests", async () => {
  expect(
    await cruise(
      plant({ "src/core/a.ts": 'import "../../tests/helper.ts";', "tests/helper.ts": "" }),
    ),
  ).toEqual(["front-door: src/core/a.ts -> tests/helper.ts"]);
});
