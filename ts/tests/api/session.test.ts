import { expect, test } from "bun:test";
import { hashSecret } from "#api";
import { ceremony } from "./signed.ts";

test("cookie_is_http_only_secure_and_strict", async () => {
  const w = await ceremony();
  const cookie = (await w.register()).headers.get("Set-Cookie");
  expect(cookie).toMatch(
    /^lodge_session=[A-Za-z0-9_-]{43}; HttpOnly; Secure; SameSite=Strict; Path=\/; Max-Age=2592000$/u,
  );
  await w.database.close();
});
test("session_is_stored_as_its_hash", async () => {
  const w = await ceremony();
  const c = (await w.register()).headers.get("Set-Cookie") ?? "";
  const secret = c.split(";")[0]?.split("=")[1] ?? "";
  expect(await w.accounts.sessionExpiry(secret)).toBeNull();
  expect(await w.accounts.sessionExpiry(hashSecret(secret))).not.toBeNull();
  await w.database.close();
});
test("session_lasts_30_days", async () => {
  const w = await ceremony();
  const c = (await w.register()).headers.get("Set-Cookie") ?? "";
  await w.options.clock.sleep(2591999);
  expect((await w.call("projects", {}, c)).status).toBe(200);
  await w.options.clock.sleep(1);
  expect((await w.call("projects", {}, c)).status).toBe(401);
  await w.database.close();
});
test("sign_out_ends_the_session", async () => {
  const w = await ceremony();
  const c = (await w.register()).headers.get("Set-Cookie") ?? "";
  const r = await w.call("sign-out", {}, c);
  expect(r.status).toBe(200);
  expect(r.headers.get("Set-Cookie")).toContain("Max-Age=0");
  expect((await w.call("projects", {}, c)).status).toBe(401);
  await w.database.close();
});
test.each([null, "https://other.test"])(
  "cookie_request_needs_this_servers_origin %p",
  async (origin) => {
    const w = await ceremony();
    const c = (await w.register()).headers.get("Set-Cookie") ?? "";
    expect((await w.call("projects", {}, c, origin)).status).toBe(403);
    await w.database.close();
  },
);
test("authorization_makes_an_agent_request", async () => {
  const w = await ceremony();
  const req = w.request("projects");
  req.headers.set("Cookie", (await w.register()).headers.get("Set-Cookie") ?? "");
  req.headers.set("Origin", "https://lodge.test");
  expect((await w.fetch(req)).status).toBe(403);
  await w.database.close();
});
test("me_says_who_is_signed_in", async () => {
  const w = await ceremony();
  expect(await (await w.call("me")).json()).toEqual({ result: { setUp: false, signedIn: false } });
  const c = (await w.register()).headers.get("Set-Cookie") ?? "";
  expect(await (await w.call("me", {}, c)).json()).toEqual({
    result: { setUp: true, signedIn: true, person: "ada" },
  });
  await w.database.close();
});
