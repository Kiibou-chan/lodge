import { expect, test } from "bun:test";
import { mkdtempSync, rmSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { sql } from "kysely";
import { LodgeError } from "#app";
import { type LodgeDatabase, openDatabase } from "#store";

test("contended_first_open_enters_wal", async () => {
  const root = mkdtempSync(join(tmpdir(), "lodge-wal-"));
  const path = join(root, "store.sqlite");
  let database: LodgeDatabase | undefined;
  const holder = Bun.spawn(
    [
      process.execPath,
      "-e",
      `
    const { Database } = require("bun:sqlite");
    const db = new Database(process.argv[1], { create: true });
    db.exec("create table fixture(value); begin; select * from fixture");
    process.stdout.write("ready");
    Atomics.wait(new Int32Array(new SharedArrayBuffer(4)), 0, 0, 800);
    db.exec("rollback");
    db.close();
  `,
      path,
    ],
    { stdout: "pipe", stderr: "pipe" },
  );
  try {
    const reader = holder.stdout.getReader();
    expect(new TextDecoder().decode((await reader.read()).value)).toBe("ready");
    reader.releaseLock();
    database = await openDatabase(path);
    expect(
      (await sql<{ journal_mode: string }>`pragma journal_mode`.execute(database.db)).rows,
    ).toEqual([{ journal_mode: "wal" }]);
    expect(await holder.exited).toBe(0);
  } finally {
    holder.kill();
    await holder.exited;
    await database?.close();
    rmSync(root, { recursive: true });
  }
});

test("private_temporary_database_is_refused_when_it_cannot_enter_wal", async () => {
  let database: LodgeDatabase | undefined;
  try {
    const opening = openDatabase("").then((opened) => {
      database = opened;
      return opened;
    });
    await expect(opening).rejects.toBeInstanceOf(LodgeError);
    await expect(opening).rejects.toThrow("the database at  could not enter WAL mode");
  } finally {
    await database?.close();
  }
});
