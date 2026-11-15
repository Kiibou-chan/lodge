import { expect, test } from "bun:test";
import { handler } from "#api";
import { AddOutcome, type Lodge } from "#app";
import { world } from "./world.ts";

test.each([
  [
    "search",
    {
      query: "kept",
      filters: {
        kind: "decision",
        scope: "process",
        status: "any",
        area: "storage",
        decidedBy: "builder",
      },
      limit: 3,
    },
    "search",
    [
      "kept",
      { kind: "decision", scope: "process", status: "any", area: "storage", decidedBy: "builder" },
      { limit: 3 },
    ],
  ],
  [
    "show",
    { ref: "x", reasoning: true, provenance: true },
    "show",
    ["x", { reasoning: true, provenance: true }],
  ],
  ["timeline", { limit: 4 }, "timeline", [{ limit: 4 }]],
  ["spec", { area: "storage" }, "spec", [{ area: "storage" }]],
  ["check", { gate: true }, "check", [true]],
  ["mint", { prefix: "s" }, "mint", ["s"]],
  [
    "add",
    { drafts: [["a", "text"]], attachments: [["a.log", "log"]], importing: true, dryRun: true },
    "add",
    [[["a", "text"]], { attachments: [["a.log", "log"]], importing: true, dryRun: true }],
  ],
  [
    "ask",
    {
      ref: "x",
      raises: "question",
      by: "ada",
      text: "why",
      where: "chat",
      when: "2026-10-29 09:00",
    },
    "ask",
    ["x", "question", "ada", "why", { where: "chat", when: "2026-10-29 09:00" }],
  ],
  [
    "reply",
    { thread: "q-111111", by: "ada", text: "yes", where: "chat", when: "2026-10-29 09:00" },
    "reply",
    ["q-111111", "ada", "yes", { where: "chat", when: "2026-10-29 09:00" }],
  ],
  [
    "close",
    { thread: "q-111111", by: "ada", text: "done", where: "chat", when: "2026-10-29 09:00" },
    "close",
    ["q-111111", "ada", { text: "done", where: "chat", when: "2026-10-29 09:00" }],
  ],
] as const)("explicit_arguments_reach_lodge %s", async (op, body, method, args) => {
  const w = await world();
  const calls: unknown[] = [];
  const fake = new Proxy(
    {},
    {
      get:
        (_target, key) =>
        (...a: unknown[]) => {
          calls.push([key, a]);
          return [];
        },
    },
  ) as Lodge;
  const r = await handler({ ...w.options, lodgeFor: () => fake })(
    w.request(op, { project: "work", ...body }),
  );
  expect(r.status).toBe(200);
  expect(calls).toEqual([[method, args]]);
  await w.database.close();
});
test.each(["add", "ask", "reply", "close"])("whole_failed_result_is_preserved %s", async (op) => {
  const w = await world();
  const result = {
    outcome: AddOutcome.CHECK_FAILED,
    ids: ["s-111111"],
    check: { problems: ["synthetic problem"] },
    feedback: [],
    paths: ["entry.md"],
    minted: ["s-111111"],
    freshness: null,
    held: null,
    awaits: null,
  };
  const fake = new Proxy({}, { get: () => () => result }) as Lodge;
  const r = await handler({ ...w.options, lodgeFor: () => fake })(
    w.request(op, {
      project: "work",
      ...(op === "add"
        ? { drafts: [] }
        : {
            ...(op === "ask" ? { ref: "x", raises: "doubt" } : { thread: "q-111111" }),
            by: "builder",
            text: "words",
          }),
    }),
  );
  expect(r.status).toBe(422);
  expect(await r.json()).toEqual({
    error: { kind: "check-failed", message: "the check failed" },
    result,
  });
  await w.database.close();
});
