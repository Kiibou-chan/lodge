import { expect, test } from "bun:test";
import { rebuild } from "#store";
import { setup } from "./support.ts";

test("create_keeps_the_settings", async () => {
  const { projects } = await setup();
  await projects.create("other", "author", { length: { title_chars: 70 } });
  expect(await projects.settings("other")).toEqual({ length: { title_chars: 70 } });
});
test("create_without_settings_keeps_none", async () => {
  expect(await (await setup()).projects.settings("storage")).toEqual({});
});
test("unknown_project_has_no_settings", async () => {
  expect(await (await setup()).projects.settings("unknown")).toBeNull();
});
test("names_lists_the_projects", async () => {
  const { projects } = await setup();
  await projects.create("aaa", "author");
  expect(await projects.names()).toEqual(["aaa", "storage"]);
});
test("settings_survive_rebuild", async () => {
  const { projects, database } = await setup();
  await projects.create("other", "author", { import: { enabled: true } });
  await rebuild(database);
  expect(await projects.settings("other")).toEqual({ import: { enabled: true } });
});
