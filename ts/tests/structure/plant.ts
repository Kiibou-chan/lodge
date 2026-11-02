import { afterAll } from "bun:test";
import {
  existsSync,
  mkdirSync,
  mkdtempSync,
  readdirSync,
  readFileSync,
  rmSync,
  symlinkSync,
  writeFileSync,
} from "node:fs";
import { createRequire } from "node:module";
import { tmpdir } from "node:os";
import { dirname, resolve } from "node:path";
import { cruise as dependencyCruise, type ICruiseResult } from "dependency-cruiser";

const planted: string[] = [];
afterAll(() => {
  for (const root of planted) rmSync(root, { recursive: true, force: true });
});
const home = resolve(import.meta.dir, "../..");
const config = createRequire(import.meta.url)(`${home}/.dependency-cruiser.cjs`);
export function plant(files: Record<string, string>): string {
  const root = mkdtempSync(`${tmpdir()}/lodge-structure-`);
  planted.push(root);
  const all = { "src/core/index.ts": "", ...files };
  const packages = [
    ...new Set(
      Object.keys(all)
        .filter((p) => p.startsWith("src/") && p.split("/").length > 2)
        .map((p) => p.split("/")[1]),
    ),
  ];
  const original = JSON.parse(readFileSync(`${home}/package.json`, "utf8"));
  writeFileSync(
    `${root}/package.json`,
    JSON.stringify({
      type: "module",
      imports: Object.fromEntries(packages.map((p) => [`#${p}`, `./src/${p}/index.ts`])),
      dependencies: original.dependencies,
      devDependencies: original.devDependencies,
    }),
  );
  writeFileSync(`${root}/tsconfig.json`, readFileSync(`${home}/tsconfig.json`));
  symlinkSync(`${home}/node_modules`, `${root}/node_modules`, "dir");
  for (const [path, text] of Object.entries(all)) {
    mkdirSync(dirname(`${root}/${path}`), { recursive: true });
    writeFileSync(`${root}/${path}`, text);
  }
  return root;
}
export async function cruise(root: string): Promise<string[]> {
  const paths = ["src", "tests", "scripts"].filter(
    (p) => existsSync(`${root}/${p}`) && readdirSync(`${root}/${p}`).length,
  );
  const result = await dependencyCruise(paths, {
    ...config.options,
    baseDir: root,
    ruleSet: config,
    validate: true,
    outputType: "json",
    tsConfig: { fileName: `${root}/tsconfig.json` },
  });
  const output: ICruiseResult =
    typeof result.output === "string" ? JSON.parse(result.output) : result.output;
  return output.summary.violations.map((v) => `${v.rule.name}: ${v.from} -> ${v.to}`);
}
