import {
  type Clock,
  CommitOutcome,
  committed,
  gate,
  type Held,
  type HeldDraft,
  LodgeError,
  NotFound,
  PublishOutcome,
  type Store,
  stampOf,
} from "#app";
import { ATTACHMENTS, decodeUtf8, encodeUtf8, type Tree, ValueError } from "#core";
import { appendEvents, json } from "./events.ts";
import { openHold, readTree, touchHead } from "./read-tree.ts";
import type { LodgeDatabase } from "./schema.ts";
export class SqliteStore implements Store {
  constructor(
    private readonly database: LodgeDatabase,
    private readonly project: string,
    private readonly actor: string,
    private readonly clock: Clock,
  ) {}
  async hold(held: HeldDraft): Promise<number> {
    return this.database.db.transaction().execute(async (tx) => {
      if (!(await touchHead(tx, this.project)))
        throw new NotFound(`no project named ${this.project}`);
      return appendEvents(tx, this.project, this.actor, stampOf(this.clock.now()), [
        { kind: "held", path: null, body: json(held), message: null },
      ]);
    });
  }
  async held(): Promise<readonly Held[]> {
    const rows = await this.database.db
      .selectFrom("held")
      .selectAll()
      .where("project", "=", this.project)
      .where("state", "=", "open")
      .orderBy("seq", "asc")
      .execute();
    return rows.map((row) => ({
      ...(JSON.parse(decodeUtf8(row.body)) as HeldDraft),
      seq: row.seq,
      at: row.at,
    }));
  }
  async decline(seq: number, reason: string): Promise<void> {
    await this.database.db.transaction().execute(async (tx) => {
      if (!(await touchHead(tx, this.project)))
        throw new NotFound(`no project named ${this.project}`);
      const held = await openHold(tx, this.project, seq);
      if (!held) throw new NotFound(`nothing is held under number ${seq}`);
      await appendEvents(tx, this.project, this.actor, stampOf(this.clock.now()), [
        { kind: "declined", path: null, body: json({ held: seq, reason }), message: null },
      ]);
    });
  }
  async trees(): Promise<readonly [Tree, Tree]> {
    return this.database.db.transaction().execute(async (tx) => {
      const current = await readTree(tx, this.project);
      return [current, current] as const;
    });
  }
  async attachmentTexts(): Promise<ReadonlyMap<string, string>> {
    const rows = await this.database.db
      .selectFrom("files")
      .selectAll()
      .where("project", "=", this.project)
      .where("path", ">=", ATTACHMENTS)
      .where("path", "<", "lodge/attachments0")
      .execute();
    return new Map(rows.map((row) => [row.path, decodeUtf8(row.body)]));
  }
  async freshness() {
    return null;
  }
  async gate(current: Tree) {
    return gate({ published: current, checked: [["", current]] });
  }
  async commit(_paths: readonly string[], _message: string) {
    return committed({
      outcome: CommitOutcome.FAILED,
      detail: "the server keeps no checkout; its writes are published at once",
    });
  }
  async publish(
    base: Tree,
    writes: ReadonlyMap<string, string>,
    message: string,
    approves: number | null = null,
  ): Promise<PublishOutcome> {
    const events: { kind: string; path: string; body: Uint8Array; message: string }[] = [];
    for (const path of writes.keys()) {
      const parts = path.split("/");
      if (
        parts[0] !== "lodge" ||
        parts.length < 2 ||
        path.includes("\\") ||
        path.includes("\0") ||
        parts.some((part) => ["", ".", "..", ".git"].includes(part))
      )
        throw new LodgeError(`${path} is outside lodge/, which is all the store writes`);
      if (base.attachments.has(path))
        throw new LodgeError(`${path} is an attachment, and lodge never overwrites an attachment`);
    }
    for (const path of writes.keys()) {
      if (/\p{Cs}/u.test(path))
        throw new LodgeError(`${path}: a path holding a lone surrogate cannot be stored`);
    }
    for (const [path, text] of writes) {
      if (
        path.startsWith("lodge/decisions/") &&
        base.files.has(path) &&
        base.files.get(path) !== text
      )
        throw new LodgeError(
          `${path} is a published decision, and lodge never rewrites a decision`,
        );
    }
    for (const [path, text] of writes) {
      try {
        events.push({ kind: "file", path, body: encodeUtf8(text), message });
      } catch (error) {
        if (!(error instanceof ValueError)) throw error;
        throw new LodgeError(`${path}: ${error.message}`);
      }
    }
    return this.database.db.transaction().execute(async (tx) => {
      if (!(await touchHead(tx, this.project, Number(base.rev)))) return PublishOutcome.REJECTED;
      if (approves !== null) {
        const held = await openHold(tx, this.project, approves);
        if (!held) return PublishOutcome.REJECTED;
      }
      const at = stampOf(this.clock.now());
      await appendEvents(tx, this.project, this.actor, at, events);
      if (approves !== null)
        await appendEvents(tx, this.project, this.actor, at, [
          { kind: "approved", path: null, body: json({ held: approves }), message: null },
        ]);
      return PublishOutcome.PUBLISHED;
    });
  }
}
