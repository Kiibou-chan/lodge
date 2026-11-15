import { afterEach, expect, test } from "bun:test";
import type { KyselyPlugin, RootOperationNode } from "kysely";
import { agent, type ExportTarget, NotFound, PublishOutcome, person } from "#app";
import { decodeUtf8, encodeUtf8 } from "#core";
import {
  type LodgeDatabase,
  openDatabase,
  rebuild,
  SqliteExportTargets,
  SqliteProjects,
} from "#store";
import { FixedClock } from "../app/fakes.ts";

const databases: LodgeDatabase[] = [];
afterEach(async () => {
  for (const database of databases.splice(0)) await database.close();
});
const first: ExportTarget = { repository: "/made-up/export", branch: "records", remote: null };
const second: ExportTarget = { repository: "/made-up/other", branch: "archive", remote: "origin" };
async function world() {
  const database = await openDatabase(":memory:");
  databases.push(database);
  const clock = new FixedClock();
  const projects = new SqliteProjects(database, clock);
  await projects.create("work", "ana");
  return { database, projects, clock, targets: new SqliteExportTargets(database, clock) };
}

test("no_target_is_null", async () => {
  const { targets } = await world();
  expect(await targets.target("work")).toBeNull();
});
test("target_set_is_read_back", async () => {
  const { targets, projects } = await world();
  await projects.create("other", "bo");
  await targets.setTarget("work", first, person("ana"));
  expect(await targets.target("work")).toEqual(first);
  expect(await targets.target("other")).toBeNull();
  await targets.setTarget("other", second, person("bo"));
  expect(await targets.target("work")).toEqual(first);
  expect(await targets.target("other")).toEqual(second);
});
test("escaped_path_is_read_back", async () => {
  const { targets } = await world();
  const target = { ...first, repository: "/made-up/\udcff" };
  await targets.setTarget("work", target, person("ana"));
  expect(await targets.target("work")).toEqual(target);
});
test("escaped_byte_in_event_body_is_read_back", async () => {
  const { database, targets } = await world();
  await database.db
    .insertInto("events")
    .values({
      project: "work",
      actor: "ana",
      at: "2026-10-29T09:30:00+01:00",
      kind: "export-target",
      path: null,
      message: null,
      body: encodeUtf8(
        '{"target":{"repository":"/made-up/\udcff","branch":"records","remote":null}}',
      ),
    })
    .execute();
  expect(await targets.target("work")).toEqual({ ...first, repository: "/made-up/\udcff" });
});
test("newest_target_wins", async () => {
  const { targets } = await world();
  await targets.setTarget("work", first, person("ana"));
  await targets.setTarget("work", second, person("ana"));
  expect(await targets.target("work")).toEqual(second);
});
test("null_stops_the_target", async () => {
  const { targets, database } = await world();
  await targets.setTarget("work", first, person("ana"));
  await targets.setTarget("work", null, person("ana"));
  expect(await targets.target("work")).toBeNull();
  const row = await database.db
    .selectFrom("events")
    .selectAll()
    .orderBy("seq", "desc")
    .executeTakeFirstOrThrow();
  expect(decodeUtf8(row.body)).toBe('{"target":null}');
  await rebuild(database);
  expect(await targets.target("work")).toBeNull();
});
test.each([person("ana"), agent("builder")])("target_is_an_event %p", async (by) => {
  const { targets, database, clock } = await world();
  clock.start = { epochMs: Date.UTC(2026, 10, 2, 10), offsetMinutes: 60 };
  await targets.setTarget("work", first, by);
  const events = await database.db.selectFrom("events").selectAll().orderBy("seq").execute();
  expect(events).toHaveLength(3);
  const row = events[2];
  expect(row).toEqual({
    seq: 3,
    project: "work",
    kind: "export-target",
    actor: by.kind === "person" ? "ana" : "agent builder",
    at: "2026-11-02T11:00:00+01:00",
    path: null,
    message: null,
    body: expect.any(Uint8Array),
  });
  expect(Array.from(row?.body ?? [])).toEqual(
    Array.from(encodeUtf8(JSON.stringify({ target: first }))),
  );
  expect(await database.db.selectFrom("heads").selectAll().execute()).toEqual([
    { project: "work", rev: 3 },
  ]);
});
test("rebuild_keeps_the_target", async () => {
  const { targets, database, projects } = await world();
  await targets.setTarget("work", first, person("ana"));
  await targets.setTarget("work", second, person("ana"));
  const before = await projects.storeFor("work", person("ana")).trees();
  for (let i = 0; i < 2; i++) {
    await rebuild(database);
    expect(await targets.target("work")).toEqual(second);
    expect(await projects.storeFor("work", person("ana")).trees()).toEqual(before);
  }
});
test("unknown_project_is_not_found", async () => {
  const { targets, database } = await world();
  const before = await database.db.selectFrom("events").selectAll().execute();
  for (const target of [first, null]) {
    const attempt = targets.setTarget("missing", target, person("ana"));
    await expect(attempt).rejects.toBeInstanceOf(NotFound);
    await expect(attempt).rejects.toThrow("no project named missing");
  }
  expect(await database.db.selectFrom("events").selectAll().execute()).toEqual(before);
  expect(await database.db.selectFrom("heads").selectAll().execute()).toEqual([
    { project: "work", rev: 2 },
  ]);
});
test("target_change_rejects_a_stale_publish", async () => {
  const { targets, projects } = await world();
  const store = projects.storeFor("work", person("ana"));
  const [base] = await store.trees();
  await targets.setTarget("work", first, person("ana"));
  expect(await store.publish(base, new Map(), "stale")).toBe(PublishOutcome.REJECTED);
  const [fresh] = await store.trees();
  expect(await store.publish(fresh, new Map(), "fresh")).toBe(PublishOutcome.PUBLISHED);
  expect(await targets.target("work")).toEqual(first);
});

test("set_target_writes_heads_first", async () => {
  const { database, clock } = await world();
  const statements: RootOperationNode[] = [];
  const plugin: KyselyPlugin = {
    transformQuery({ node }) {
      statements.push(node);
      return node;
    },
    async transformResult({ result }) {
      return result;
    },
  };
  const targets = new SqliteExportTargets(
    { ...database, db: database.db.withPlugin(plugin) },
    clock,
  );
  await targets.setTarget("work", first, person("ana"));
  expect(statements[0]).toMatchObject({
    kind: "UpdateQueryNode",
    table: { table: { identifier: { name: "heads" } } },
  });
});
