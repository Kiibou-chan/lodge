import type { Transaction } from "kysely";
import { NotFound, Role } from "#app";
import { ATTACHMENTS, decodeUtf8, type Tree, tree } from "#core";
import type { Tables } from "./schema.ts";
export async function headOf(tx: Transaction<Tables>, project: string): Promise<number> {
  const head = await tx
    .selectFrom("heads")
    .select("rev")
    .where("project", "=", project)
    .executeTakeFirst();
  if (!head) throw new NotFound(`no project named ${project}`);
  return head.rev;
}
export async function touchHead(
  tx: Transaction<Tables>,
  project: string,
  rev?: number,
): Promise<boolean> {
  let query = tx
    .updateTable("heads")
    .set((eb) => ({ rev: eb.ref("rev") }))
    .where("project", "=", project);
  if (rev !== undefined) query = query.where("rev", "=", rev);
  const result = await query.executeTakeFirst();
  return result.numUpdatedRows !== 0n;
}
export async function readTree(tx: Transaction<Tables>, project: string): Promise<Tree> {
  const rev = await headOf(tx, project);
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
  const owners = await tx
    .selectFrom("members")
    .select("person")
    .where("project", "=", project)
    .where("role", "=", Role.OWNER)
    .execute();
  return tree({
    rev: String(rev),
    files,
    attachments,
    people: new Set(owners.map((row) => row.person)),
  });
}
