// Probe D: two connections on one file (WAL). A read-then-write transaction that another
// connection's commit overtakes, against a compare-and-set whose first statement writes.
import { mkdtempSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { sql } from "kysely";
import { open } from "./db.ts";
interface DB { heads: { project: string; rev: number }; e: { seq: number; project: string } }
const file = join(mkdtempSync(join(tmpdir(), "p4-")), "db.sqlite");
const a = open<DB>(file), b = open<DB>(file);
for (const c of [a, b]) { c.raw.exec("PRAGMA journal_mode=WAL"); c.raw.exec("PRAGMA busy_timeout=2000"); }
await sql`create table heads (project text primary key, rev integer not null)`.execute(a.db);
await sql`create table e (seq integer primary key autoincrement, project text not null)`.execute(a.db);
await a.db.insertInto("heads").values({ project: "p", rev: 0 }).execute();
// 1: read inside a deferred transaction, the other connection commits, then write
try {
  await a.db.transaction().execute(async (tx) => {
    await tx.selectFrom("heads").selectAll().execute();
    await b.db.insertInto("e").values({ project: "p" } as never).execute();
    await tx.insertInto("e").values({ project: "p" } as never).execute();
  });
  console.log("read-then-write: committed");
} catch (e) { console.log("read-then-write:", (e as Error).message); }
// 2: compare-and-set as the first statement, base read before the other commit
const base = (await a.db.selectFrom("heads").select("rev").where("project", "=", "p").executeTakeFirstOrThrow()).rev;
await b.db.updateTable("heads").set({ rev: base + 1 }).where("project", "=", "p").execute();
const moved = await a.db.transaction().execute(async (tx) => {
  const r = await tx.updateTable("heads").set({ rev: base + 1 }).where("project", "=", "p").where("rev", "=", base).executeTakeFirst();
  return Number(r.numUpdatedRows);
});
console.log("compare-and-set on a stale base updated rows:", moved);
