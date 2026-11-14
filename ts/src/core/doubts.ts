import { Action, type Decision, Raises, ThreadState } from "./model.ts";
import type { Snapshot } from "./snapshot.ts";
import { byCodePoint } from "./text.ts";

export function doubtMarks(
  s: Snapshot,
  changedBy: ReadonlyMap<string, readonly string[]>,
): ReadonlyMap<string, readonly string[]> {
  const openThreads = (kind: Raises) =>
    new Set(
      [...s.threads.values()]
        .filter((t) => t.state === ThreadState.OPEN && t.raises === kind)
        .map((t) => t.about),
    );
  const doubts = openThreads(Raises.DOUBT);
  const questions = openThreads(Raises.QUESTION);
  const marks = new Map<string, string[]>();
  const affected = new Set<string>();
  for (const ident of [...new Set([...s.decisions.keys(), ...s.entries.keys()])].sort(
    byCodePoint,
  )) {
    const local: string[] = [];
    if (doubts.has(ident)) local.push("in doubt");
    if (questions.has(ident)) local.push("question open");
    let changed = false;
    if (s.entries.has(ident)) {
      for (const id of [...doubts].filter((id) => s.decisions.has(id)).sort(byCodePoint)) {
        const d = s.decisions.get(id) as Decision;
        const created = d.changes.some((c) => c.entry === ident && c.action === Action.CREATE);
        if (created || changedBy.get(ident)?.[0] === id) {
          changed = true;
          local.push(`changed by ${id}, in doubt`);
        }
      }
      if (doubts.has(ident) || changed) affected.add(ident);
    }
    if (local.length) marks.set(ident, local);
  }
  for (const ident of [...s.entries.keys()].sort(byCodePoint)) {
    const seen = new Set([ident]);
    const pending = [...(s.entries.get(ident)?.restsOn ?? [])];
    const reached = new Set<string>();
    while (pending.length) {
      const target = pending.pop() as string;
      if (seen.has(target)) continue;
      seen.add(target);
      if (affected.has(target)) reached.add(target);
      pending.push(...(s.entries.get(target)?.restsOn ?? []));
    }
    if (reached.size)
      marks.set(ident, [
        ...(marks.get(ident) ?? []),
        ...[...reached].sort(byCodePoint).map((t) => `rests on ${t}, in doubt`),
      ]);
  }
  return marks;
}
