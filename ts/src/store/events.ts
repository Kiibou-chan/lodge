import type { Selectable, Transaction } from "kysely";
import { decodeUtf8, encodeUtf8 } from "#core";
import type { LodgeDatabase, Tables } from "./schema.ts";

interface NewEvent {
  readonly kind: string;
  readonly path: string | null;
  readonly body: Uint8Array;
  readonly message: string | null;
}
export function json(value: unknown): Uint8Array {
  return encodeUtf8(JSON.stringify(value));
}
export async function appendEvents(
  tx: Transaction<Tables>,
  project: string,
  actor: string,
  at: string,
  events: readonly NewEvent[],
): Promise<number> {
  let seq = 0;
  for (const event of events) {
    const row = await tx
      .insertInto("events")
      .values({
        ...event,
        message: event.message === null ? null : encodeUtf8(event.message),
        project,
        actor,
        at,
      })
      .returningAll()
      .executeTakeFirstOrThrow();
    await applyEvent(tx, row);
    seq = row.seq;
  }
  return seq;
}
async function applyEvent(
  tx: Transaction<Tables>,
  row: Selectable<Tables["events"]>,
): Promise<void> {
  const { project, seq } = row;
  switch (row.kind) {
    case "project":
      await tx
        .insertInto("heads")
        .values({ project, rev: seq })
        .onConflict((c) => c.column("project").doUpdateSet({ rev: seq }))
        .execute();
      break;
    case "member": {
      const { person, role } = JSON.parse(decodeUtf8(row.body)) as { person: string; role: string };
      await tx
        .insertInto("members")
        .values({ project, person, role })
        .onConflict((c) => c.columns(["project", "person"]).doUpdateSet({ role }))
        .execute();
      break;
    }
    case "file":
      if (row.path === null) throw new Error("a file event needs a path");
      await tx
        .insertInto("files")
        .values({ project, path: row.path, body: row.body, seq })
        .onConflict((c) => c.columns(["project", "path"]).doUpdateSet({ body: row.body, seq }))
        .execute();
      break;
    case "held": {
      const { person } = JSON.parse(decodeUtf8(row.body)) as { person: string };
      await tx
        .insertInto("held")
        .values({ seq, project, person, at: row.at, body: row.body, state: "open" })
        .execute();
      break;
    }
    case "approved":
    case "declined": {
      const { held } = JSON.parse(decodeUtf8(row.body)) as { held: number };
      const result = await tx
        .updateTable("held")
        .set({ state: row.kind })
        .where("seq", "=", held)
        .where("project", "=", project)
        .where("state", "=", "open")
        .executeTakeFirst();
      if (result.numUpdatedRows !== 1n) throw new Error(`nothing is held under number ${held}`);
      break;
    }
    default:
      throw new Error(`unknown event kind: ${row.kind}`);
  }
  if (row.kind !== "project")
    await tx.updateTable("heads").set({ rev: seq }).where("project", "=", project).execute();
}
export async function rebuild(database: LodgeDatabase): Promise<void> {
  await database.db.transaction().execute(async (tx) => {
    await tx.deleteFrom("held").execute();
    await tx.deleteFrom("heads").execute();
    await tx.deleteFrom("files").execute();
    await tx.deleteFrom("members").execute();
    const events = await tx.selectFrom("events").selectAll().orderBy("seq", "asc").execute();
    for (const event of events) await applyEvent(tx, event);
  });
}
