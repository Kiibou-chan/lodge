import type { Snapshot } from "#core";
import { LodgeError } from "./errors.ts";
import type { Actor } from "./ports.ts";

export function awaitsPerson(before: Snapshot, after: Snapshot, actor: Actor): string | null {
  const people = new Set<string>();
  for (const [id, decision] of after.decisions) {
    if (
      !before.decisions.has(id) &&
      after.people.has(decision.decidedBy) &&
      !(actor.kind === "person" && actor.name === decision.decidedBy)
    )
      people.add(decision.decidedBy);
  }
  if (people.size > 1)
    throw new LodgeError(
      "an add holds the decisions of one person at a time; split the drafts by person",
    );
  return [...people][0] ?? null;
}
