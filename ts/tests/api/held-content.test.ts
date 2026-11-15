import { expect, test } from "bun:test";
import { agent } from "#app";
import { doc, draft } from "./person-fixtures.ts";
import { signed } from "./signed.ts";

test("held decision includes its full text and attachment text", async () => {
  const w = await signed();
  try {
    const initial = await w.fetch(
      w.request("add", { project: "work", drafts: [["old.md", draft("reviewer")]] }),
    );
    expect(initial.status).toBe(200);
    const previous = (await initial.text().then(JSON.parse)).result.ids[0];
    const text = draft().replace(
      "scope: process",
      `scope: process\nreplaces: [${previous}]\nattachments: [note.txt]`,
    );
    const add = await w.fetch(
      w.request("add", {
        project: "work",
        drafts: [["decision.md", text]],
        attachments: [["note.txt", "Supporting notes.\n"]],
      }),
    );
    expect(add.status).toBe(200);
    const result = (await add.text().then(JSON.parse)).result;
    expect(result.outcome).toBe("held for approval");
    const response = await w.call("held", { project: "work" });
    expect(response.status).toBe(200);
    const held = (await response.text().then(JSON.parse)).result[0];
    expect(held.attachments).toEqual([{ name: "note.txt", text: "Supporting notes.\n" }]);
    expect(held.drafts).toEqual([
      {
        name: "decision.md",
        kind: "decision",
        title: "Keep transcripts",
        statement: "Transcripts are kept.",
        quote: { text: "Keep them.", where: "chat", when: "2026-10-29 10:00" },
        text,
      },
    ]);
    expect(held.drafts[0].text).toContain(`replaces: [${previous}]`);
    expect(held.drafts[0].text).toContain("## Reasoning\n\nThey help.");
  } finally {
    await w.database.close();
  }
});

test.each([
  ["entry.md", doc("kind: spec\nid: s-111111\narea: storage\ntitle: Stored", "Held.")],
  ["area.md", doc("kind: area\nname: storage\ntitle: Storage\norder: []", "How data is kept.")],
  ["bad.md", "not YAML"],
])("held draft carries its own text and empty attachments %s", async (name, text) => {
  const w = await signed();
  try {
    await w.projects.storeFor("work", agent()).hold({
      kind: "add",
      person: "ada",
      by: "agent",
      drafts: [[name, text]],
      attachments: [],
      importing: false,
      message: "pending",
    });
    const held = (await (await w.call("held", { project: "work" })).text().then(JSON.parse))
      .result[0];
    expect(held.drafts[0]).toMatchObject({ name, text });
    expect(held.attachments).toEqual([]);
  } finally {
    await w.database.close();
  }
});
