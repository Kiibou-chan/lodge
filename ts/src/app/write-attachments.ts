import { byCodePoint, type Decision, type Draft, pyRepr } from "#core";
import { LodgeError } from "./errors.ts";

export function attached(
  attachments: readonly (readonly [string, string])[],
  drafts: readonly Draft[],
): ReadonlyMap<string, string> {
  const named = new Map<string, string>();
  if (!attachments.length) return named;
  const created = drafts.filter((d) => d.kind === "decision" && !d.header.has("id")).length;
  if (created !== 1)
    throw new LodgeError(`--attach needs the add to create one decision, not ${created}`);
  for (const [name, text] of attachments) {
    if (["", ".", "..", ".git"].includes(name) || [...name].some((c) => "/\\\0".includes(c)))
      throw new LodgeError(`${pyRepr(name)} is not a plain file name`);
    if (named.has(name)) throw new LodgeError(`${name} is attached twice`);
    named.set(name, text);
  }
  return named;
}
export function requireListed(decision: Decision, attached: ReadonlyMap<string, string>): void {
  const listed = [...new Set(decision.attachments)].sort(byCodePoint),
    wanted = [...attached.keys()].sort(byCodePoint);
  if (JSON.stringify(listed) !== JSON.stringify(wanted))
    throw new LodgeError(
      `the new decision lists [${listed.join(", ")}] in attachments, but the attached files are [${wanted.join(", ")}]; list exactly the attached names`,
    );
}
