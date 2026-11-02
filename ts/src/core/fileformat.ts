import { sha256 } from "@noble/hashes/sha2.js";
import { bytesToHex } from "@noble/hashes/utils.js";
import {
  assemble,
  hasReasoningHeading,
  normaliseNewlines,
  REASONING_HEADING,
  readWith,
} from "./document.ts";
import { ValueError } from "./errors.ts";
import { FormatError, readAreaName } from "./fields.ts";
import { areaFrom, decisionFrom, specFrom } from "./headers.ts";
import type { Area, Decision, Imported, Problem, Record, SpecEntry } from "./model.ts";
import { READ_BACK_FIELDS } from "./read-back-fields.ts";
import { pyRepr } from "./text.ts";
import { LINE_BREAKS_AND_TABS, quoted } from "./yamlio.ts";

export function parseRecord(path: string, text: string): Record | Problem {
  return readWith(path, text, (header, body) => {
    const kind = header.get("kind");
    if (kind === "decision") return decisionFrom(header, body);
    if (kind === "spec") return specFrom(header, body, folderOf(path));
    throw new FormatError("kind must be 'decision' or 'spec'", "kind");
  });
}
export function parseArea(path: string, text: string): Area | Problem {
  return readWith(path, text, (header, body) => areaFrom(header, body, folderOf(path)));
}
// A record that would not read back unchanged raises ValueError.
export function writeRecord(record: Record): string {
  if (hasReasoningHeading(record.statement))
    throw new ValueError(`the statement holds a line reading '${REASONING_HEADING}'`);
  const text =
    record.kind === "decision"
      ? assemble(decisionHeader(record), decisionBody(record))
      : assemble(specHeader(record), record.statement);
  const back = parseRecord(newRecordPath(record), text);
  if (back.kind === "problem")
    throw new ValueError(`the record would not read back: ${back.message}`);
  const difference = differing(record, back);
  if (difference !== null)
    throw new ValueError(`the record would not read back unchanged: ${difference}`);
  return text;
}
export function writeArea(area: Area): string {
  const header = ["kind: area", `title: ${quoteValue("title", area.title)}`];
  if (area.rank !== null) header.push(`rank: ${area.rank}`);
  if (area.order.length) header.push(`order: [${area.order.join(", ")}]`);
  const text = assemble(header, area.intro);
  const back = parseArea(areaPath(area.name), text);
  if (back.kind === "problem")
    throw new ValueError(`the area would not read back: ${back.message}`);
  const difference = differing(area, back);
  if (difference !== null)
    throw new ValueError(`the area would not read back unchanged: ${difference}`);
  return text;
}
export function newRecordPath(record: Record): string {
  const words = slug(record.title);
  const stem = words ? `${record.id}-${words}` : record.id;
  return record.kind === "decision"
    ? `lodge/decisions/${stem}.md`
    : `lodge/spec/${record.area}/${stem}.md`;
}
export function areaPath(name: string): string {
  return `lodge/spec/${name}/_area.md`;
}
const SLUG_WORDS = 6;
const SLUG_CHARS = 60;
const PLAIN = /^[A-Za-z0-9][A-Za-z0-9._-]*$/u;

export function slug(title: string): string {
  const joined = (title.toLowerCase().match(/[a-z0-9]+/gu) ?? []).slice(0, SLUG_WORDS).join("-");
  if (joined.length <= SLUG_CHARS) return joined;
  const cut = joined.lastIndexOf("-", SLUG_CHARS);
  return joined.slice(0, cut > 0 ? cut : SLUG_CHARS);
}
export function contentHash(text: string): string {
  const bytes = new TextEncoder().encode(normaliseNewlines(text));
  return bytesToHex(sha256(bytes)).slice(0, 12);
}
function folderOf(path: string): string {
  const parts = path.split("/");
  if (parts.length < 2)
    throw new FormatError(
      "an area's files lie in a folder named after the area, as in lodge/spec/<area>/",
    );
  return readAreaName(parts.at(-2), "area");
}
function equal(a: unknown, b: unknown): boolean {
  if (a === b) return true;
  if (Array.isArray(a) && Array.isArray(b))
    return a.length === b.length && a.every((item, i) => equal(item, b[i]));
  if (a !== null && b !== null && typeof a === "object" && typeof b === "object")
    return (
      Object.keys(a).length === Object.keys(b).length &&
      Object.entries(a).every(([key, value]) => equal(value, Reflect.get(b, key)))
    );
  return false;
}
function valueRepr(value: unknown): string {
  if (typeof value === "string") return pyRepr(value);
  if (value === null) return "None";
  if (Array.isArray(value))
    return `(${value.map(valueRepr).join(", ")}${value.length === 1 ? "," : ""})`;
  if (typeof value === "object") {
    const get = (key: string) => valueRepr(Reflect.get(value, key));
    if ("entry" in value && "action" in value)
      return `Change(entry=${get("entry")}, action=<Action.${String(value.action).toUpperCase()}: ${get("action")}>)`;
    if ("text" in value && "where" in value && "when" in value)
      return `Quote(text=${get("text")}, where=${get("where")}, when=${get("when")})`;
    if ("value" in value && "handle" in value)
      return `NumberHandle(value=${get("value")}, handle=${get("handle")})`;
    if ("file" in value && "heading" in value)
      return `Imported(file=${get("file")}, heading=${get("heading")})`;
  }
  return String(value);
}
function differing(record: Record | Area, back: Record | Area): string | null {
  const fields = READ_BACK_FIELDS[record.kind];
  for (const key of fields)
    if (!equal(Reflect.get(record, key), Reflect.get(back, key)))
      return `${key.replace(/[A-Z]/gu, (char) => `_${char.toLowerCase()}`)} reads back as ${valueRepr(Reflect.get(back, key))}`;
  return record.kind === back.kind ? null : "the kind differs";
}
function quoteValue(key: string, value: string, allowed = ""): string {
  try {
    return quoted(value, allowed);
  } catch (error) {
    if (!(error instanceof ValueError)) throw error;
    throw new ValueError(`${key}: ${error.message}`);
  }
}
function importedLine(imported: Imported): string {
  return `imported_from: {file: ${quoteValue("imported_from.file", imported.file)}, heading: ${quoteValue("imported_from.heading", imported.heading)}}`;
}
function decisionHeader(d: Decision): string[] {
  const plain = PLAIN.test(d.decidedBy) ? d.decidedBy : quoteValue("decided_by", d.decidedBy);
  const header = [`id: ${d.id}`, "kind: decision"];
  if (d.code !== null) header.push(`code: ${d.code}`);
  header.push(
    `title: ${quoteValue("title", d.title)}`,
    `scope: ${d.scope}`,
    `decided_by: ${plain}`,
    `date: ${d.date}`,
  );
  if (d.changes.length)
    header.push(
      "changes:",
      ...d.changes.map((c) => `  - {entry: ${c.entry}, action: ${c.action}}`),
    );
  for (const [key, ids] of [
    ["replaces", d.replaces],
    ["narrows", d.narrows],
    ["confirms", d.confirms],
  ] as const)
    if (ids.length) header.push(`${key}: [${ids.join(", ")}]`);
  if (d.workItem !== null) header.push(`work_item: ${quoteValue("work_item", d.workItem)}`);
  if (d.quote !== null)
    header.push(
      `quote: {text: ${quoteValue("quote.text", d.quote.text, LINE_BREAKS_AND_TABS)}, where: ${quoteValue("quote.where", d.quote.where)}, when: ${quoteValue("quote.when", d.quote.when)}}`,
    );
  if (d.numbers.length)
    header.push(
      "numbers:",
      ...d.numbers.map(
        (n) =>
          `  - {value: ${quoteValue("numbers.value", n.value)}, handle: ${quoteValue("numbers.handle", n.handle)}}`,
      ),
    );
  if (d.attachments.length)
    header.push(
      `attachments: [${d.attachments.map((a) => quoteValue("attachments", a)).join(", ")}]`,
    );
  if (d.importedFrom !== null) header.push(importedLine(d.importedFrom));
  return header;
}
function decisionBody(d: Decision): string {
  return d.reasoning ? `${d.statement}\n\n${REASONING_HEADING}\n\n${d.reasoning}` : d.statement;
}
function specHeader(entry: SpecEntry): string[] {
  const header = [`id: ${entry.id}`, "kind: spec"];
  if (entry.code !== null) header.push(`code: ${entry.code}`);
  header.push(`title: ${quoteValue("title", entry.title)}`);
  if (entry.restsOn.length) header.push(`rests_on: [${entry.restsOn.join(", ")}]`);
  if (entry.importedFrom !== null) header.push(importedLine(entry.importedFrom));
  return header;
}
