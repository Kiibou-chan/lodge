import {
  type Actor,
  actorText,
  type Clock,
  Conflict,
  LodgeError,
  NotFound,
  PROJECT_NAME,
  type Projects,
  type Role,
  stampOf,
} from "#app";
import { byCodePoint, load } from "#core";
import { appendEvents, json } from "./events.ts";
import { headOf, readTree, touchHead } from "./read-tree.ts";
import type { LodgeDatabase } from "./schema.ts";
import { SqliteStore } from "./sqlite-store.ts";

const PERSON_NAME = { pattern: /^[a-z][a-z0-9-]{0,31}$/u, what: "a person's name" };
function checkName(name: string, rule: { pattern: RegExp; what: string }): void {
  if (!rule.pattern.test(name))
    throw new LodgeError(`${name} is not ${rule.what}: ${rule.pattern.source}`);
}
export class SqliteProjects implements Projects {
  constructor(
    private readonly database: LodgeDatabase,
    private readonly clock: Clock,
  ) {}
  async create(
    project: string,
    owner: string,
    settings: Readonly<Record<string, unknown>> = {},
  ): Promise<void> {
    checkName(project, PROJECT_NAME);
    checkName(owner, PERSON_NAME);
    await this.database.db.transaction().execute(async (tx) => {
      const result = await tx
        .insertInto("heads")
        .values({ project, rev: 0 })
        .onConflict((c) => c.column("project").doNothing())
        .executeTakeFirst();
      if (result.numInsertedOrUpdatedRows === 0n)
        throw new Conflict(`a project named ${project} exists`);
      await appendEvents(tx, project, owner, stampOf(this.clock.now()), [
        { kind: "project", path: null, body: json({ owner, settings }), message: null },
        { kind: "member", path: null, body: json({ person: owner, role: "owner" }), message: null },
      ]);
    });
  }
  async settings(project: string): Promise<Readonly<Record<string, unknown>> | null> {
    const row = await this.database.db
      .selectFrom("project_settings")
      .select("body")
      .where("id", "=", project)
      .executeTakeFirst();
    return row ? JSON.parse(new TextDecoder().decode(row.body)) : null;
  }
  async names(): Promise<readonly string[]> {
    const rows = await this.database.db.selectFrom("heads").select("project").execute();
    return rows.map((row) => row.project).sort(byCodePoint);
  }
  async members(project: string): Promise<ReadonlyMap<string, Role>> {
    return this.database.db.transaction().execute(async (tx) => {
      await headOf(tx, project);
      const rows = await tx
        .selectFrom("members")
        .selectAll()
        .where("project", "=", project)
        .execute();
      return new Map(
        rows
          .sort((a, b) => byCodePoint(a.person, b.person))
          .map((row) => [row.person, row.role as Role]),
      );
    });
  }
  async addMember(project: string, person: string, role: Role, by: Actor): Promise<void> {
    checkName(person, PERSON_NAME);
    await this.database.db.transaction().execute(async (tx) => {
      if (!(await touchHead(tx, project))) throw new NotFound(`no project named ${project}`);
      const member = await tx
        .selectFrom("members")
        .select("person")
        .where("project", "=", project)
        .where("person", "=", person)
        .executeTakeFirst();
      if (member) throw new Conflict(`${person} is a member of ${project}`);
      const snapshot = load(await readTree(tx, project));
      const ids = [...snapshot.decisions.values()]
        .filter((d) => d.decidedBy === person)
        .map((d) => d.id);
      ids.push(
        ...[...snapshot.threads.values()]
          .filter((t) => t.messages.some((m) => m.by === person))
          .map((t) => t.id),
      );
      ids.sort(byCodePoint);
      if (ids.length)
        throw new Conflict(`${person} is a role in ${ids[0]}, so it cannot name a person`);
      await appendEvents(tx, project, actorText(by), stampOf(this.clock.now()), [
        { kind: "member", path: null, body: json({ person, role }), message: null },
      ]);
    });
  }
  storeFor(project: string, actor: Actor): SqliteStore {
    return new SqliteStore(this.database, project, actorText(actor), this.clock);
  }
}
