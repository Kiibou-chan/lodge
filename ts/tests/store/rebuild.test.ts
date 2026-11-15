import { expect, test } from "bun:test";
import { person, Role } from "#app";
import { rebuild } from "#store";
import { events, setup } from "./support.ts";

async function populated() {
  const context = await setup();
  await context.projects.addMember("storage", "bo", Role.MEMBER, person("author"));
  for (const writes of [
    new Map([
      ["lodge/a", "first"],
      ["lodge/b", "b"],
    ]),
    new Map([["lodge/a", "second"]]),
    new Map([["lodge/c", "c"]]),
  ])
    await context.store.publish((await context.store.trees())[0], writes, "write");
  return context;
}
test("rebuild_gives_the_same_tables", async () => {
  const { database } = await populated();
  async function rows() {
    return Promise.all([
      database.db.selectFrom("heads").selectAll().orderBy("project").execute(),
      database.db.selectFrom("files").selectAll().orderBy("path").execute(),
      database.db.selectFrom("members").selectAll().orderBy("person").execute(),
    ]);
  }
  const before = await rows();
  await rebuild(database);
  expect(await rows()).toEqual(before);
});
test("rebuild_keeps_every_event", async () => {
  const { database } = await populated();
  const before = await events(database);
  await rebuild(database);
  expect(await events(database)).toEqual(before);
});
