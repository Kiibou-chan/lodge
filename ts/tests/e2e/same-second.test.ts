import { expect, test } from "bun:test";
import { splitLines } from "#core";
import { project } from "./project.ts";
import { decisionText, firstDecision, QUOTE, seed } from "./support.ts";

test("agent_edit_in_the_same_second_is_flagged", async () => {
  const p = await project();
  const clock = p.standStill();
  const ids = await seed(p, [QUOTE], { decidedBy: "author" });
  const edited = (await p.run("draft", ids.entry)).out.replace("Held.", "Held, whole.");
  const decision = decisionText(
    "Keep them whole",
    ["changes:", `  - {entry: ${ids.entry}, action: edit}`],
    { body: "Say so." },
  );
  const added = await p.run("add", p.draft("decision.md", decision), p.draft("entry.md", edited));
  expect([added.code, added.err]).toEqual([0, ""]);
  const flagged = firstDecision(added.out);
  expect(clock.slept).toEqual([0.75]);
  const waiting = splitLines((await p.run("waiting")).out);
  expect(waiting).toContain("waiting for the author");
  const group = waiting.indexOf("waiting for the author");
  expect(waiting.slice(0, group).some((line) => line.includes(flagged))).toBe(false);
  expect(waiting[group + 1]?.startsWith(`${flagged} · current · coordinator`)).toBe(true);
  const shown = (await p.run("show", ids.entry)).out.split("\n")[0] ?? "";
  expect(shown).toContain("coordinator");
  expect(shown).toContain("awaiting the author");
  expect((await p.run("check", "--gate")).code).toBe(0);
});
