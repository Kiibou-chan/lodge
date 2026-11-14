import { Database } from "bun:sqlite";
import { afterEach, expect, test } from "bun:test";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { sql } from "kysely";
import { LodgeError } from "#app";
import { type LodgeDatabase, openDatabase, rebuild } from "#store";

const roots: string[] = [];
const databases: LodgeDatabase[] = [];
afterEach(async () => {
  for (const database of databases.splice(0)) await database.close();
  for (const root of roots.splice(0)) rmSync(root, { recursive: true });
});
function path(): string {
  const root = mkdtempSync(join(tmpdir(), "lodge-db-"));
  roots.push(root);
  return join(root, "store.sqlite");
}
async function open(file = ":memory:"): Promise<LodgeDatabase> {
  const database = await openDatabase(file);
  databases.push(database);
  return database;
}
const event = (kind: string, body: number[], project = "storage", path: string | null = null) => ({
  project,
  at: "2026-10-29T09:30:00+01:00",
  actor: "ada",
  kind,
  path,
  body: new Uint8Array(body),
  message: null,
});
test("schema_is_created_once", async () => {
  const file = path();
  const first = await openDatabase(file);
  await first.db
    .insertInto("events")
    .values(event("project", [123, 125]))
    .execute();
  await first.close();
  const second = await open(file);
  expect(
    (await sql<{ user_version: number }>`pragma user_version`.execute(second.db)).rows,
  ).toEqual([{ user_version: 1 }]);
  expect(await second.db.selectFrom("events").selectAll().execute()).toHaveLength(1);
});
test("newer_schema_is_refused", async () => {
  const file = path();
  const raw = new Database(file, { create: true });
  raw.exec("pragma user_version=9");
  raw.close();
  await expect(openDatabase(file)).rejects.toThrow(LodgeError);
  await expect(openDatabase(file)).rejects.toThrow(
    `the database at ${file} has schema 9, newer than this lodge's 1`,
  );
});
test.each(["insert or replace", "replace"])("events_refuse_%s", async (statement) => {
  const { db } = await open();
  await db
    .insertInto("events")
    .values(event("project", [123, 125]))
    .execute();
  await expect(
    sql
      .raw(
        `${statement} into events(seq, project, at, actor, kind, body) values (1, 'storage', 'now', 'bo', 'project', x'7b7d')`,
      )
      .execute(db),
  ).rejects.toThrow("events are append-only");
  expect(await db.selectFrom("events").select("actor").execute()).toEqual([{ actor: "ada" }]);
});
test("events_are_append_only", async () => {
  const { db } = await open();
  await db
    .insertInto("events")
    .values(event("project", [123, 125]))
    .execute();
  await expect(db.updateTable("events").set({ actor: "bo" }).execute()).rejects.toThrow(
    "events are append-only",
  );
  await expect(db.deleteFrom("events").execute()).rejects.toThrow("events are append-only");
});
test("rebuild_derives_the_tables_from_raw_events", async () => {
  const database = await open();
  const { db } = database;
  const member = Array.from(new TextEncoder().encode('{"person":"ada","role":"owner"}'));
  for (const row of [
    event("project", [123, 125]),
    event("member", member),
    event("member", Array.from(new TextEncoder().encode('{"person":"ada","role":"member"}'))),
    event("file", [128], "storage", "a.md"),
    event("file", [239, 187, 191, 255], "storage", "a.md"),
  ]) {
    await db.insertInto("events").values(row).execute();
  }
  for (let i = 0; i < 2; i++) {
    await rebuild(database);
    expect(await db.selectFrom("heads").selectAll().execute()).toEqual([
      { project: "storage", rev: 5 },
    ]);
    expect(await db.selectFrom("members").selectAll().execute()).toEqual([
      { project: "storage", person: "ada", role: "member" },
    ]);
    const files = await db.selectFrom("files").selectAll().execute();
    expect(files).toHaveLength(1);
    expect(files[0]).toEqual({
      project: "storage",
      path: "a.md",
      body: expect.any(Uint8Array),
      seq: 5,
    });
    expect(Array.from(files[0]?.body ?? [])).toEqual([239, 187, 191, 255]);
    expect(await db.selectFrom("events").selectAll().execute()).toHaveLength(5);
  }
});
test("an_event_of_no_project_adds_no_head", async () => {
  const database = await open();
  await database.db
    .insertInto("events")
    .values(event("file", [128], "", "a.md"))
    .execute();
  await rebuild(database);
  expect(await database.db.selectFrom("heads").selectAll().execute()).toEqual([]);
});

test("rebuild_removes_stale_rows", async () => {
  const database = await open();
  const { db } = database;
  await db.insertInto("heads").values({ project: "stale", rev: 9 }).execute();
  await db
    .insertInto("files")
    .values({ project: "stale", path: "a.md", body: new Uint8Array([128]), seq: 9 })
    .execute();
  await db
    .insertInto("members")
    .values({ project: "stale", person: "bo", role: "owner" })
    .execute();
  await rebuild(database);
  expect(await db.selectFrom("heads").selectAll().execute()).toEqual([]);
  expect(await db.selectFrom("files").selectAll().execute()).toEqual([]);
  expect(await db.selectFrom("members").selectAll().execute()).toEqual([]);
});
test("unknown_event_rolls_back_rebuild", async () => {
  const database = await open();
  const { db } = database;
  await db.insertInto("heads").values({ project: "storage", rev: 9 }).execute();
  await db
    .insertInto("files")
    .values({ project: "storage", path: "a.md", body: new Uint8Array([128]), seq: 9 })
    .execute();
  await db
    .insertInto("members")
    .values({ project: "storage", person: "ada", role: "owner" })
    .execute();
  const before = [
    await db.selectFrom("heads").selectAll().execute(),
    await db.selectFrom("files").selectAll().execute(),
    await db.selectFrom("members").selectAll().execute(),
  ];
  await db
    .insertInto("events")
    .values(event("mystery", [123, 125]))
    .execute();
  await expect(rebuild(database)).rejects.toThrow("unknown event kind: mystery");
  expect([
    await db.selectFrom("heads").selectAll().execute(),
    await db.selectFrom("files").selectAll().execute(),
    await db.selectFrom("members").selectAll().execute(),
  ]).toEqual(before);
});
