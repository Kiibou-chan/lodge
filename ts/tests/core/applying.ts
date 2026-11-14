import assert from "node:assert/strict";
import {
  type Applied,
  type Area,
  applyDrafts,
  type Decision,
  type Draft,
  load,
  type Problem,
  parseDraft,
  type Snapshot,
  type SpecEntry,
  type StaleBase,
  type Tree,
} from "#core";
import { treeOf } from "./builders.ts";
import { document } from "./samples.ts";

export const NOW = "2026-10-29T09:30:00+01:00";
function drafted(...texts: string[]): Draft[] {
  const drafts = texts.map((text, i) => parseDraft(`draft${i}.md`, text));
  assert(drafts.every((d) => d.kind !== "problem"));
  return drafts;
}
type Body = { body: string };
function parts(args: (string | Body)[], fallback: string): [string[], string] {
  return [
    args.filter((a): a is string => typeof a === "string"),
    args.find((a): a is Body => typeof a !== "string")?.body ?? fallback,
  ];
}
export function decisionText(...args: (string | Body)[]): string {
  const [extra, body] = parts(args, "It is kept.");
  return document(
    [
      "kind: decision",
      'title: "Keep transcripts"',
      "scope: process",
      "decided_by: coordinator",
      ...extra,
    ],
    body,
  );
}
export function specText(...args: (string | Body)[]): string {
  const [header, body] = parts(args, "They are kept.");
  return document(["kind: spec", 'title: "Transcripts"', ...header], body);
}
export function areaText(...args: (string | Body)[]): string {
  const [header, body] = parts(args, "Intro.");
  return document(["kind: area", 'title: "Storage"', ...header], body);
}
export function state(...items: (Decision | SpecEntry | Area)[]): [Snapshot, Tree] {
  const tree = treeOf(...items);
  return [load(tree), tree];
}
type Options = { ids?: readonly string[]; importing?: boolean };
export function apply(s: Snapshot, tree: Tree, ...args: (string | Options)[]) {
  const texts = args.filter((a): a is string => typeof a === "string");
  const options = args.find((a): a is Options => typeof a !== "string") ?? {};
  return applyDrafts(
    s,
    tree,
    drafted(...texts),
    options.ids ?? [],
    NOW,
    options.importing ?? false,
  );
}
export function applied(result: Applied | Problem[]): Applied {
  assert(!Array.isArray(result));
  return result;
}
export function problems(result: Applied | Problem[]): Problem[] {
  assert(Array.isArray(result));
  return result;
}
export function present<T>(value: T | undefined): T {
  assert(value !== undefined);
  return value;
}

export function isStale(value: Problem): value is StaleBase {
  return "stale" in value && value.stale === true;
}
