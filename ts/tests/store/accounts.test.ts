import { afterEach, expect, test } from "bun:test";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { Conflict, NotFound, stampOf } from "#app";
import { type LodgeDatabase, openDatabase, rebuild, SqliteAccounts, SqliteProjects } from "#store";
import { FixedClock } from "../app/fakes.ts";

const opened: LodgeDatabase[] = [];
const roots: string[] = [];
afterEach(async () => {
  for (const db of opened.splice(0)) await db.close();
  for (const root of roots.splice(0)) rmSync(root, { recursive: true });
});
async function fixture(file = ":memory:") {
  const database = await openDatabase(file);
  opened.push(database);
  const clock = new FixedClock();
  return { database, clock, accounts: new SqliteAccounts(database, clock) };
}
const setup = {
  origin: "https://lodge.example",
  person: "author",
  at: "2026-10-29T09:30:00+01:00",
};
const expiry = "2026-10-29T09:30:02+01:00";
const key = {
  id: "credential",
  publicKey: "cHVibGlj",
  counter: 0,
  transports: ["internal"],
  created: setup.at,
};
const token = {
  id: "t-aaaaaa",
  project: "storage",
  role: null,
  label: "test",
  issued: setup.at,
  revoked: null,
};

test("server_is_set_up_once", async () => {
  const { accounts } = await fixture();
  expect(await accounts.setup()).toBeNull();
  await accounts.setUp(setup);
  expect(await accounts.setup()).toEqual(setup);
  await expect(accounts.setUp(setup)).rejects.toThrow(Conflict);
});
test("setup_code_is_spent_once", async () => {
  const { accounts } = await fixture();
  await accounts.issueSetupCode("hash", expiry);
  expect(await accounts.spendSetupCode("hash")).toBe(true);
  expect(await accounts.spendSetupCode("hash")).toBe(false);
  await accounts.issueSetupCode("next", expiry);
  expect(
    (await Promise.all([accounts.spendSetupCode("next"), accounts.spendSetupCode("next")])).sort(),
  ).toEqual([false, true]);
});
test("checking_a_setup_code_spends_nothing", async () => {
  const { accounts } = await fixture();
  expect(await accounts.setupCodeValid("unknown")).toBe(false);
  await accounts.issueSetupCode("hash", expiry);
  expect(await accounts.setupCodeValid("hash")).toBe(true);
  expect(await accounts.setupCodeValid("hash")).toBe(true);
});
test("setup_code_expires", async () => {
  const { accounts, clock } = await fixture();
  await accounts.issueSetupCode("hash", expiry);
  await clock.sleep(1);
  expect(await accounts.setupCodeValid("hash")).toBe(true);
  await clock.sleep(1);
  expect(await accounts.setupCodeValid("hash")).toBe(false);
  expect(await accounts.spendSetupCode("hash")).toBe(false);
});
test("newer_setup_code_replaces_older", async () => {
  const { accounts } = await fixture();
  await accounts.issueSetupCode("old", expiry);
  await accounts.issueSetupCode("new", expiry);
  expect(await accounts.setupCodeValid("old")).toBe(false);
  expect(await accounts.spendSetupCode("old")).toBe(false);
  expect(await accounts.setupCodeValid("new")).toBe(true);
});
test("passkeys_keep_their_counter", async () => {
  const { accounts } = await fixture();
  await accounts.addPasskey(key);
  await accounts.addPasskey({ ...key, id: "second" });
  await accounts.usePasskey(key.id, 7);
  expect(await accounts.passkeys()).toEqual([
    { ...key, counter: 7 },
    { ...key, id: "second" },
  ]);
});
test("sessions_start_and_end", async () => {
  const { accounts } = await fixture();
  expect(await accounts.sessionExpiry("unknown")).toBeNull();
  await accounts.startSession("hash", expiry);
  expect(await accounts.sessionExpiry("hash")).toBe(expiry);
  await accounts.endSession("hash");
  expect(await accounts.sessionExpiry("hash")).toBeNull();
});
test("tokens_issue_list_and_revoke", async () => {
  const { accounts, clock } = await fixture();
  await accounts.issueToken(token, "hash");
  await accounts.issueToken({ ...token, id: "t-bbbbbb", role: "builder" }, "other");
  expect(await accounts.tokenFor("hash")).toEqual(token);
  expect((await accounts.tokens()).map((t) => t.id)).toEqual(["t-aaaaaa", "t-bbbbbb"]);
  expect(await accounts.revokeToken("unknown")).toBe(false);
  expect(await accounts.revokeToken(token.id)).toBe(true);
  expect(await accounts.tokenFor("hash")).toBeNull();
  expect((await accounts.tokens())[0]).toEqual({ ...token, revoked: stampOf(clock.now()) });
});
test("revoked_token_keeps_its_revocation", async () => {
  const { accounts, clock } = await fixture();
  await accounts.issueToken(token, "hash");
  await accounts.revokeToken(token.id);
  const before = await accounts.tokens();
  await clock.sleep(1);
  expect(await accounts.revokeToken(token.id)).toBe(false);
  expect(await accounts.tokens()).toEqual(before);
});
test("no_event_holds_a_clear_secret", async () => {
  const { accounts, database } = await fixture();
  const secrets = ["clear-setup-secret", "clear-session-secret", "clear-token-secret"];
  const hashes = await Promise.all(
    secrets.map(async (value) => {
      const digest = await crypto.subtle.digest("SHA-256", new TextEncoder().encode(value));
      return Buffer.from(digest).toString("hex");
    }),
  );
  await accounts.issueSetupCode(hashes[0] ?? "", expiry);
  await accounts.startSession(hashes[1] ?? "", expiry);
  const issued = {
    ...token,
    clearSetupCode: secrets[0],
    clearSession: secrets[1],
    clearToken: secrets[2],
  };
  await accounts.issueToken(issued, hashes[2] ?? "");
  for (const event of await database.db.selectFrom("events").selectAll().execute())
    for (const secret of secrets)
      expect(new TextDecoder().decode(event.body)).not.toContain(secret);
});
test("server_events_belong_to_no_project", async () => {
  const { accounts, database } = await fixture();
  await accounts.setUp(setup);
  await accounts.issueSetupCode("hash", expiry);
  await accounts.spendSetupCode("hash");
  await accounts.addPasskey(key);
  await accounts.usePasskey(key.id, 1);
  await accounts.startSession("hash", expiry);
  await accounts.endSession("hash");
  await accounts.issueToken(token, "hash");
  await accounts.revokeToken(token.id);
  const events = await database.db.selectFrom("events").selectAll().execute();
  expect(events).toHaveLength(9);
  expect(events.every((e) => e.project === "" && e.actor === "server")).toBe(true);
  expect(await database.db.selectFrom("heads").selectAll().execute()).toEqual([]);
});
test("accounts_survive_reopening_and_rebuild", async () => {
  const root = mkdtempSync(join(tmpdir(), "lodge-accounts-"));
  roots.push(root);
  const file = join(root, "store.sqlite");
  const { accounts, database } = await fixture(file);
  await accounts.setUp(setup);
  await accounts.issueSetupCode("hash", expiry);
  await accounts.addPasskey(key);
  await accounts.usePasskey(key.id, 5);
  await accounts.startSession("session", expiry);
  await accounts.issueToken(token, "token");
  await accounts.revokeToken(token.id);
  await database.close();
  opened.splice(opened.indexOf(database), 1);
  const next = await fixture(file);
  for (let i = 0; i < 2; i++) {
    expect(await next.accounts.setup()).toEqual(setup);
    expect(await next.accounts.setupCodeValid("hash")).toBe(true);
    expect(await next.accounts.passkeys()).toEqual([{ ...key, counter: 5 }]);
    expect(await next.accounts.sessionExpiry("session")).toBe(expiry);
    expect(await next.accounts.tokenFor("token")).toBeNull();
    expect((await next.accounts.tokens())[0]?.revoked).toBe(setup.at);
    await rebuild(next.database);
  }
});

test("spent_newest_code_never_revives_older_codes", async () => {
  const { accounts, database } = await fixture();
  await accounts.issueSetupCode("old", expiry);
  await accounts.issueSetupCode("new", expiry);
  expect(await accounts.spendSetupCode("new")).toBe(true);
  for (let i = 0; i < 2; i++) {
    expect(await accounts.setupCodeValid("old")).toBe(false);
    expect(await accounts.spendSetupCode("old")).toBe(false);
    await rebuild(database);
  }
});
test("duplicate_token_id_is_a_conflict", async () => {
  const { accounts, database } = await fixture();
  await accounts.issueToken(token, "original");
  await accounts.issueToken({ ...token, id: "t-bbbbbb" }, "second");
  const before = await database.db.selectFrom("events").selectAll().execute();
  await expect(accounts.issueToken({ ...token, project: "other" }, "replacement")).rejects.toThrow(
    Conflict,
  );
  expect(await accounts.tokenFor("original")).toEqual(token);
  expect(await accounts.tokenFor("replacement")).toBeNull();
  expect((await accounts.tokens()).map((t) => t.id)).toEqual([token.id, "t-bbbbbb"]);
  expect(await database.db.selectFrom("events").selectAll().execute()).toEqual(before);
});
test("unknown_passkey_is_not_found", async () => {
  const { accounts, database } = await fixture();
  await expect(accounts.usePasskey("unknown", 3)).rejects.toThrow(NotFound);
  expect(await database.db.selectFrom("events").selectAll().execute()).toEqual([]);
});
test.each(["setup", "setup_codes", "passkeys", "sessions", "tokens", "project_settings"] as const)(
  "rebuild_clears_stale_%s",
  async (table) => {
    const { accounts, database, clock } = await fixture();
    await new SqliteProjects(database, clock).create("storage", "author", {
      length: { title_chars: 70 },
    });
    await accounts.setUp(setup);
    await accounts.issueSetupCode("hash", expiry);
    await accounts.addPasskey(key);
    await accounts.startSession("session", expiry);
    await accounts.issueToken(token, "token");
    const before = await database.db.selectFrom(table).selectAll().execute();
    await database.db
      .insertInto(table)
      .values({
        id: "stale",
        body: new TextEncoder().encode("{}"),
        seq: 999,
      })
      .execute();
    await rebuild(database);
    expect(await database.db.selectFrom(table).selectAll().execute()).toEqual(before);
  },
);
