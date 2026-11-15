import { expect, test } from "bun:test";
import { project } from "./project.ts";
import { document, initialise } from "./support.ts";

test("add_non_string_scalar_exits_2", async () => {
  const p = await project();
  await initialise(p);
  const path = p.draft(
    "scalar.md",
    document(
      ["kind: decision", "title: [a, b]", "scope: product", "decided_by: coordinator"],
      "Text.",
    ),
  );
  const r = await p.run("add", path);
  expect([r.code, r.out]).toEqual([2, ""]);
  expect(r.err.startsWith(`lodge: ${path}:3: `)).toBe(true);
  expect(r.err).toContain("title");
  expect(r.err.split("\n").length - 1).toBe(1);
});
test("yaml_words_that_look_like_values_stay_text", async () => {
  const p = await project();
  await initialise(p);
  const r = await p.run(
    "add",
    p.draft(
      "scalar.md",
      document(
        ["kind: decision", "title: no", "scope: product", "decided_by: coordinator"],
        "Text.",
      ),
    ),
  );
  expect([r.code, r.err]).toEqual([0, ""]);
  const shown = await p.run("show", r.out.trim().split(/\s+/u).at(-1) ?? "");
  expect(shown.out.split("\n")[1]).toBe("no");
});
