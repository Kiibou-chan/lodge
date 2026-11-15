import { expect, test } from "bun:test";
import { world } from "./world.ts";

const document = (header: string, body: string) => `---\n${header}\n---\n\n${body}\n`;
const entry = "s-111111";
const drafts = [
  [
    "entry.md",
    document(`kind: spec\nid: ${entry}\narea: storage\ntitle: Transcripts are kept`, "Held."),
  ],
  [
    "area.md",
    document(`kind: area\nname: storage\ntitle: Storage\norder: [${entry}]`, "How data is kept."),
  ],
];
test("failed_check_answers_422_with_the_result", async () => {
  const w = await world();
  const r = await w.fetch(w.request("add", { project: "work", drafts }));
  expect(r.status).toBe(422);
  const body = (await r.json()) as { error: unknown; result: { outcome: string; check: unknown } };
  expect(body.error).toEqual({ kind: "check-failed", message: "the check failed" });
  expect(body.result.outcome).toBe("check failed");
  expect(body.result.check).toBeDefined();
  expect(
    (await w.projects.storeFor("work", { kind: "agent", role: null }).trees())[0].files.size,
  ).toBe(0);
  await w.database.close();
});
test("agents_relay_is_held", async () => {
  const w = await world();
  const decision = document(
    `kind: decision\ntitle: Keep transcripts\nscope: product\ndecided_by: coordinator\ncode: ITEM-1\nchanges:\n  - {entry: ${entry}, action: create}`,
    "Transcripts are kept.",
  );
  const add = await w.fetch(
    w.request("add", { project: "work", drafts: [["decision.md", decision], ...drafts] }),
  );
  expect(add.status).toBe(200);
  const r = await w.fetch(
    w.request("ask", {
      project: "work",
      ref: entry,
      raises: "question",
      by: "ada",
      text: "Keep these?",
      where: "chat",
      when: "2026-10-29 09:00",
    }),
  );
  expect(r.status).toBe(200);
  expect(await r.json()).toMatchObject({
    result: {
      outcome: "held for approval",
      awaits: "ada",
      held: expect.any(Number),
    },
  });
  const threads = await w.fetch(w.request("threads", { project: "work" }));
  expect(await threads.json()).toMatchObject({ result: { items: [] } });
  await w.database.close();
});
