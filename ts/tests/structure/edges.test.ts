import { expect, test } from "bun:test";
import { cruise, plant } from "./plant.ts";
import { PACKAGES } from "./table.ts";

const packages = [...PACKAGES.keys()].filter((p) => p !== "main");
test("allowed_edges_match_the_table", async () => {
  const tree: Record<string, string> = {};
  const expected: string[] = [];
  for (const [pkg, allowed] of PACKAGES) {
    const path = pkg === "main" ? "src/main.ts" : `src/${pkg}/index.ts`;
    tree[path] = packages
      .filter((q) => q !== pkg)
      .map((q) => `import "#${q}";`)
      .join("\n");
    for (const q of packages)
      if (q !== pkg && !allowed.includes(q))
        expected.push(`allowed-imports: ${path} -> src/${q}/index.ts`);
  }
  expect(
    (await cruise(plant(tree))).filter((v) => v.startsWith("allowed-imports:")).sort(),
  ).toEqual(expected.sort());
});
test("every_package_uses_front_doors", async () => {
  const tree: Record<string, string> = {};
  const expected: string[] = [];
  for (const pkg of packages) {
    tree[`src/${pkg}/x.ts`] = "";
    tree[`src/${pkg}/index.ts`] = packages
      .filter((q) => q !== pkg)
      .map((q) => `import "../${q}/x.ts";`)
      .join("\n");
    for (const q of packages)
      if (q !== pkg) expected.push(`front-door: src/${pkg}/index.ts -> src/${q}/x.ts`);
  }
  expect((await cruise(plant(tree))).filter((v) => v.startsWith("front-door:")).sort()).toEqual(
    expected.sort(),
  );
});
test("relative_import_to_loose_source_is_refused", async () => {
  expect(
    await cruise(
      plant({
        "src/core/a.ts": 'import "../util.ts";',
        "src/util.ts": "",
      }),
    ),
  ).toEqual(["front-door: src/core/a.ts -> src/util.ts"]);
});
test.each(["tests", "scripts"])("cycles_and_missing_imports_bind %p", async (folder) => {
  const found = await cruise(
    plant({
      [`${folder}/a.ts`]: 'import "./b.ts";',
      [`${folder}/b.ts`]: 'import "./a.ts";',
      [`${folder}/missing.ts`]: 'import "missing-package";',
    }),
  );
  expect(found.sort()).toEqual(
    [
      `no-circular: ${folder}/a.ts -> ${folder}/b.ts`,
      `not-to-unresolvable: ${folder}/missing.ts -> missing-package`,
    ].sort(),
  );
});
