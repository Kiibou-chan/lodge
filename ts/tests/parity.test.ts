import { expect, test } from "bun:test";
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { resolve } from "node:path";
import parity from "./parity.json";
import { pythonTestNames, rowMissing, todoTitles, typescriptTestTitles } from "./parity-names.ts";

import { plant } from "./structure/plant.ts";

const root = resolve(import.meta.dir, "../..");
const rows = Object.entries(parity) as [
  string,
  { status: string; plan?: number; ts: string[]; why?: string },
][];
function files(dir: string): string[] {
  return readdirSync(dir, { withFileTypes: true }).flatMap((e) =>
    e.name === "__pycache__"
      ? []
      : e.isDirectory()
        ? files(`${dir}/${e.name}`)
        : [`${dir}/${e.name}`],
  );
}
test("every_python_test_file_is_in_the_table", () => {
  expect(rows.map(([p]) => p).sort()).toEqual(
    files(`${root}/tests`)
      .map((p) => p.slice(root.length + 1))
      .sort(),
  );
});
test("statuses_are_known", () => {
  for (const [, r] of rows) expect(["planned", "ported", "changed", "later"]).toContain(r.status);
});
test("changed_and_later_give_a_why", () => {
  for (const [, r] of rows) if (["changed", "later"].includes(r.status)) expect(r.why).toBeTruthy();
});
test("planned_rows_name_a_plan", () => {
  for (const [, r] of rows) if (r.status === "planned") expect([1, 2, 3, 4]).toContain(r.plan ?? 0);
});
test("ported_files_exist", () => {
  for (const [, r] of rows)
    if (r.status === "ported" || (r.status === "changed" && r.plan === 1))
      for (const p of r.ts) expect(existsSync(`${root}/${p}`)).toBe(true);
});
test("ported_files_keep_every_python_test_name", () => {
  for (const [p, r] of rows) if (r.status === "ported") expect(rowMissing(root, p, r)).toEqual([]);
});
test("ported_files_hold_no_todo", () => {
  for (const [, r] of rows)
    if (r.status === "ported")
      for (const p of r.ts) expect(todoTitles(readFileSync(`${root}/${p}`, "utf8"))).toEqual([]);
});
test("a_ported_file_losing_a_name_fails", () => {
  const fixture = plant({
    "tests/sample.py": "def test_a(): pass\ndef test_b(): pass",
    "tests/sample.test.ts": 'test("a", () => {})',
  });
  expect(rowMissing(fixture, "tests/sample.py", { ts: ["tests/sample.test.ts"] })).toEqual(["b"]);
});
test("parity_names_read_both_languages", () => {
  expect(
    pythonTestNames("def test_a(): pass\nasync def test_b(): pass\n# def test_no(): pass"),
  ).toEqual(["a", "b"]);
  const text = `test(\n"a", () => {}); it('b', () => {}); test.each([[1]])("c %p", x => {}); test.todo("d"); // test("no")`;
  expect(typescriptTestTitles(text)).toEqual(["a", "b", "c %p", "d"]);
  expect(todoTitles(text)).toEqual(["d"]);
});
test("parity_names_ignore_non_test_calls", () => {
  expect(
    typescriptTestTitles(
      'test.each("not a title")("real %p", () => {}); test.helper("not a test");',
    ),
  ).toEqual(["real %p"]);
});
