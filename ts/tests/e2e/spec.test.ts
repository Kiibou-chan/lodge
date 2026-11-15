import { expect, test } from "bun:test";
import { project } from "./project.ts";
import { decisionText, QUOTE, seed } from "./support.ts";

test("spec", async () => {
  const p = await project(),
    ids = await seed(p),
    r = await p.run("spec");
  expect([r.code, r.err]).toEqual([0, ""]);
  for (const s of ["Storage", ids.entry, "Held."]) expect(r.out).toContain(s);
  expect((await p.run("spec", "--area", "storage")).out).toBe(r.out);
});
test("spec_of_an_empty_store", async () => {
  const p = await project();
  expect((await p.run("init")).code).toBe(0);
  const r = await p.run("spec");
  expect([r.code, r.out]).toEqual([0, "Nothing is recorded yet.\n"]);
});
test("spec_unknown_area", async () => {
  const p = await project();
  await seed(p);
  expect(await p.run("spec", "--area", "nowhere")).toEqual({
    code: 2,
    out: "",
    err: "lodge: no area named nowhere\n",
  });
});
test("spec_escapes_hash_lines_inside_a_statement", async () => {
  const p = await project(),
    ids = await seed(p, [QUOTE], { decidedBy: "author" });
  const edited = (await p.run("draft", ids.entry)).out.replace(
    "Held.",
    "Held.\n\n## Fake (s-zzzzzz)",
  );
  const agent = decisionText(
    "Keep them whole",
    ["changes:", `  - {entry: ${ids.entry}, action: edit}`],
    { body: "Say so." },
  );
  const added = await p.run("add", p.draft("d.md", agent), p.draft("e.md", edited));
  expect(added.code, added.out + added.err).toBe(0);
  const lines = (await p.run("spec")).out.split("\n");
  expect(lines).toContain("\\## Fake (s-zzzzzz)");
  expect(lines.some((l) => l.startsWith("## Fake"))).toBe(false);
  expect(lines.some((l) => l.startsWith("## Transcripts are kept") && l.includes("awaiting"))).toBe(
    true,
  );
});
