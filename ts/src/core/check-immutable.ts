import { problemAt } from "./check-state.ts";
import { isAuthor } from "./derive.ts";
import { type Decision, type Problem, ThreadState } from "./model.ts";
import type { Snapshot } from "./snapshot.ts";
import { byCodePoint } from "./text.ts";

const REMEDY = "; a correction is a new decision that replaces it";
const REASONING_REMEDY = "; a correction or a shorter reasoning is a new decision that replaces it";

function equal(a: unknown, b: unknown): boolean {
  if (a === b) return true;
  if (Array.isArray(a) && Array.isArray(b))
    return a.length === b.length && a.every((v, i) => equal(v, b[i]));
  if (a !== null && b !== null && typeof a === "object" && typeof b === "object")
    return (
      Object.keys(a).length === Object.keys(b).length &&
      Object.entries(a).every(([k, v]) => Object.hasOwn(b, k) && equal(v, Reflect.get(b, k)))
    );
  return false;
}
const FIELDS: readonly (readonly [keyof Decision, string])[] = [
  ["title", "title"],
  ["scope", "scope"],
  ["decidedBy", "decided_by"],
  ["date", "date"],
  ["statement", "statement"],
  ["reasoning", "reasoning"],
  ["code", "code"],
  ["changes", "changes"],
  ["replaces", "replaces"],
  ["narrows", "narrows"],
  ["confirms", "confirms"],
  ["workItem", "work_item"],
  ["quote", "quote"],
  ["numbers", "numbers"],
  ["attachments", "attachments"],
  ["importedFrom", "imported_from"],
];
export function checkImmutable(published: Snapshot, after: Snapshot): Problem[] {
  const problems: Problem[] = [];
  for (const id of [...published.decisions.keys()]
    .filter((id) => after.decisions.has(id))
    .sort(byCodePoint)) {
    const before = published.decisions.get(id) as Decision;
    const now = after.decisions.get(id) as Decision;
    const who = isAuthor(before) ? "author" : "agent";
    for (const [key, name] of FIELDS) {
      if (equal(before[key], now[key])) continue;
      const message =
        name === "reasoning"
          ? `reasoning of a published ${who} decision was changed${REASONING_REMEDY}`
          : `${name} of a published decision was changed${REMEDY}`;
      problems.push(problemAt(after, id, 5, message));
    }
  }
  for (const id of [...published.threads.keys()]
    .filter((id) => after.threads.has(id))
    .sort(byCodePoint)) {
    const old = published.threads.get(id),
      now = after.threads.get(id);
    if (!old || !now) continue;
    const messages: string[] = [];
    for (const name of ["about", "raises", "opened"] as const)
      if (old[name] !== now[name]) messages.push(`${name} of a published thread was changed`);
    if (!equal(now.messages.slice(0, old.messages.length), old.messages))
      messages.push("a published message was changed or removed; messages are only appended");
    if (old.state === ThreadState.CLOSED) {
      if (now.state === ThreadState.OPEN) messages.push("a closed thread was opened again");
      if (now.messages.length > old.messages.length)
        messages.push("a message was added after the thread was closed");
    } else if (now.state === ThreadState.CLOSED && now.messages.length <= old.messages.length)
      messages.push("a thread was closed without a closing message");
    problems.push(...messages.map((m) => problemAt(after, id, 5, m)));
  }
  return problems;
}
