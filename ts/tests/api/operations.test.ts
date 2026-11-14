import { expect, test } from "bun:test";
import { handler, issueToken } from "#api";
import { agent, Conflict, Forbidden, type Lodge, LodgeError, NotFound, StaleList } from "#app";
import { cases } from "./operation-cases.ts";
import { world } from "./world.ts";

test.each(cases)("each_operation_reaches_lodge %s", async (op, body, method, args) => {
  const w = await world();
  const calls: unknown[] = [];
  const fake = new Proxy(
    {},
    {
      get:
        (_target, key) =>
        (...a: unknown[]) => {
          calls.push([key, a]);
          return "answer";
        },
    },
  ) as Lodge;
  const r = await handler({ ...w.options, lodgeFor: () => fake })(
    w.request(op, { project: "work", ...body }),
  );
  expect(r.status).toBe(200);
  expect(await r.json()).toEqual({ result: "answer" });
  expect(calls).toEqual([[method, args]]);
  await w.database.close();
});
test.each([
  ["search", { query: 1 }, "query must be a string"],
  ["search", { limit: 1.5 }, "limit must be a whole number from 1"],
  ["search", { limit: 0 }, "limit must be a whole number from 1"],
  ["search", { filters: { kind: "other" } }, "filters.kind must be decision or spec or null"],
  ["search", { filters: { scope: "other" } }, "filters.scope must be product or process or null"],
  [
    "search",
    { filters: { status: "other" } },
    "filters.status must be current or replaced or retired or any",
  ],
  ["search", { filters: [] }, "filters must be an object"],
  ["search", { filters: { kind: 2 } }, "filters.kind must be a string or null"],
  ["search", { filters: { extra: 1 } }, "unknown field filters.extra"],
  ["show", { ref: "x", reasoning: "yes" }, "reasoning must be a boolean"],
  ["mint", { prefix: "q" }, "prefix must be d or s"],
  ["ask", { ref: "x", raises: "other" }, "raises must be doubt or question"],
  ["spec", { area: 1 }, "area must be a string or null"],
  ["add", { drafts: [["a", "b", "c"]] }, "drafts must be a list of [name, text] pairs"],
  ["add", { drafts: [["a", 1]] }, "drafts must be a list of [name, text] pairs"],
  ["add", { drafts: ["x"] }, "drafts must be a list of [name, text] pairs"],
  ["search", { extra: true }, "unknown field extra"],
  ["show", {}, "ref must be a string"],
])("arguments_are_checked %s %p", async (op, fields, message) => {
  const w = await world();
  const r = await w.fetch(w.request(op, { project: "work", ...fields }));
  expect(r.status).toBe(400);
  expect(await r.json()).toEqual({ error: { kind: "usage", message: `${op}: ${message}` } });
  await w.database.close();
});
test.each([
  [new NotFound("missing"), 404, "not-found"],
  [new Conflict("race"), 409, "conflict"],
  [new StaleList("stale"), 409, "conflict"],
  [new Forbidden("denied"), 403, "forbidden"],
  [new LodgeError("bad"), 400, "usage"],
] as const)("app_errors_map_to_kinds %p", async (error, status, kind) => {
  const w = await world();
  const fake = {
    search: () => {
      throw error;
    },
  } as unknown as Lodge;
  const r = await handler({ ...w.options, lodgeFor: () => fake })(
    w.request("search", { project: "work" }),
  );
  expect(r.status).toBe(status);
  expect(await r.json()).toEqual({ error: { kind, message: error.message } });
  await w.database.close();
});
test("token_role_is_the_actor", async () => {
  const w = await world();
  const actors: unknown[] = [];
  const fetch = handler({
    ...w.options,
    lodgeFor: (p, s, a) => {
      actors.push(a);
      return w.options.lodgeFor(p, s, a);
    },
  });
  for (const role of ["builder", null]) {
    const t = await issueToken(w.options, "work", "label", role);
    expect((await fetch(w.request("search", { project: "work" }, t.secret))).status).toBe(200);
  }
  expect(actors).toEqual([agent("builder"), agent()]);
  await w.database.close();
});
test("unknown_project_is_no_project", async () => {
  const w = await world();
  const t = await issueToken(w.options, "missing", "label", null);
  const r = await w.fetch(w.request("search", { project: "missing" }, t.secret));
  expect(r.status).toBe(404);
  expect(await r.json()).toEqual({
    error: { kind: "no-project", message: "no project named missing" },
  });
  await w.database.close();
});
