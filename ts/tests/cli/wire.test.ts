import { expect, test } from "bun:test";
import { toWire } from "#api";
import { fromWire, run, runThread } from "#cli";

import { project } from "../e2e/project.ts";
import { seed } from "../e2e/support.ts";

test("round_trip", () => {
  const value = {
    nested: new Map([["key", new Set(["astral 🦦", null])]]),
    array: [null, new Map([["x", [new Set([1, 2]), true]]])],
    text: "hello 🦦",
  };
  expect(fromWire(toWire(value))).toEqual(value);
});
test("add_sends_draft_names_and_exact_attachments", async () => {
  const p = await project();
  const draft = p.draft("decision.md", "draft\r\n"),
    attachment = p.draft("evidence.log", "evidence\r\n");
  let out = "",
    err = "";
  expect(
    await run(["add", draft, "--attach", attachment], {
      cwd: p.root,
      env: {},
      version: "0.3.0",
      out: (t) => {
        out += t;
      },
      err: (t) => {
        err += t;
      },
      fetch: async (req) => {
        expect(req.method).toBe("POST");
        expect(req.headers.get("Content-Type")).toBe("application/json");
        expect(await req.json()).toEqual({
          project: "work",
          drafts: [[draft, "draft\n"]],
          attachments: [["evidence.log", "evidence\r\n"]],
          importing: false,
          dryRun: false,
        });
        return new Response(
          JSON.stringify({
            result: {
              outcome: "nothing changed",
              minted: [],
              ids: [],
              feedback: [],
              check: { notes: [], problems: [], ok: true },
            },
          }),
          { headers: { "Lodge-Version": "0.3.0" } },
        );
      },
    }),
  ).toBe(0);
  expect(out).toBe("nothing changed\n");
  expect(err).toBe("");
});
test("thread_wire_prints_closed_messages_exactly", async () => {
  const shown = {
    thread: {
      kind: "thread",
      id: "q-aaaaaa",
      about: "s-aaaaaa",
      raises: "doubt",
      state: "closed",
      opened: "2026-10-29T09:30:00+01:00",
      messages: [
        { by: "author", when: "2026-10-29 10:00", where: "chat", text: "Why?\r\n" },
        { by: "agent", when: "2026-10-29T11:00:00+01:00", where: null, text: "" },
      ],
    },
    about: null,
    read: { freshness: "fresh", unrecorded: [], statuses: new Map() },
  };
  let out = "";
  expect(
    await runThread(
      { kind: "thread", ref: "q-aaaaaa" },
      async () => fromWire(toWire(shown)),
      (t) => {
        out += t;
      },
    ),
  ).toBe(0);
  expect(out).toBe(
    "fresh\nq-aaaaaa · closed · doubt · about s-aaaaaa · 2 messages · last by agent\nabout s-aaaaaa, not found\n\nauthor · 2026-10-29 10:00 · chat\nWhy?\r\n\n\nclosed by agent · 2026-10-29T11:00:00+01:00\n",
  );
});
test("shown_sections_keep_blank_lines", async () => {
  const p = await project(),
    ids = await seed(p);
  const shown = await p.run("show", ids.decision, "--reasoning", "--provenance");
  expect(shown.code).toBe(0);
  expect(shown.err).toBe("");
  expect(shown.out).toMatch(/\n\n## Reasoning\n\n[\s\S]*\n\n## Provenance\n\n/u);
});
test("file_errors_keep_the_name_as_given", async () => {
  const p = await project();
  await p.run("init");
  for (const argv of [
    ["add", "../drafts/absent.md"],
    ["add", p.draft("draft.md", "draft"), "--attach", "../drafts/absent.md"],
    ["ask", "s-aaaaaa", "--kind", "question", "--by", "agent", "../drafts/absent.md"],
  ]) {
    expect(await p.run(...argv)).toEqual({
      code: 2,
      out: "",
      err: "lodge: ../drafts/absent.md: cannot be read: No such file or directory\n",
    });
  }
});
