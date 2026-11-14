import { expect, test } from "bun:test";
import { hashSecret, issueToken, tokenId } from "#api";
import { world } from "./world.ts";

test.each([
  ["no_credentials_is_unauthorised", null, "sign in, or send an agent token"],
  ["unknown_token_is_unauthorised", "unknown", "the agent token is not known or was revoked"],
])("%s", async (_name, secret, message) => {
  const w = await world();
  const r = await w.fetch(w.request("search", { project: "work" }, secret));
  expect(r.status).toBe(401);
  expect(await r.json()).toEqual({ error: { kind: "unauthorised", message } });
  await w.database.close();
});
test("revoked_token_is_unauthorised", async () => {
  const w = await world();
  await w.accounts.revokeToken(w.issued.token.id);
  expect((await w.fetch(w.request("search", { project: "work" }))).status).toBe(401);
  await w.database.close();
});
test("token_reaches_only_its_project", async () => {
  const w = await world();
  const r = await w.fetch(w.request("search", { project: "other" }));
  expect(r.status).toBe(403);
  expect(await r.json()).toEqual({
    error: { kind: "forbidden", message: "this agent token is for project work" },
  });
  await w.database.close();
});
test("token_may_create_its_own_project_only", async () => {
  const w = await world();
  const token = await issueToken(w.options, "new", "new", null);
  expect(
    (await w.fetch(w.request("project-create", { project: "other", settings: {} }, token.secret)))
      .status,
  ).toBe(403);
  expect(
    (await w.fetch(w.request("project-create", { project: "new", settings: {} }, token.secret)))
      .status,
  ).toBe(200);
  await w.database.close();
});
test("issued_token_is_stored_as_its_hash", async () => {
  const w = await world();
  const calls: unknown[][] = [];
  const issued = await issueToken(
    {
      ...w.options,
      accounts: new Proxy(w.accounts, {
        get(target, key) {
          if (key === "issueToken")
            return async (...args: Parameters<typeof target.issueToken>) => {
              calls.push(args);
              await target.issueToken(...args);
            };
          const v = Reflect.get(target, key);
          return typeof v === "function" ? v.bind(target) : v;
        },
      }),
    },
    "work",
    "label",
    "builder",
  );
  expect(issued.secret).toMatch(/^lodge_[A-Za-z0-9_-]{43}$/u);
  expect(calls).toEqual([[issued.token, hashSecret(issued.secret)]]);
  expect(JSON.stringify(calls)).not.toContain(issued.secret);
  expect(hashSecret("abc")).toBe(
    "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
  );
  expect(await w.accounts.tokenFor(hashSecret(issued.secret))).toEqual(issued.token);
  expect(issued.token).toMatchObject({
    project: "work",
    label: "label",
    role: "builder",
    issued: "2026-10-29T09:30:00+01:00",
    revoked: null,
  });
  await w.database.close();
});
test("token_id_is_spelled_as_an_id", () => {
  expect(tokenId(new Uint8Array([0, 31, 32, 33, 255, 10]))).toBe("t-0z01za");
});
