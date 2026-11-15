import { expect, test } from "bun:test";
import { hashSecret } from "#api";
import { agent } from "#app";
import { draft } from "./person-fixtures.ts";
import { signed } from "./signed.ts";
import { SESSION_COOKIE, world } from "./world.ts";

test("token_issue_shows_the_secret_once", async () => {
  const w = await signed();
  const b = await (await w.call("token-issue", { project: "work", label: "helper", role: null }))
    .text()
    .then(JSON.parse);
  expect(b.result.secret).toMatch(/^lodge_/u);
  const list = await (await w.call("tokens")).text();
  expect(list).toContain("helper");
  expect(list).not.toContain(b.result.secret);
  expect(list).not.toContain(hashSecret(b.result.secret));
  await w.database.close();
});
test.each(["issued_token_works_for_its_project", "revoked_token_stops_working"])(
  "%s",
  async (name) => {
    const w = await signed();
    const b = (
      await (
        await w.call("token-issue", { project: "work", label: "helper" })
      )
        .text()
        .then(JSON.parse)
    ).result;
    expect((await w.fetch(w.request("search", { project: "work" }, b.secret))).status).toBe(200);
    expect((await w.fetch(w.request("search", { project: "other" }, b.secret))).status).toBe(403);
    if (name === "revoked_token_stops_working") {
      expect((await w.call("token-revoke", { id: b.token.id })).status).toBe(200);
      expect((await w.fetch(w.request("search", { project: "work" }, b.secret))).status).toBe(401);
      expect((await w.call("token-revoke", { id: b.token.id })).status).toBe(404);
    }
    await w.database.close();
  },
);
test.each([
  "import",
  "export-target",
  "token-issue",
  "token-revoke",
  "tokens",
  "projects",
  "confirm",
  "held",
  "approve",
  "decline",
])("person_operations_refuse_an_agent_token %s", async (op) => {
  const w = await signed();
  const r = await w.fetch(w.request(op, { project: "work" }));
  expect(r.status).toBe(403);
  expect(await r.text().then(JSON.parse)).toEqual({
    error: { kind: "forbidden", message: `only the signed-in person may ${op}` },
  });
  await w.database.close();
});
test("person_may_call_record_operations", async () => {
  const w = await signed();
  expect((await w.call("search", { project: "work" })).status).toBe(200);
  expect(await (await w.call("projects")).text().then(JSON.parse)).toEqual({ result: ["work"] });
  await w.database.close();
});
test("confirm_writes_the_persons_confirmation", async () => {
  const w = await signed();
  const add = (
    await (
      await w.fetch(w.request("add", { project: "work", drafts: [["d.md", draft("reviewer")]] }))
    )
      .text()
      .then(JSON.parse)
  ).result;
  const r = await w.call("confirm", {
    project: "work",
    ids: add.ids,
    words: "Keep these.",
    area: null,
  });
  expect(r.status).toBe(200);
  const result = (await r.text().then(JSON.parse)).result;
  expect(result.outcome).toBe("published");
  const show = await (
    await w.call("show", { project: "work", ref: result.ids[0], provenance: true })
  ).text();
  expect(show).toContain("ada");
  expect(show).toContain("Keep these.");
  await w.database.close();
});
test.each([
  "approve_makes_the_held_decision_current",
  "decline_closes_the_hold",
  "held_lists_what_waits_for_the_person",
])("%s", async (name) => {
  const w = await signed();
  const add = (
    await (
      await w.fetch(w.request("add", { project: "work", drafts: [["d.md", draft()]] }))
    )
      .text()
      .then(JSON.parse)
  ).result;
  expect(add.outcome).toBe("held for approval");
  expect(typeof add.held).toBe("number");
  const store = w.projects.storeFor("work", agent());
  await store.hold({
    kind: "add",
    person: "bo",
    by: "agent",
    drafts: [],
    attachments: [],
    importing: false,
    message: "other",
  });
  const held = (await (await w.call("held", { project: "work" })).text().then(JSON.parse)).result;
  expect(held).toHaveLength(1);
  expect(held[0].seq).toBe(add.held);
  if (name === "decline_closes_the_hold") {
    expect(
      (await w.call("decline", { project: "work", seq: add.held, reason: "No." })).status,
    ).toBe(200);
    expect((await w.call("approve", { project: "work", seq: add.held })).status).toBe(404);
  } else {
    const approved = await w.call("approve", { project: "work", seq: add.held });
    expect(approved.status).toBe(200);
    const b = (await approved.text().then(JSON.parse)).result;
    expect(structuredClone(b)).toMatchObject({
      kind: "add",
      added: { outcome: "published", ids: [expect.any(String)] },
    });
    expect((await w.call("show", { project: "work", ref: b.added.ids[0] })).status).toBe(200);
  }
  expect(await (await w.call("held", { project: "work" })).text().then(JSON.parse)).toEqual({
    result: [],
  });
  await w.database.close();
});
test("global_person_operations_refuse_tokens_without_a_project", async () => {
  const w = await signed();
  for (const op of ["tokens", "projects", "token-revoke"]) {
    const r = await w.fetch(w.request(op));
    expect(await r.json()).toEqual({
      error: { kind: "forbidden", message: `only the signed-in person may ${op}` },
    });
  }
  await w.database.close();
});

test.each(["import", "export-target"])(
  "moving_operations_require_a_session_and_origin %s",
  async (operation) => {
    const w = await world();
    const response = await w.fetch(w.request(operation, { project: "work" }, null));
    expect(response.status).toBe(401);
    expect(await response.json()).toEqual({
      error: { kind: "unauthorised", message: "sign in, or send an agent token" },
    });
    await w.asPerson("projects");
    const request = w.request(operation, { project: "work" }, null);
    request.headers.set("Cookie", SESSION_COOKIE);
    request.headers.set("Origin", "https://other.test");
    const wrongOrigin = await w.fetch(request);
    expect(wrongOrigin.status).toBe(403);
    expect(await wrongOrigin.json()).toEqual({
      error: { kind: "forbidden", message: "the request does not come from this server's page" },
    });
    await w.database.close();
  },
);
