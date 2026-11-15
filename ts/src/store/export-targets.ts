import {
  type Actor,
  actorText,
  type Clock,
  type ExportTarget,
  type ExportTargets,
  NotFound,
  stampOf,
} from "#app";
import { decodeUtf8, encodeUtf8 } from "#core";
import { appendEvents } from "./events.ts";
import { touchHead } from "./read-tree.ts";
import type { LodgeDatabase } from "./schema.ts";

export class SqliteExportTargets implements ExportTargets {
  constructor(
    private readonly database: LodgeDatabase,
    private readonly clock: Clock,
  ) {}

  async target(project: string): Promise<ExportTarget | null> {
    const row = await this.database.db
      .selectFrom("events")
      .select("body")
      .where("project", "=", project)
      .where("kind", "=", "export-target")
      .orderBy("seq", "desc")
      .executeTakeFirst();
    if (!row) return null;
    return (JSON.parse(decodeUtf8(row.body)) as { target: ExportTarget | null }).target;
  }

  async setTarget(project: string, target: ExportTarget | null, by: Actor): Promise<void> {
    await this.database.db.transaction().execute(async (tx) => {
      if (!(await touchHead(tx, project))) throw new NotFound(`no project named ${project}`);
      await appendEvents(tx, project, actorText(by), stampOf(this.clock.now()), [
        {
          kind: "export-target",
          path: null,
          body: encodeUtf8(JSON.stringify({ target })),
          message: null,
        },
      ]);
    });
  }
}
