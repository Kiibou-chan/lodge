import { mkdtempSync, mkdirSync, symlinkSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { cruise } from "dependency-cruiser";
const here = process.cwd();
async function run(label: string, deps: boolean, preserveSymlinks: boolean) {
  const root = mkdtempSync(join(tmpdir(), "plant-"));
  const pkg: Record<string, unknown> = { name: "planted", private: true, type: "module", imports: { "#core": "./src/core/index.ts" } };
  if (deps) pkg.dependencies = { "@noble/hashes": "2.4.0", yaml: "2.9.1" };
  writeFileSync(join(root, "package.json"), JSON.stringify(pkg));
  writeFileSync(join(root, "tsconfig.json"), JSON.stringify({ compilerOptions: { module: "Preserve", moduleResolution: "bundler", allowImportingTsExtensions: true, noEmit: true } }));
  symlinkSync(join(here, "node_modules"), join(root, "node_modules"));
  mkdirSync(join(root, "src/core"), { recursive: true });
  writeFileSync(join(root, "src/core/index.ts"), 'import { parse } from "yaml";\nimport { sha256 } from "@noble/hashes/sha2.js";\nexport const a = [parse, sha256];\n');
  const result = await cruise(["src"], {
    baseDir: root, preserveSymlinks, doNotFollow: { path: "node_modules" },
    tsConfig: { fileName: join(root, "tsconfig.json") },
  });
  const out = typeof result.output === "string" ? JSON.parse(result.output) : result.output;
  const mod = out.modules.find((m: { source: string }) => m.source === "src/core/index.ts");
  for (const d of mod.dependencies) console.log(label, d.module, "->", d.resolved, d.dependencyTypes.join(","));
}
await run("no deps, follow links:", false, false);
await run("deps copied, preserveSymlinks:", true, true);
