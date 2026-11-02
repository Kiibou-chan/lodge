import { isId } from "./ids.ts";
import { isDay, isStamp } from "./stamps.ts";
import { pyRepr, strip } from "./text.ts";
import { LINE_BREAKS_AND_TABS, unreadableChar } from "./yamlio.ts";

const ID_KIND: ReadonlyMap<string, string> = new Map([
  ["d", "decision"],
  ["s", "specification entry"],
  ["q", "thread"],
]);
const CODE = /^[A-Za-z0-9][A-Za-z0-9._-]*$/u;

export class FormatError extends Error {
  constructor(
    message: string,
    readonly key: string | null = null,
    readonly line: number | null = null,
  ) {
    super(message);
    this.name = "FormatError";
  }
}
export function checkKeys(header: ReadonlyMap<string, unknown>, allowed: readonly string[]): void {
  const unknown = [...header.keys()].filter((key) => !allowed.includes(key));
  if (unknown.length)
    throw new FormatError(
      `unknown key ${unknown.map(pyRepr).join(", ")}; the keys here are ${allowed.join(", ")}`,
      unknown[0],
    );
}
export function require(header: ReadonlyMap<string, unknown>, key: string): unknown {
  if (!header.has(key)) throw new FormatError(`missing required field '${key}'`, key);
  return header.get(key);
}
export function readStr(value: unknown, key: string, allowed = ""): string {
  if (typeof value !== "string" || !strip(value))
    throw new FormatError(`${key} must be a non-empty string`, key);
  const bad = unreadableChar(value, allowed);
  if (bad !== null)
    throw new FormatError(
      `${key} holds U+${bad.codePointAt(0)?.toString(16).toUpperCase().padStart(4, "0")}, which a header cannot carry`,
      key,
    );
  return value;
}
export function readOptionalStr(header: ReadonlyMap<string, unknown>, key: string): string | null {
  return header.has(key) ? readStr(header.get(key), key) : null;
}
export function readCode(header: ReadonlyMap<string, unknown>): string | null {
  const code = readOptionalStr(header, "code");
  if (code !== null && !CODE.test(code))
    throw new FormatError(
      `code must match [A-Za-z0-9][A-Za-z0-9._-]*, not ${pyRepr(code)}`,
      "code",
    );
  return code;
}
function readList(value: unknown, key: string): unknown[] {
  if (!Array.isArray(value)) throw new FormatError(`${key} must be a list`, key);
  return value;
}
// The multiline key may hold line breaks and tabs.
export function readMap(
  value: unknown,
  key: string,
  names: readonly string[],
  multiline: string | null = null,
): ReadonlyMap<string, string> {
  if (!(value instanceof Map))
    throw new FormatError(`${key} must be a mapping with ${names.join(", ")}`, key);
  for (const name of value.keys())
    if (!names.includes(name))
      throw new FormatError(
        `${key} has an unknown key ${pyRepr(String(name))}; it takes ${names.join(", ")}`,
        key,
      );
  for (const name of names)
    if (!value.has(name)) throw new FormatError(`${key} is missing '${name}'`, key);
  return new Map(
    names.map((name) => [
      name,
      readStr(value.get(name), `${key}.${name}`, name === multiline ? LINE_BREAKS_AND_TABS : ""),
    ]),
  );
}
export function readMaps(
  value: unknown,
  key: string,
  names: readonly string[],
): readonly ReadonlyMap<string, string>[] {
  return readList(value, key).map((item) => readMap(item, key, names));
}
export function readId(value: unknown, key: string, prefix: string): string {
  const text = readStr(value, key);
  if (!isId(text) || !text.startsWith(`${prefix}-`))
    throw new FormatError(
      `${key} holds ${pyRepr(text)}, which is not a ${ID_KIND.get(prefix)} id`,
      key,
    );
  return text;
}
export function readIds(value: unknown, key: string, prefix: string): readonly string[] {
  return readList(value, key).map((item) => readId(item, key, prefix));
}
export function readStrs(value: unknown, key: string): readonly string[] {
  return readList(value, key).map((item) => readStr(item, key));
}
export function readEnum<T extends string>(
  kind: { readonly [key: string]: T },
  value: unknown,
  key: string,
): T {
  const text = readStr(value, key);
  const values = Object.values(kind);
  if (!values.includes(text as T))
    throw new FormatError(
      `${key} must be one of ${values.map(pyRepr).join(", ")}, not ${pyRepr(text)}`,
      key,
    );
  return text as T;
}
const STAMP = /^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}[+-][0-9]{2}:[0-9]{2}$/u;
const DAY = /^[0-9]{4}-[0-9]{2}-[0-9]{2}$/u;
// A bare day is accepted only for an imported record.
export function readDate(value: unknown, imported: boolean): string {
  const text = readStr(value, "date");
  if (STAMP.test(text)) {
    if (isStamp(text)) return text;
    throw new FormatError(`date ${pyRepr(text)} is not a real date and time`, "date");
  }
  if (DAY.test(text) && imported) {
    if (isDay(text)) return `${text}T00:00:00+00:00`;
    throw new FormatError(`date ${pyRepr(text)} is not a real date and time`, "date");
  }
  const hint = imported ? "" : "; a date alone is accepted only with imported_from";
  throw new FormatError(
    `date must be ISO 8601 with seconds and an offset, as in 2026-10-28T23:48:10+01:00${hint}`,
    "date",
  );
}
export function readAreaName(value: unknown, key: string): string {
  const text = readStr(value, key);
  if (!/^[a-z0-9]+(?:-[a-z0-9]+)*$/u.test(text))
    throw new FormatError(
      `area name ${pyRepr(text)} must be lower-case words joined by hyphens`,
      key,
    );
  return text;
}
export function readRank(value: unknown): number {
  if (
    typeof value !== "string" ||
    !/^(?:0|[1-9][0-9]*)$/u.test(value) ||
    !Number.isSafeInteger(Number(value))
  )
    throw new FormatError(
      "rank must be a non-negative whole number without leading zeroes",
      "rank",
    );
  return Number(value);
}
export function readStamp(value: unknown, key: string): string {
  const text = readStr(value, key);
  if (STAMP.test(text) && isStamp(text)) return text;
  throw new FormatError(`${key} must be ISO 8601 with seconds and an offset`, key);
}
