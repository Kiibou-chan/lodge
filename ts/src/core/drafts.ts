import { loadHeader, problemFor, splitDocument, trimBlock } from "./document.ts";
import { checkKeys, FormatError, readStr } from "./fields.ts";
import {
  AREA_KEYS,
  areaFrom,
  DECISION_KEYS,
  decisionFrom,
  SPEC_KEYS,
  specFrom,
} from "./headers.ts";
import type { Area, Problem, Record } from "./model.ts";
import { pyRepr } from "./text.ts";
import { valueRepr } from "./value-repr.ts";

type DraftKind = "decision" | "spec" | "area";
const KEYS: { readonly [K in DraftKind]: readonly string[] } = {
  decision: [...DECISION_KEYS, "base"],
  spec: [...SPEC_KEYS, "area", "base"],
  area: [...AREA_KEYS, "name", "base"],
};
export interface Draft {
  readonly kind: DraftKind;
  readonly header: ReadonlyMap<string, unknown>;
  readonly body: string;
  readonly source: string;
  readonly headerText: string;
}
// Checks syntax and key names only.
export function parseDraft(source: string, text: string): Draft | Problem {
  let headerText = "";
  try {
    const [head, body] = splitDocument(text);
    headerText = head;
    const header = loadHeader(headerText);
    const kind = kindOf(header.get("kind"));
    checkKeys(header, KEYS[kind]);
    return { kind, header, body: trimBlock(body), source, headerText };
  } catch (error) {
    if (!(error instanceof FormatError)) throw error;
    return problemFor(source, error, headerText);
  }
}
// New records receive date; only imports may carry their own date.
// Existing records receive null and keep their draft date.
// New entries and areas name themselves; existing ones receive area.
export function recordFromDraft(
  draft: Draft,
  id: string,
  date: string | null,
  area: string | null,
): Record | Area | Problem {
  let header = new Map(
    [...draft.header].filter(([key]) => !["area", "name", "base"].includes(key)),
  );
  try {
    if (draft.kind === "area") return areaFrom(header, draft.body, name(draft, "name", area));
    header = withId(header, id);
    if (draft.kind === "spec") return specFrom(header, draft.body, name(draft, "area", area));
    return decisionFrom(withDate(header, date), draft.body);
  } catch (error) {
    if (!(error instanceof FormatError)) throw error;
    return problemFor(draft.source, error, draft.headerText);
  }
}
function kindOf(value: unknown): DraftKind {
  if (value === "decision" || value === "spec" || value === "area") return value;
  throw new FormatError("kind must be 'decision', 'spec', or 'area'", "kind");
}
function withId(header: Map<string, unknown>, id: string): Map<string, unknown> {
  if (header.has("id") && header.get("id") !== id)
    throw new FormatError(
      `id ${valueRepr(header.get("id"))} differs from the id ${pyRepr(id)} lodge gave this draft`,
      "id",
    );
  return new Map([...header, ["id", id]]);
}
function withDate(header: Map<string, unknown>, date: string | null): Map<string, unknown> {
  if (date === null || (header.has("date") && header.has("imported_from"))) return header;
  if (header.has("date"))
    throw new FormatError(
      "lodge sets the date; a draft may set one only with imported_from",
      "date",
    );
  return new Map([...header, ["date", date]]);
}
function name(draft: Draft, key: string, given: string | null): string {
  const own = draft.header.has(key) ? readStr(draft.header.get(key), key) : null;
  if (given !== null && own !== null && own !== given)
    throw new FormatError(
      `${key} ${pyRepr(own)} differs from ${pyRepr(given)}; entries do not move`,
      key,
    );
  const found = given !== null ? given : own;
  if (found === null) throw new FormatError(`a new ${draft.kind} draft needs a '${key}' key`, key);
  return found;
}
