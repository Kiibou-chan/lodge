import { expect, test } from "bun:test";
import { SoftAuthenticator } from "./authenticator.ts";
import { ceremony } from "./signed.ts";

test("register_with_the_setup_code_then_sign_in", async () => {
  const w = await ceremony();
  expect((await w.register()).status).toBe(200);
  const r = await w.call("sign-in", {
    response: await w.a.get(await w.challenge("sign-in-options")),
  });
  expect(r.status).toBe(200);
  const cookie = r.headers.get("Set-Cookie");
  expect(cookie).toMatch(
    /^lodge_session=[A-Za-z0-9_-]{43}; HttpOnly; Secure; SameSite=Strict; Path=\/; Max-Age=2592000$/u,
  );
  expect(await (await w.call("me", {}, cookie ?? "")).json()).toEqual({
    result: { setUp: true, signedIn: true, person: "ada" },
  });
  expect((await w.accounts.passkeys())[0]?.counter).toBe(1);
  await w.database.close();
});
test.each([
  "setup_code_is_spent_by_registration",
  "wrong_setup_code_is_refused",
  "setup_code_lasts_15_minutes",
])("%s", async (name) => {
  const w = await ceremony();
  if (name === "setup_code_is_spent_by_registration") expect((await w.register()).status).toBe(200);
  if (name === "setup_code_lasts_15_minutes") {
    await w.options.clock.sleep(899);
    expect((await w.register()).status).toBe(200);
  }
  const code = name === "wrong_setup_code_is_refused" ? "wrong" : w.code;
  expect((await w.call("register-options", { setupCode: code })).status).toBe(401);
  await w.database.close();
});
test("setup_code_expires_at_15_minutes", async () => {
  const w = await ceremony();
  await w.options.clock.sleep(900);
  expect((await w.call("register-options", { setupCode: w.code })).status).toBe(401);
  await w.database.close();
});
test.each([
  "wrong_challenge_is_refused",
  "challenge_is_spent_on_use",
  "challenge_lasts_5_minutes",
  "other_origin_is_refused",
  "user_verification_is_required",
  "refusal_does_not_echo_the_library",
])("%s", async (name) => {
  const w = await ceremony();
  const challenge = await w.challenge("register-options", { setupCode: w.code });
  if (name === "other_origin_is_refused") w.a.origin = "https://other.test";
  if (name === "user_verification_is_required") w.a.uv = false;
  const response = await w.a.create(
    name === "wrong_challenge_is_refused" || name === "refusal_does_not_echo_the_library"
      ? "wrong"
      : challenge,
  );
  if (name === "challenge_lasts_5_minutes") await w.options.clock.sleep(300);
  if (name === "challenge_is_spent_on_use")
    expect((await w.call("register", { setupCode: w.code, response })).status).toBe(200);
  const r = await w.call("register", { setupCode: w.code, response });
  expect(r.status).toBe(401);
  if (name === "refusal_does_not_echo_the_library") {
    expect(await r.text().then(JSON.parse)).toEqual({
      error: { kind: "unauthorised", message: "the passkey was not accepted" },
    });
    expect(w.logs.length).toBeGreaterThan(0);
  }
  await w.database.close();
});
test("register_options_keep_one_user_id", async () => {
  const w = await ceremony();
  const get = async () =>
    (await (await w.call("register-options", { setupCode: w.code })).text().then(JSON.parse))
      .result;
  const a = await get(),
    b = await get();
  expect(a.user.id).toBe(b.user.id);
  expect(a.authenticatorSelection).toMatchObject({
    residentKey: "preferred",
    userVerification: "required",
  });
  await w.database.close();
});
test.each([
  "counter_going_back_is_refused",
  "sign_in_requires_user_verification",
  "sign_in_challenge_is_spent",
  "sign_in_challenge_expires",
])("%s", async (name) => {
  const w = await ceremony();
  await w.register();
  const sign = async () =>
    w.call("sign-in", { response: await w.a.get(await w.challenge("sign-in-options")) });
  expect((await sign()).status).toBe(200);
  if (name === "counter_going_back_is_refused") w.a.count = -1;
  if (name === "sign_in_requires_user_verification") w.a.uv = false;
  const response = await w.a.get(await w.challenge("sign-in-options"));
  if (name === "sign_in_challenge_is_spent")
    expect((await w.call("sign-in", { response })).status).toBe(200);
  if (name === "sign_in_challenge_expires") await w.options.clock.sleep(300);
  expect((await w.call("sign-in", { response })).status).toBe(401);
  await w.database.close();
});
test("signed_in_person_adds_a_passkey", async () => {
  const w = await ceremony();
  const cookie = (await w.register()).headers.get("Set-Cookie")?.split(";")[0];
  const r = await w.call("register-options", {}, cookie);
  const opts = (await r.text().then(JSON.parse)).result;
  expect(opts.excludeCredentials[0].id).toBe((await w.accounts.passkeys())[0]?.id);
  const a = new SoftAuthenticator();
  expect(
    (await w.call("register", { response: await a.create(opts.challenge) }, cookie)).status,
  ).toBe(200);
  expect(await w.accounts.passkeys()).toHaveLength(2);
  await w.database.close();
});
test("registration_challenge_expires_between_options_and_response", async () => {
  const w = await ceremony();
  const challenge = await w.challenge("register-options", { setupCode: w.code });
  const response = await w.a.create(challenge);
  await w.options.clock.sleep(299);
  expect((await w.call("register", { setupCode: w.code, response })).status).toBe(200);
  await w.database.close();
});
test("signed_in_registration_cannot_reuse_a_challenge", async () => {
  const w = await ceremony();
  const cookie = (await w.register()).headers.get("Set-Cookie") ?? "";
  const a = new SoftAuthenticator();
  const response = await a.create(await w.challenge("register-options", {}, cookie));
  expect((await w.call("register", { response }, cookie)).status).toBe(200);
  const r = await w.call("register", { response }, cookie);
  expect(r.status).toBe(401);
  expect(await r.json()).toMatchObject({ error: { message: "the passkey was not accepted" } });
  await w.database.close();
});
test("setup_code_is_normalised_and_stored_as_a_hash", async () => {
  const w = await ceremony();
  const hash = new Bun.CryptoHasher("sha256")
    .update(w.code.toLowerCase().replaceAll("-", ""))
    .digest("hex");
  expect(await w.accounts.setupCodeValid(w.code)).toBe(false);
  expect(await w.accounts.setupCodeValid(hash)).toBe(true);
  const setupCode = ` ${w.code.toLowerCase().replaceAll("-", " - ")} `;
  const response = await w.a.create(await w.challenge("register-options", { setupCode }));
  expect((await w.call("register", { setupCode, response })).status).toBe(200);
  expect(await w.accounts.setupCodeValid(hash)).toBe(false);
  await w.database.close();
});
test("registration_user_handle_is_the_origin_and_person_hash", async () => {
  const w = await ceremony();
  const opts = (
    await (await w.call("register-options", { setupCode: w.code })).text().then(JSON.parse)
  ).result;
  expect(opts.user.id).toBe(
    new Bun.CryptoHasher("sha256")
      .update("https://lodge.test ada")
      .digest()
      .subarray(0, 16)
      .toString("base64url"),
  );
  expect(opts.rp).toEqual({ name: "lodge", id: "lodge.test" });
  expect(opts.attestation).toBe("none");
  await w.database.close();
});

test.each(["register-options", "register"])("registration_requires_access %s", async (op) => {
  const w = await ceremony();
  const response = await w.a.create(await w.challenge("register-options", { setupCode: w.code }));
  for (const cookie of [undefined, "lodge_session=unknown"]) {
    const r = await w.call(op, op === "register" ? { response } : {}, cookie);
    expect(r.status).toBe(401);
    expect(await r.json()).toEqual({ error: { kind: "unauthorised", message: "sign in again" } });
  }
  const cookie = (await w.register()).headers.get("Set-Cookie") ?? "";
  expect((await w.call(op, op === "register" ? { response } : {}, cookie, null)).status).toBe(403);
  await w.options.clock.sleep(2592000);
  expect((await w.call(op, op === "register" ? { response } : {}, cookie)).status).toBe(401);
  await w.database.close();
});

test("library_log_escapes_line_breaks", async () => {
  const w = await ceremony();
  await w.register();
  w.a.origin = "https://other.test\r\nFORGED LOG LINE";
  const response = await w.call("sign-in", {
    response: await w.a.get(await w.challenge("sign-in-options")),
  });
  expect(response.status).toBe(401);
  expect(await response.json()).toEqual({
    error: { kind: "unauthorised", message: "the passkey was not accepted" },
  });
  expect(w.logs).toHaveLength(1);
  expect(w.logs[0]).not.toMatch(/[\r\n]/u);
  expect(JSON.parse(w.logs[0] ?? "")).toContain(w.a.origin);
  await w.database.close();
});
