import { expect, test } from "bun:test";
import { issueToken } from "#api";
import { world } from "./world.ts";

async function creating(setUp = true, project = "new") {
  const w = await world(setUp);
  const t = await issueToken(w.options, project, "create", null);
  return {
    ...w,
    create: (settings: unknown = {}) =>
      w.fetch(w.request("project-create", { project, settings }, t.secret)),
    secret: t.secret,
  };
}
test("project_create_records_the_settings", async () => {
  const w = await creating();
  const settings = { length: { title_chars: 80 }, import: { sources: ["archive"] } };
  const r = await w.create(settings);
  expect(r.status).toBe(200);
  expect(await r.json()).toEqual({ result: { project: "new" } });
  expect(await w.projects.settings("new")).toEqual(settings);
  expect((await w.fetch(w.request("search", { project: "new" }, w.secret))).status).toBe(200);
  await w.database.close();
});
test.each([
  [{ length: { title_chars: 0 } }, "length.title_chars must be a positive whole number"],
  [{ store: { mode: "tree" } }, "unknown section [store]"],
  [{ stray: 1 }, "unknown key stray"],
])("project_create_checks_the_settings %p", async (settings, message) => {
  const w = await creating();
  const r = await w.create(settings);
  expect(r.status).toBe(400);
  expect(await r.json()).toEqual({ error: { kind: "usage", message: `settings: ${message}` } });
  expect(await w.projects.settings("new")).toBeNull();
  await w.database.close();
});
test("project_create_twice_is_already_initialised", async () => {
  const w = await creating();
  await w.create();
  const r = await w.create();
  expect(r.status).toBe(400);
  expect(await r.json()).toEqual({
    error: { kind: "usage", message: "lodge is already initialised: project new exists" },
  });
  await w.database.close();
});
test("project_name_is_checked", async () => {
  const w = await creating(true, "Bad");
  const r = await w.create();
  expect(r.status).toBe(400);
  expect(await r.json()).toMatchObject({
    error: { message: expect.stringContaining("Bad is not a project name") },
  });
  await w.database.close();
});
test("project_create_makes_the_person_owner", async () => {
  const w = await creating();
  await w.create();
  expect(await w.projects.members("new")).toEqual(new Map([["ada", "owner"]]));
  await w.database.close();
});
test("project_create_before_setup_is_usage", async () => {
  const w = await creating(false);
  const r = await w.create();
  expect(r.status).toBe(400);
  expect(await r.json()).toEqual({
    error: { kind: "usage", message: "the server is not set up; run lodge server setup" },
  });
  await w.database.close();
});
