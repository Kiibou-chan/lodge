import { expect, test } from "bun:test";
import { join } from "node:path";
import { version } from "../../package.json";
import { project } from "./project.ts";

const COMMANDS = [
  "hook",
  "init",
  "id",
  "search",
  "show",
  "draft",
  "add",
  "check",
  "spec",
  "waiting",
  "guide",
  "threads",
  "thread",
  "ask",
  "reply",
  "close",
];
test("help_lists_every_command", async () => {
  const p = await project();
  const r = await p.run("--help");
  expect([r.code, r.err]).toEqual([0, ""]);
  for (const name of COMMANDS)
    expect(r.out.split("\n").some((l) => l.trim().split(/\s+/u)[0] === name)).toBe(true);
});
test.each(COMMANDS.map((c) => [c]))("every_command_has_help %p", async (name) => {
  const r = await (await project()).run(name, "--help");
  expect(r.code).toBe(0);
  expect(r.out.startsWith(`usage: lodge ${name}`)).toBe(true);
});
test("no_command_is_a_usage_error", async () => {
  const r = await (await project()).run();
  expect(r.code).toBe(2);
  expect(r.err).toContain("usage:");
});
test("version_works_anywhere", async () => {
  const p = await project();
  expect((await p.runIn(join(p.root, ".."), "--version")).out).toBe(`lodge ${version}\n`);
});
