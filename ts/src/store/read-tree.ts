import type { Transaction } from "kysely";
import { NotFound } from "#app";
import { ATTACHMENTS, decodeUtf8, type Tree, tree } from "#core";
import type { Tables } from "./schema.ts";
export async function readTree(tx: Transaction<Tables>, project: string): Promise<Tree> {
  const head = await tx
    .selectFrom("heads")
    .select("rev")
    .where("project", "=", project)
    .executeTakeFirst();
  if (!head) throw new NotFound(`no project named ${project}`);
  const rows = await tx
    .selectFrom("files")
    .selectAll()
    .where("project", "=", project)
    .orderBy("path", "asc")
    .execute();
  const files = new Map<string, string>(),
    attachments = new Set<string>();
  for (const row of rows) {
    if (row.path.startsWith(ATTACHMENTS)) attachments.add(row.path);
    else files.set(row.path, decodeUtf8(row.body));
  }
  return tree({ rev: String(head.rev), files, attachments });
}
