import { expect, test } from "bun:test";
import { splitLines } from "#core";
import { project } from "./project.ts";
import { QUOTE, seed } from "./support.ts";

test("broken_agent_decision_warns_above_show", async () => {
  const p = await project(),
    ids = await seed(p, [QUOTE], { decidedBy: "author" });
  const id = (await p.run("id", "d")).out.trim(),
    path = `lodge/decisions/${id}-keep-them-whole.md`;
  const entry = (await p.paths()).find((path) => path.includes(ids.entry));
  if (!entry) throw new Error("entry missing");
  const text = await p.stored(entry);
  if (text === null) throw new Error("entry missing");
  await p.handEdit({
    [path]: "---\ntitle: [unclosed\n---\n",
    [entry]: text.replace("Held.", "Held, whole."),
  });
  const lines = splitLines((await p.run("show", ids.entry)).out);
  expect(lines[0]?.startsWith(`problem: ${path}:2: `)).toBe(true);
  expect(lines[1]?.startsWith(`${ids.entry} · current`)).toBe(true);
  expect(lines.join("\n")).toContain('quote: "Keep them."');
});
