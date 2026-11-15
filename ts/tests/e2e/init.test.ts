import { expect, test } from "bun:test";
import { project } from "./project.ts";

test("init", async () => {
  const p = await project();
  expect(await p.run("init")).toEqual({
    code: 0,
    err: "",
    out: `created project work on ${p.url}\nnext: lodge guide\n`,
  });
  expect(await p.paths()).toEqual([]);
});
test("init_twice_is_refused", async () => {
  const p = await project();
  await p.run("init");
  expect(await p.run("init")).toEqual({
    code: 2,
    out: "",
    err: "lodge: lodge is already initialised: project work exists\n",
  });
});
test("init_when_the_server_cannot_be_reached", async () => {
  const p = await project({ unreachable: true });
  const r = await p.run("init");
  expect([r.code, r.out]).toEqual([2, ""]);
  expect(r.err.startsWith(`lodge: cannot reach ${p.url}: `)).toBe(true);
  expect(r.err.split("\n")).toHaveLength(2);
});
