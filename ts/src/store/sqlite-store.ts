import {
  type Clock,
  CommitOutcome,
  committed,
  gate,
  LodgeError,
  PublishOutcome,
  type Store,
  stampOf,
} from "#app";
import { ATTACHMENTS, decodeUtf8, encodeUtf8, type Tree, ValueError } from "#core";
import { appendEvents } from "./events.ts";
import { readTree } from "./read-tree.ts";
import type { LodgeDatabase } from "./schema.ts";
export class SqliteStore implements Store {
  constructor(
    private readonly database: LodgeDatabase,
    private readonly project: string,
    private readonly actor: string,
    private readonly clock: Clock,
  ) {}
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
      .execute();
    return new Map(
      rows
        .filter((row) => row.path.startsWith(ATTACHMENTS))
        .map((row) => [row.path, decodeUtf8(row.body)]),
    );
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
  ): Promise<PublishOutcome> {
    const events: { kind: string; path: string; body: Uint8Array; message: string }[] = [];
    for (const [path, text] of writes) {
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
      if (/\p{Cs}/u.test(path))
        throw new LodgeError(`${path}: a path holding a lone surrogate cannot be stored`);
      if (
        path.startsWith("lodge/decisions/") &&
        base.files.has(path) &&
        base.files.get(path) !== text
      )
        throw new LodgeError(
          `${path} is a published decision, and lodge never rewrites a decision`,
        );
      try {
        events.push({ kind: "file", path, body: encodeUtf8(text), message });
      } catch (error) {
        if (!(error instanceof ValueError)) throw error;
        throw new LodgeError(`${path}: ${error.message}`);
      }
    }
    if (base.rev === null || !/^[0-9]+$/u.test(base.rev)) return PublishOutcome.REJECTED;
    return this.database.db.transaction().execute(async (tx) => {
      const result = await tx
        .updateTable("heads")
        .set((eb) => ({ rev: eb.ref("rev") }))
        .where("project", "=", this.project)
        .where("rev", "=", Number(base.rev))
        .executeTakeFirst();
      if (result.numUpdatedRows === 0n) return PublishOutcome.REJECTED;
      await appendEvents(tx, this.project, this.actor, stampOf(this.clock.now()), events);
      return PublishOutcome.PUBLISHED;
    });
  }
}
