import { expect, test } from "bun:test";
import { splitLines } from "#core";
import { project } from "./project.ts";
import { areaText, entryText, initialise } from "./support.ts";

test("add_failing_check_exits_1", async () => {
  const p = await project();
  await initialise(p);
  const entry = (await p.run("id", "s")).out.trim();
  const r = await p.run(
    "add",
    p.draft("area.md", areaText(entry)),
    p.draft("entry.md", entryText(entry)),
  );
  expect([r.code, r.err]).toEqual([1, ""]);
  const lines = splitLines(r.out);
  expect(lines.at(-1)).toBe("not published: the check failed");
  expect(lines.some((line) => line.startsWith("check 4: ") && line.includes(entry))).toBe(true);
  expect((await p.paths()).filter((path) => path.includes("lodge/spec/storage"))).toHaveLength(0);
});
