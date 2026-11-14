import { expect, test } from "bun:test";
import { agent } from "#app";
import { decision, filesOf } from "../core/builders.ts";
import { doc } from "./person-fixtures.ts";
import { signed } from "./signed.ts";

const seed = [
  [
    "decision.md",
    doc(
      "kind: decision\ntitle: Keep transcripts\nscope: product\ndecided_by: ada\ncode: ITEM-1\nchanges: [{entry: s-111111, action: create}]\nquote:\n  text: Keep them.\n  where: chat\n  when: '2026-10-29 10:00'",
      "Transcripts are kept.\n\n## Reasoning\n\nThey help.",
    ),
  ],
  [
    "entry.md",
    doc("kind: spec\nid: s-111111\narea: storage\ntitle: Transcripts are kept", "Held."),
  ],
  [
    "area.md",
    doc("kind: area\nname: storage\ntitle: Storage\norder: [s-111111]", "How data is kept."),
  ],
];
test("held_shows_the_drafts_as_core_reads_them", async () => {
  const w = await signed();
  const add = (
    await (
      await w.fetch(w.request("add", { project: "work", drafts: seed }))
    )
      .text()
      .then(JSON.parse)
  ).result;
  expect(add.outcome).toBe("held for approval");
  const held = (await (await w.call("held", { project: "work" })).text().then(JSON.parse)).result;
  expect(held[0].drafts).toEqual([
    {
      name: "decision.md",
      kind: "decision",
      title: "Keep transcripts",
      statement: "Transcripts are kept.",
      quote: { text: "Keep them.", where: "chat", when: "2026-10-29 10:00" },
    },
    { name: "entry.md", kind: "spec", title: "Transcripts are kept", statement: "Held." },
    { name: "area.md", kind: "area", title: "Storage", intro: "How data is kept." },
  ]);
  expect((await w.call("approve", { project: "work", seq: add.held })).status).toBe(200);
  const edit = (
    await (await w.call("draft", { project: "work", ref: "s-111111" })).text().then(JSON.parse)
  ).result;
  const store = w.projects.storeFor("work", agent());
  await store.hold({
    kind: "add",
    person: "ada",
    by: "agent",
    drafts: [["edit.md", edit]],
    attachments: [],
    importing: false,
    message: "edit",
  });
  await store.hold({
    kind: "add",
    person: "ada",
    by: "agent",
    drafts: [["bad.md", "not YAML"]],
    attachments: [],
    importing: false,
    message: "bad",
  });
  const list = (await (await w.call("held", { project: "work" })).text().then(JSON.parse)).result;
  expect(list[0].drafts[0]).toEqual({
    name: "edit.md",
    kind: "spec",
    title: "Transcripts are kept",
    statement: "Held.",
  });
  expect(list[1].drafts[0]).toEqual({
    name: "bad.md",
    problem: expect.any(String),
    text: "not YAML",
  });
  await w.database.close();
});
test("approval_failing_the_check_answers_422", async () => {
  const w = await signed();
  const initial = seed.map(([name, text]) => [
    name,
    text?.replace("decided_by: ada", "decided_by: reviewer"),
  ]);
  expect((await w.fetch(w.request("add", { project: "work", drafts: initial }))).status).toBe(200);
  const pending = [
    [
      "next.md",
      doc(
        "kind: decision\ntitle: Keep more\nscope: product\ndecided_by: ada\ncode: ITEM-2\nchanges: [{entry: s-222222, action: create}]\nquote:\n  text: Keep more.\n  where: chat\n  when: '2026-10-29 10:00'",
        "Keep more.",
      ),
    ],
    [
      "next-entry.md",
      doc(
        "kind: spec\nid: s-222222\narea: storage\ntitle: More transcripts\nrests_on: [s-111111]",
        "More.",
      ),
    ],
  ];
  const add = (
    await (
      await w.fetch(w.request("add", { project: "work", drafts: pending }))
    )
      .text()
      .then(JSON.parse)
  ).result;
  expect(add.outcome).toBe("held for approval");
  const store = w.projects.storeFor("work", agent("hand"));
  const [tree] = await store.trees();
  const writes = filesOf(
    decision({
      id: "d-zzzzzz",
      title: "Retire transcripts",
      changes: [{ entry: "s-111111", action: "retire" }],
    }),
  );
  const path = [...tree.files.keys()].find((p) => p.includes("s-111111"));
  if (!path) throw new Error("entry missing");
  writes.set(path, (tree.files.get(path) ?? "").replace("Held.", "Changed while approval waited."));
  expect(await store.publish(tree, writes, "hand edit and retirement")).toBe("published");
  const r = await w.call("approve", { project: "work", seq: add.held });
  expect(r.status).toBe(422);
  const b = await r.text().then(JSON.parse);
  expect(b.error).toEqual({ kind: "check-failed", message: "the check failed" });
  expect(b.result.kind).toBe("add");
  expect(b.result).not.toHaveProperty("checkFailed");
  expect(b.result.added.check.problems.some((p: { check: number }) => p.check === 6)).toBe(true);
  expect(
    (await (await w.call("held", { project: "work" })).text().then(JSON.parse)).result,
  ).toHaveLength(1);
  await w.database.close();
});
