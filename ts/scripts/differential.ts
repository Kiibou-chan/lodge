import { readdir, readFile } from "node:fs/promises";
import { join } from "node:path";
import {
  byCodePoint,
  checkState,
  derive,
  failingIds,
  filters,
  formatLevel1,
  formatLevel3,
  level1,
  level2,
  level3,
  load,
  parseArea,
  parseCoreSettings,
  parseRecord,
  parseThread,
  renderSpec,
  search,
  splitWords,
  writeArea,
  writeRecord,
  writeThread,
} from "#core";

const root = process.argv[2];
const reference = process.argv[3];
if (!root || !reference) throw new Error("usage: differential.ts ROOT PYTHON_JSON");
const files = new Map<string, string>();
async function walk(relative: string): Promise<void> {
  for (const entry of await readdir(join(root as string, relative), { withFileTypes: true })) {
    const path = `${relative}/${entry.name}`;
    if (entry.isDirectory()) await walk(path);
    else if (entry.isFile()) files.set(path, await readFile(join(root as string, path), "utf8"));
  }
}
await walk("lodge");
const table = Bun.TOML.parse(await readFile(join(root, ".lodge.toml"), "utf8"));
parseCoreSettings(
  Object.fromEntries(Object.entries(table).filter(([key]) => ["length", "import"].includes(key))),
);
const snapshot = load({ rev: null, files, attachments: new Set() });
const derived = derive(snapshot);
const checked = checkState(snapshot);
const failing = failingIds(snapshot, checked);
const records = new Map<string, { readonly title: string }>([
  ...snapshot.decisions,
  ...snapshot.entries,
]);
const levels = Object.fromEntries(
  [...records.keys()].map((id) => [
    id,
    [
      formatLevel1(level1(snapshot, derived, id, failing)),
      level2(snapshot, derived, id, failing),
      formatLevel3(level3(snapshot, derived, id)),
    ],
  ]),
);
const queries = [
  ...new Set([...records.values()].flatMap((r) => splitWords(r.title).slice(0, 1))),
].sort(byCodePoint);
const rewrite: Record<string, readonly [string, boolean]> = {};
for (const [path, text] of files) {
  let written: string;
  if (path.startsWith("lodge/spec/") && path.endsWith("/_area.md")) {
    const area = parseArea(path, text);
    if (area.kind === "problem") continue;
    written = writeArea(area);
  } else if (/^lodge\/(?:decisions\/[^/]+|spec\/[^/]+\/[^/]+)\.md$/u.test(path)) {
    const record = parseRecord(path, text);
    if (record.kind === "problem") continue;
    written = writeRecord(record);
  } else if (/^lodge\/threads\/[^/]+\.md$/u.test(path)) {
    const thread = parseThread(path, text);
    if (thread.kind === "problem") continue;
    written = writeThread(thread);
  } else continue;
  rewrite[path] = [new Bun.CryptoHasher("sha256").update(written).digest("hex"), written === text];
}
const problems = checked.problems.map((p) => [p.path, p.check, p.line, p.message]);
problems.sort((a, b) => {
  for (let i = 0; i < a.length; i++) {
    if (a[i] === b[i]) continue;
    const x = a[i],
      y = b[i];
    if (typeof x === "number" && typeof y === "number") return x - y;
    return byCodePoint(String(x), String(y));
  }
  return 0;
});
const actual = {
  spec: renderSpec(snapshot, derived, failing),
  problems,
  levels,
  search: Object.fromEntries(queries.map((q) => [q, search(snapshot, derived, q, filters(), 20)])),
  rewrite,
};
let differences = 0;
function compare(path: string, python: unknown, typescript: unknown): void {
  if (JSON.stringify(python) === JSON.stringify(typescript)) return;
  if (
    python !== null &&
    typescript !== null &&
    typeof python === "object" &&
    typeof typescript === "object" &&
    Array.isArray(python) === Array.isArray(typescript)
  ) {
    const a = python as Record<string, unknown>,
      b = typescript as Record<string, unknown>;
    for (const key of [...new Set([...Object.keys(a), ...Object.keys(b)])].sort(byCodePoint)) {
      compare(path ? `${path}[${JSON.stringify(key)}]` : key, a[key], b[key]);
    }
    return;
  }
  console.log(`${path}: Python=${JSON.stringify(python)} TypeScript=${JSON.stringify(typescript)}`);
  differences++;
}
compare("", JSON.parse(await readFile(reference, "utf8")), actual);
console.log(
  `${records.size} records, ${snapshot.areas.size} areas, ${snapshot.threads.size} threads, ${problems.length} problems, ${queries.length} queries, ${Object.keys(rewrite).length} rewritten files`,
);
console.log(`${differences} differences`);
process.exitCode = differences ? 1 : 0;
