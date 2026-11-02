import { type Add, areaFiles, refuse } from "./apply-state.ts";
import { type Draft, recordFromDraft } from "./drafts.ts";
import { ValueError } from "./errors.ts";
import { areaPath, contentHash, newRecordPath, writeRecord } from "./fileformat.ts";
import { isId } from "./ids.ts";
import { Action, type Problem, problem, type Record } from "./model.ts";
import type { Snapshot, Tree } from "./snapshot.ts";
import { byCodePoint } from "./text.ts";
import { valueRepr } from "./value-repr.ts";

export interface StaleBase extends Problem {
  readonly stale: true;
}
export interface Applied {
  readonly files: ReadonlyMap<string, string>;
  readonly ids: readonly string[];
}
export function applyDrafts(
  current: Snapshot,
  tree: Tree,
  drafts: readonly Draft[],
  newDecisionIds: readonly string[],
  date: string,
  importing: boolean,
): Applied | Problem[] {
  const newDrafts = drafts.filter((d) => d.kind === "decision" && !d.header.has("id"));
  if (newDrafts.length !== newDecisionIds.length)
    throw new ValueError(
      `${newDrafts.length} new decision drafts but ${newDecisionIds.length} IDs were given`,
    );
  const names = new Set(
    drafts
      .filter((d) => d.kind === "area")
      .map((d) => d.header.get("name"))
      .filter((name): name is string => typeof name === "string"),
  );
  const add: Add = {
    current,
    tree,
    date,
    importing,
    newIds: [...newDecisionIds].sort(byCodePoint),
    draftedAreas: names,
    files: new Map(),
    ids: [],
    areas: new Map(),
    newEntries: [],
    retired: new Set(),
  };
  const problems: Problem[] = [];
  for (const draft of drafts) {
    const found =
      draft.kind === "decision"
        ? decision(add, draft)
        : draft.kind === "spec"
          ? entry(add, draft)
          : area(add, draft);
    if (found !== null) problems.push(found);
  }
  problems.push(...areaFiles(add));
  return problems.length ? problems : { files: add.files, ids: add.ids };
}
function decision(add: Add, draft: Draft): Problem | null {
  const given = draft.header.get("id") ?? null;
  let path: string | null, id: string, date: string | null;
  if (given === null) {
    if (draft.header.has("base"))
      return refuse(
        draft,
        "base is for edits, but this draft has no id and would add a new decision; keep the id that lodge draft printed to edit one",
      );
    if (draft.header.has("imported_from") && !add.importing) return refuse(draft, NEEDS_FLAG);
    path = null;
    id = add.newIds.shift() as string;
    date = add.date;
  } else {
    if (typeof given !== "string" || !hasId(given, "d")) return refuse(draft, notAnId(given, "d"));
    if (!add.current.decisions.has(given))
      return refuse(
        draft,
        `the decision ${given} does not exist; a new decision draft carries no id`,
      );
    path = add.current.paths.get(given) as string;
    id = given;
    date = null;
    const found = stale(add, draft, path, given);
    if (found !== null) return found;
  }
  const record = recordFromDraft(draft, id, date, null);
  if (record.kind !== "decision")
    return record.kind === "problem" ? record : refuse(draft, "this is not a decision");
  if (path !== null) {
    const existing = add.current.decisions.get(record.id);
    if (!sameOrigin(record.importedFrom, existing?.importedFrom ?? null) && !add.importing)
      return refuse(draft, originChanged(record.id));
  } else {
    for (const change of record.changes)
      if (change.action === Action.RETIRE) add.retired.add(change.entry);
  }
  return keep(add, draft, record, path ?? newRecordPath(record));
}
function entry(add: Add, draft: Draft): Problem | null {
  const given = draft.header.get("id") ?? null;
  if (given === null)
    return refuse(draft, "a specification draft needs an id; lodge id s gives one");
  if (typeof given !== "string" || !hasId(given, "s")) return refuse(draft, notAnId(given, "s"));
  const existing = add.current.entries.get(given);
  let area = draft.header.get("area") ?? null;
  let path: string | null;
  if (existing !== undefined) {
    if (area !== null && area !== existing.area)
      return refuse(
        draft,
        `area ${display(area)} differs from ${existing.area}; entries do not move areas`,
      );
    path = add.current.paths.get(given) as string;
    const found = stale(add, draft, path, given);
    if (found !== null) return found;
    area = existing.area;
  } else {
    path = null;
    if (draft.header.has("base"))
      return refuse(draft, `base is for edits, but no entry ${given} exists to edit`);
    if (draft.header.has("imported_from") && !add.importing) return refuse(draft, NEEDS_FLAG);
    if (area === null) return refuse(draft, "a new specification draft needs an area key");
    if (typeof area !== "string")
      return refuse(draft, `area must be one name, not ${valueRepr(area)}`);
    if (!add.current.areas.has(area) && !add.draftedAreas.has(area))
      return refuse(draft, `area ${area} does not exist; add an area draft for it in the same add`);
  }
  const record = recordFromDraft(draft, given, null, String(area));
  if (record.kind !== "spec")
    return record.kind === "problem" ? record : refuse(draft, "this is not an entry");
  if (
    existing !== undefined &&
    !sameOrigin(record.importedFrom, existing.importedFrom) &&
    !add.importing
  )
    return refuse(draft, originChanged(record.id));
  if (existing === undefined) add.newEntries.push(record);
  return keep(add, draft, record, path ?? newRecordPath(record));
}
function area(add: Add, draft: Draft): Problem | null {
  const record = recordFromDraft(draft, "", null, null);
  if (record.kind !== "area")
    return record.kind === "problem" ? record : refuse(draft, "this is not an area");
  const path = areaPath(record.name);
  if (!add.current.areas.has(record.name)) {
    if (draft.header.has("base"))
      return refuse(draft, `base is for edits, but no area ${record.name} exists to edit`);
  } else {
    const found = stale(add, draft, path, `area:${record.name}`);
    if (found !== null) return found;
  }
  if (add.areas.has(record.name))
    return refuse(draft, `another draft of this add is for the area ${record.name}`);
  add.areas.set(record.name, record);
  return null;
}
function keep(add: Add, draft: Draft, record: Record, path: string): Problem | null {
  if (add.ids.includes(record.id))
    return refuse(draft, `another draft of this add is for ${record.id}`);
  try {
    add.files.set(path, writeRecord(record));
  } catch (error) {
    if (!(error instanceof ValueError)) throw error;
    return refuse(draft, error.message);
  }
  add.ids.push(record.id);
  return null;
}
function stale(add: Add, draft: Draft, path: string, ref: string): Problem | null {
  const base = draft.header.get("base") ?? null;
  if (base === null)
    return refuse(draft, `an edit draft needs a base key; print the draft with lodge draft ${ref}`);
  const text = add.tree.files.get(path);
  const actual = text === undefined ? "(the file is missing)" : contentHash(text);
  if (base === actual) return null;
  const message = `the base ${display(base)} differs from ${actual}, the hash of ${path} now; it changed since the draft was made, so print it again with lodge draft ${ref}, make the change on that print, and add it`;
  const found: StaleBase = { ...problem({ path: draft.source, check: 1, message }), stale: true };
  return found;
}
const NEEDS_FLAG = "imported_from is for imports; add with --import to bring in imported records";
function hasId(text: string, prefix: string): boolean {
  return isId(text) && text.startsWith(`${prefix}-`);
}
function notAnId(given: unknown, prefix: string): string {
  const [kind, noun, example] =
    prefix === "d"
      ? ["a decision", "a decision", "d-3m8qk2"]
      : ["a specification entry", "an entry", "s-4kq1zm"];
  const head = `id ${valueRepr(given)} is not ${kind} ID; `;
  if (
    typeof given === "string" &&
    given !== given.toLowerCase() &&
    hasId(given.toLowerCase(), prefix)
  )
    return `${head}IDs are lower case, like ${example}`;
  if (typeof given === "string" && isId(given))
    return `${head}${noun} ID starts with ${prefix}-, like ${example}`;
  return `${head}an ID is ${prefix}- and six characters from 0-9 and a-z without i, l, o, and u, like ${example}`;
}
function originChanged(id: string): string {
  return `this draft changes imported_from of ${id}; keep it as lodge draft printed it`;
}
function sameOrigin(a: Record["importedFrom"], b: Record["importedFrom"]): boolean {
  return a === b || (a !== null && b !== null && a.file === b.file && a.heading === b.heading);
}

function display(value: unknown): string {
  return typeof value === "string" ? value : valueRepr(value);
}
