import { expect, test } from "bun:test";
import { splitLines } from "#core";
import { project } from "./project.ts";
import { decisionText, firstDecision, QUOTE, seed } from "./support.ts";

test("waiting", async () => {
  const p = await project(),
    ids = await seed(p, [QUOTE], { decidedBy: "author" });
  expect((await p.run("waiting")).out).toBe(
    "waiting for an agent\nnothing\n\nwaiting for the author\nnothing\n",
  );
  const edited = (await p.run("draft", ids.entry)).out.replace("Held.", "Held, whole.");
  const agent = decisionText(
    "Keep them whole",
    ["changes:", `  - {entry: ${ids.entry}, action: edit}`],
    { body: "Say so." },
  );
  const added = await p.run("add", p.draft("decision.md", agent), p.draft("entry.md", edited));
  expect(added.code, added.out + added.err).toBe(0);
  const flagged = firstDecision(added.out),
    waiting = await p.run("waiting");
  expect([waiting.code, waiting.err]).toEqual([0, ""]);
  expect(waiting.out).toContain(`waiting for the author\n${flagged} · current · coordinator`);
  expect(waiting.out.split("waiting for the author\n")[1]?.split("\n")[0]).toContain(
    "awaiting the author",
  );
  expect(waiting.out).not.toContain(ids.decision);
  const thread = (
    await p.run(
      "ask",
      ids.entry,
      "--kind",
      "question",
      "--by",
      "reviewer",
      p.draft("thread.txt", "Why?"),
    )
  ).out
    .trim()
    .split(" ")
    .at(-1) as string;
  const out = (await p.run("waiting")).out;
  expect(out).toContain("waiting for an agent");
  expect(out).toContain("waiting for the author");
  expect(out.indexOf("waiting for an agent")).toBeLessThan(out.indexOf("waiting for the author"));
  const [first, second] = out.split("waiting for the author");
  expect(first).not.toContain(flagged);
  expect(first).not.toContain(thread);
  expect(second).toContain(flagged);
  expect(second).toContain(thread);
  expect(second?.indexOf(flagged)).toBeLessThan(second?.indexOf(thread) as number);
});
test("waiting_groups_threads", async () => {
  const p = await project(),
    entry = (await seed(p)).entry;
  const author = await p.run(
    "ask",
    entry,
    "--kind",
    "question",
    "--by",
    "author",
    "--where",
    "chat",
    "--when",
    "2026-10-31 12:00",
    p.draft("author.txt", "Why?"),
  );
  expect([author.code, author.err]).toEqual([0, ""]);
  const held = splitLines(author.out)
    .at(-1)
    ?.match(
      /^held for approval by author as hold (\d+); nothing is current until they approve it$/u,
    );
  expect(held).not.toBeNull();
  const id = (await p.approve(Number(held?.[1])))[0] as string;
  const agent = await p.run(
    "ask",
    entry,
    "--kind",
    "doubt",
    "--by",
    "reviewer",
    p.draft("agent.txt", "Check storage."),
  );
  expect([author.code, agent.code]).toEqual([0, 0]);
  const out = (await p.run("waiting")).out;
  expect(out).toContain("waiting for an agent");
  expect(out).toContain("waiting for the author");
  expect(out.indexOf("waiting for an agent")).toBeLessThan(out.indexOf("waiting for the author"));
  const [first, second] = out.split("waiting for the author"),
    agentId = agent.out.trim().split(" ").at(-1) as string;
  expect(first).toContain(id);
  expect(first).not.toContain(agentId);
  expect(second).toContain(agentId);
  expect(second).not.toContain(id);
});
