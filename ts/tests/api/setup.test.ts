import { expect, test } from "bun:test";
import { type ServerIo, serverCommand } from "#api";
import { ceremony } from "./signed.ts";
import { world } from "./world.ts";

async function command(setUp = false) {
  const w = await world(setUp);
  const out: string[] = [],
    err: string[] = [],
    listens: unknown[] = [];
  const io: ServerIo = {
    out: (t) => out.push(t),
    err: (t) => err.push(t),
    open: async () => ({ options: w.options }),
    listen: async (...args) => {
      listens.push(args);
    },
  };
  return { ...w, out, err, listens, io, run: (args: string[]) => serverCommand(args, io) };
}
const args = [
  "setup",
  "--data",
  "synthetic.db",
  "--origin",
  "https://lodge.test",
  "--person",
  "ada",
];
test("setup_prints_a_code", async () => {
  const w = await command();
  expect(await w.run(args)).toBe(0);
  expect(w.out.join("")).toMatch(
    /^setup code: [0-9A-HJKMNP-TV-Z]{5}(-[0-9A-HJKMNP-TV-Z]{5}){3}\nit works once, for 15 minutes: open https:\/\/lodge.test, enter it, and register a passkey\n$/u,
  );
  await w.database.close();
});
test("setup_again_before_a_passkey_gives_a_new_code", async () => {
  const w = await command();
  await w.run(args);
  const old = w.out.join("").split("\n")[0]?.slice(12);
  await w.run(args);
  expect((await w.fetch(w.request("register-options", { setupCode: old }, null))).status).toBe(401);
  await w.database.close();
});
test("setup_after_a_passkey_is_refused", async () => {
  const w = await ceremony();
  await w.register();
  const err: string[] = [];
  expect(
    await serverCommand(args, {
      out: () => {},
      err: (t) => err.push(t),
      open: async () => ({ options: w.options }),
      listen: async () => {},
    }),
  ).toBe(2);
  expect(err.join("")).toContain(
    "a passkey is registered; sign in on https://lodge.test to add another",
  );
  await w.database.close();
});
test("setup_fixes_origin_and_person", async () => {
  const w = await command();
  await w.run(args);
  expect(await w.run(args.map((v) => (v === "ada" ? "bo" : v)))).toBe(2);
  expect(w.err.join("")).toContain("the server is set up for https://lodge.test and ada");
  await w.database.close();
});
test.each([
  "http://lodge.example.org",
  "https://lodge.example.org/path",
  "ftp://x",
  "http://127.0.0.1:8787",
  "http://[::1]:8787",
])("setup_refuses_a_bad_origin %s", async (origin) => {
  const w = await command();
  expect(await w.run(args.map((v) => (v === "https://lodge.test" ? origin : v)))).toBe(2);
  expect(await w.accounts.setup()).toBeNull();
  await w.database.close();
});
test.each(["Ada", "1ada"])("setup_refuses_a_bad_person %s", async (person) => {
  const w = await command();
  expect(await w.run(args.map((v) => (v === "ada" ? person : v)))).toBe(2);
  expect(w.err.join("")).toContain(
    "the person's name must be lower-case letters, digits, and hyphens, starting with a letter",
  );
  await w.database.close();
});
test("serve_needs_setup", async () => {
  const w = await command();
  expect(await w.run(["serve", "--data", "synthetic.db"])).toBe(2);
  expect(w.err.join("")).toBe("lodge: the server is not set up; run lodge server setup\n");
  await w.database.close();
});
test("serve_listens_where_told", async () => {
  const w = await command(true);
  expect(await w.run(["serve", "--data", "synthetic.db"])).toBe(0);
  expect(w.listens[0]).toEqual([expect.any(Function), "127.0.0.1", 8787]);
  expect(
    await w.run(["serve", "--data", "synthetic.db", "--host", "0.0.0.0", "--port", "9000"]),
  ).toBe(0);
  expect(w.listens[1]).toEqual([expect.any(Function), "0.0.0.0", 9000]);
  await w.database.close();
});
test.each([
  [],
  ["missing"],
  ["setup"],
  ["serve", "--data"],
  ["serve", "--data", "x", "--port", "no"],
  ["serve", "--data", "x", "--unknown", "x"],
])("server_usage_errors_exit_2 %p", async (...argv: string[]) => {
  const w = await command();
  expect(await w.run(argv)).toBe(2);
  expect(w.err.join("")).toContain("usage:");
  await w.database.close();
});
