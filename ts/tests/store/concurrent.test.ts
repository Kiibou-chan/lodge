import { afterEach, expect, test } from "bun:test";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { AddOutcome, PublishOutcome, type Store } from "#app";
import { checkState, load, type Tree } from "#core";
import { type LodgeDatabase, openDatabase, SqliteProjects, SqliteStore } from "#store";
import { CountingIds, FixedClock } from "../app/fakes.ts";
import { wired } from "../app/support.ts";
import { areaText, decisionText, specText } from "../core/applying.ts";
import { Interleaved } from "./interleaving.ts";

const databases: LodgeDatabase[] = [];
const roots: string[] = [];
afterEach(async () => {
  for (const database of databases.splice(0)) await database.close();
  for (const root of roots.splice(0)) rmSync(root, { recursive: true });
});
async function open(path: string) {
  const database = await openDatabase(path);
  databases.push(database);
  return database;
}
function drafts(id: string, body: string): readonly (readonly [string, string])[] {
  return [
    ["d.md", decisionText("changes:", `  - {entry: ${id}, action: create}`)],
    ["s.md", specText(`id: ${id}`, "area: storage", { body })],
  ];
}
async function seeded() {
  const root = mkdtempSync(join(tmpdir(), "lodge-concurrent-"));
  roots.push(root);
  const path = join(root, "store.sqlite");
  const database = await open(path);
  const clock = new FixedClock();
  await new SqliteProjects(database, clock).create("storage", "author");
  const store = new SqliteStore(database, "storage", "author", clock);
  expect(
    (
      await wired(store).add([
        ["area.md", areaText("name: storage")],
        ...drafts("s-bbbbbb", "Initial."),
      ])
    ).outcome,
  ).toBe(AddOutcome.PUBLISHED);
  return { database, path, store, clock };
}
function assertBothPublished(tip: Tree) {
  const state = load(tip);
  for (const id of ["s-bbbbbb", "s-cccccc", "s-dddddd"]) expect(state.entries.has(id)).toBe(true);
  expect(state.decisions.size).toBe(3);
  expect(state.areas.get("storage")?.order).toEqual(["s-bbbbbb", "s-cccccc", "s-dddddd"]);
  expect(checkState(state).ok).toBe(true);
}
async function addInterleaved(a: Store, b: Store) {
  const during = wired(a, new FixedClock(), new CountingIds(20));
  const between = new Interleaved(b, during, drafts("s-cccccc", "First session."));
  expect(
    (
      await wired(between, new FixedClock(), new CountingIds(40)).add(
        drafts("s-dddddd", "Second session."),
      )
    ).outcome,
  ).toBe(AddOutcome.PUBLISHED);
  expect(between.outcomes).toEqual([PublishOutcome.REJECTED, PublishOutcome.PUBLISHED]);
}
test("two_clones_add_at_once", async () => {
  const { path, store, clock } = await seeded();
  const second = new SqliteStore(await open(path), "storage", "author", clock);
  await addInterleaved(store, second);
  const reader = new SqliteStore(await open(path), "storage", "author", clock);
  assertBothPublished((await reader.trees())[0]);
});
test("two_worktrees_of_one_clone_add_interleaved", async () => {
  const { database, store, clock } = await seeded();
  const second = new SqliteStore(database, "storage", "author", clock);
  await addInterleaved(store, second);
  assertBothPublished((await store.trees())[0]);
});
test("stale_tree_publish_rejected_ref_unchanged", async () => {
  const { database, store: a, clock } = await seeded();
  const b = new SqliteStore(database, "storage", "author", clock);
  const [aRead] = await a.trees();
  const [bRead] = await b.trees();
  expect(await a.publish(aRead, new Map([["lodge/attachments/d-aaaaaa/a.txt", "a\n"]]), "a")).toBe(
    PublishOutcome.PUBLISHED,
  );
  const head = () =>
    database.db
      .selectFrom("heads")
      .select("rev")
      .where("project", "=", "storage")
      .executeTakeFirstOrThrow();
  const tip = await head();
  expect(await b.publish(bRead, new Map([["lodge/attachments/d-aaaaaa/b.txt", "b\n"]]), "b")).toBe(
    PublishOutcome.REJECTED,
  );
  expect(await head()).toEqual(tip);
  expect((await a.trees())[0].rev).toBe(String(tip.rev));
});
