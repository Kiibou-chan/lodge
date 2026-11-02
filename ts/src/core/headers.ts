import { hasReasoningHeading, REASONING_HEADING, splitReasoning, trimBlock } from "./document.ts";
import {
  checkKeys,
  FormatError,
  readAreaName,
  readCode,
  readDate,
  readEnum,
  readId,
  readIds,
  readMap,
  readMaps,
  readOptionalStr,
  readRank,
  readStr,
  readStrs,
  require as requireField,
} from "./fields.ts";
import {
  Action,
  type Area,
  area,
  type Decision,
  decision,
  type Imported,
  type Quote,
  Scope,
  type SpecEntry,
  specEntry,
} from "./model.ts";

type Header = ReadonlyMap<string, unknown>;
export const DECISION_KEYS = [
  "id",
  "kind",
  "code",
  "title",
  "scope",
  "decided_by",
  "date",
  "changes",
  "replaces",
  "narrows",
  "confirms",
  "work_item",
  "quote",
  "numbers",
  "attachments",
  "imported_from",
];
export const SPEC_KEYS = ["id", "kind", "code", "title", "imported_from", "rests_on"];
export const AREA_KEYS = ["kind", "title", "order", "rank"];
export function decisionFrom(header: Header, body: string): Decision {
  checkKeys(header, DECISION_KEYS);
  expectKind(header, "decision");
  const id = readId(requireField(header, "id"), "id", "d");
  const title = readStr(requireField(header, "title"), "title");
  const scope = readEnum(Scope, requireField(header, "scope"), "scope");
  const decidedBy = readStr(requireField(header, "decided_by"), "decided_by");
  const importedFrom = imported(header);
  const date = readDate(requireField(header, "date"), importedFrom !== null);
  const [statement, reasoning] = splitReasoning(body);
  if (!statement)
    throw new FormatError("the statement is empty; write it above any '## Reasoning' heading");
  return decision({
    id,
    title,
    scope,
    decidedBy,
    date,
    statement,
    reasoning,
    code: readCode(header),
    changes: changes(header).map((item) => ({
      entry: mapString(item, "entry"),
      action: readEnum(Action, item.get("action"), "changes.action"),
    })),
    replaces: ids(header, "replaces"),
    narrows: ids(header, "narrows"),
    confirms: ids(header, "confirms"),
    workItem: readOptionalStr(header, "work_item"),
    quote: quote(header),
    numbers: readMaps(header.has("numbers") ? header.get("numbers") : [], "numbers", [
      "value",
      "handle",
    ]).map((item) => ({ value: mapString(item, "value"), handle: mapString(item, "handle") })),
    attachments: readStrs(
      header.has("attachments") ? header.get("attachments") : [],
      "attachments",
    ),
    importedFrom,
  });
}
export function specFrom(header: Header, body: string, name: string): SpecEntry {
  checkKeys(header, SPEC_KEYS);
  expectKind(header, "spec");
  const id = readId(requireField(header, "id"), "id", "s");
  const title = readStr(requireField(header, "title"), "title");
  if (hasReasoningHeading(body))
    throw new FormatError(`a specification entry has no '${REASONING_HEADING}' section`);
  const statement = trimBlock(body);
  if (!statement) throw new FormatError("the statement is empty");
  return specEntry({
    id,
    area: readAreaName(name, "area"),
    title,
    statement,
    code: readCode(header),
    importedFrom: imported(header),
    restsOn: ids(header, "rests_on", "s"),
  });
}
export function areaFrom(header: Header, body: string, name: string): Area {
  checkKeys(header, AREA_KEYS);
  expectKind(header, "area");
  return area({
    name: readAreaName(name, "area"),
    title: readStr(requireField(header, "title"), "title"),
    intro: trimBlock(body),
    order: ids(header, "order", "s"),
    rank: header.has("rank") ? readRank(header.get("rank")) : null,
  });
}
function expectKind(header: Header, kind: string): void {
  if (requireField(header, "kind") !== kind)
    throw new FormatError(`kind must be '${kind}' here`, "kind");
}
function ids(header: Header, key: string, prefix = "d"): readonly string[] {
  return readIds(header.has(key) ? header.get(key) : [], key, prefix);
}
function changes(header: Header): readonly ReadonlyMap<string, string>[] {
  const items = readMaps(header.has("changes") ? header.get("changes") : [], "changes", [
    "entry",
    "action",
  ]);
  for (const item of items) readId(item.get("entry"), "changes.entry", "s");
  return items;
}
function quote(header: Header): Quote | null {
  if (!header.has("quote")) return null;
  const fields = readMap(header.get("quote"), "quote", ["text", "where", "when"], "text");
  return {
    text: mapString(fields, "text"),
    where: mapString(fields, "where"),
    when: mapString(fields, "when"),
  };
}
function imported(header: Header): Imported | null {
  if (!header.has("imported_from")) return null;
  const fields = readMap(header.get("imported_from"), "imported_from", ["file", "heading"]);
  return { file: mapString(fields, "file"), heading: mapString(fields, "heading") };
}

// readMap has already required every named value to be a string.
function mapString(fields: ReadonlyMap<string, string>, key: string): string {
  const value = fields.get(key);
  if (value === undefined) throw new FormatError(`missing required field '${key}'`, key);
  return value;
}
