// Probe B: BLOB columns keep bytes exactly; where does TEXT lose the BOM?
import { sql } from "kysely";
import { open } from "./db.ts";
interface DB { t: { k: string; v: Uint8Array } }
const { db, raw } = open<DB>(":memory:");
await sql`create table t (k text, v blob)`.execute(db);
const bytes = new Uint8Array([0xef, 0xbb, 0xbf, 0x61, 0x80, 0xff, 0x00, 0x0d, 0x0a]);
await db.insertInto("t").values({ k: "b", v: bytes }).execute();
const row = await db.selectFrom("t").selectAll().executeTakeFirstOrThrow();
console.log("blob type", row.v?.constructor?.name, "same", Buffer.compare(Buffer.from(row.v), Buffer.from(bytes)) === 0);
raw.exec("create table u (v text)");
raw.prepare("insert into u values (?)").run("﻿a");
console.log("raw text bom kept on read:", (raw.prepare("select v, hex(v) as h from u").get() as { v: string; h: string }).v.length === 2,
  (raw.prepare("select hex(v) as h from u").get() as { h: string }).h);
