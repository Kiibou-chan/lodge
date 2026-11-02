import { expect, test } from "bun:test";
import { sql } from "kysely";
import { handler, open } from "../src/server/db.ts";
test("events round trip in sqlite through kysely", async () => {
  const db = open(":memory:");
  await sql`create table events (seq integer primary key autoincrement, kind text not null, body text not null)`.execute(db);
  await db.insertInto("events").values({ kind: "decision", body: "{}" }).execute();
  const rows = await db.selectFrom("events").selectAll().execute();
  expect(rows).toEqual([{ seq: 1, kind: "decision", body: "{}" }]);
  await db.destroy();
});
test("the handler answers without a socket", async () => {
  const res = await handler(new Request("http://lodge.test/api/echo", { method: "POST", body: JSON.stringify({ a: 1 }) }));
  expect(res.status).toBe(200);
  expect(await res.json()).toEqual({ a: 1 });
});
