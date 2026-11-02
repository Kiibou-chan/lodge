import { newDecisions, problemAt } from "./check-state.ts";
import { derive } from "./derive.ts";
import { Action, type Problem, type SpecEntry } from "./model.ts";
import type { CoreSettings } from "./settings.ts";
import type { Snapshot } from "./snapshot.ts";
import { byCodePoint } from "./text.ts";

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
function onlyRestsOnDiffers(before: SpecEntry | undefined, entry: SpecEntry): boolean {
  return before !== undefined && equal({ ...before, restsOn: entry.restsOn }, entry);
}
export function* checkEntries(
  published: Snapshot,
  after: Snapshot,
  settings: CoreSettings,
): Generator<Problem> {
  const added = newDecisions(published, after);
  const listed = new Set(added.flatMap((d) => d.changes.map((c) => `${c.entry}:${c.action}`)));
  const was = derive(published).status,
    now = derive(after).status;
  for (const id of [...after.entries.keys()].sort(byCodePoint)) {
    const entry = after.entries.get(id) as SpecEntry,
      before = published.entries.get(id);
    const wanted: [Action, string][] = [];
    if (before === undefined) wanted.push([Action.CREATE, "created"]);
    else if (!equal(before, entry)) wanted.push([Action.EDIT, "edited"]);
    if (now.get(id) === "retired" && was.get(id) !== "retired")
      wanted.push([Action.RETIRE, "retired"]);
    const exempt = before === undefined && entry.importedFrom !== null;
    const linksOnly = onlyRestsOnDiffers(before, entry);
    for (const [action, verb] of wanted) {
      const linked = linksOnly && action === Action.EDIT && listed.has(`${id}:${Action.LINK}`);
      if (!exempt && !linked && !listed.has(`${id}:${action}`)) {
        const label = linksOnly && action === Action.EDIT ? "edit or link" : action;
        yield problemAt(
          after,
          id,
          4,
          `${verb}, but no new decision in this change lists it with action ${label}; list it in the decision's changes`,
        );
      }
    }
  }
  for (const d of added) {
    const seen = new Set<string>();
    for (const change of d.changes) {
      const key = `${change.entry}:${change.action}`;
      if (seen.has(key)) continue;
      seen.add(key);
      if (change.action === Action.LINK && after.entries.has(change.entry)) {
        if (
          added.some(
            (other) =>
              other.id !== d.id &&
              other.changes.some(
                (c) =>
                  c.entry === change.entry &&
                  (c.action === Action.EDIT || c.action === Action.CREATE),
              ),
          )
        )
          continue;
        const before = published.entries.get(change.entry),
          entry = after.entries.get(change.entry) as SpecEntry;
        let reason = "";
        if (before === undefined)
          reason = "is new; list it with action create in another decision of this change";
        else if (!onlyRestsOnDiffers(before, entry))
          reason =
            "changes more than rests_on; list it with action edit in another decision of this change";
        if (reason)
          yield problemAt(after, d.id, 4, `lists link for ${change.entry}, which ${reason}`);
      }
      if (change.action === Action.CREATE && published.entries.has(change.entry))
        yield problemAt(after, d.id, 4, `lists create for ${change.entry}, which already exists`);
    }
  }
  const records = [
    ...added,
    ...[...after.entries.keys()]
      .sort(byCodePoint)
      .filter((id) => !published.entries.has(id))
      .map((id) => after.entries.get(id) as SpecEntry),
  ];
  for (const record of records) {
    const source = record.importedFrom;
    if (source !== null && !settings.importSources.includes(source.file))
      yield problemAt(
        after,
        record.id,
        4,
        `imported from ${source.file}, which is not listed in [import] sources`,
      );
  }
}
