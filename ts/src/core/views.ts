import type { CheckResult } from "./check-state.ts";
import { type Derived, isAuthor } from "./derive.ts";
import {
  Action,
  type Decision,
  type Imported,
  type NumberHandle,
  type Problem,
  type Quote,
  type SpecEntry,
  uniqueChanges,
} from "./model.ts";
import type { Snapshot } from "./snapshot.ts";
import { orderInstant } from "./stamps.ts";
export interface Level1 {
  readonly id: string;
  readonly kind: string;
  readonly code: string | null;
  readonly title: string;
  readonly statement: string;
  readonly status: string;
  readonly decidedBy: string | null;
  readonly date: string | null;
  readonly scope: string | null;
  readonly area: string | null;
  readonly flags: readonly string[];
  readonly quote: Quote | null;
}
export interface Level3 {
  readonly quote: Quote | null;
  readonly numbers: readonly NumberHandle[];
  readonly workItem: string | null;
  readonly attachments: readonly string[];
  readonly importedFrom: Imported | null;
  readonly links: readonly (readonly [string, string, string])[];
}
export function failingIds(s: Snapshot, result: CheckResult): ReadonlySet<string> {
  const byPath = new Map([...s.paths].map(([id, path]) => [path, id]));
  return new Set(
    result.problems.flatMap((p) => (byPath.has(p.path) ? [byPath.get(p.path) as string] : [])),
  );
}
export function unrecordedProblems(s: Snapshot, result: CheckResult): readonly Problem[] {
  const held = new Set([...s.paths].filter(([id]) => !s.threads.has(id)).map(([, path]) => path));
  return result.problems.filter((p) => !held.has(p.path));
}
export function level1(s: Snapshot, d: Derived, id: string, failing: ReadonlySet<string>): Level1 {
  const dec = s.decisions.get(id);
  const record = dec ?? (s.entries.get(id) as Decision | SpecEntry);
  const newest = d.changedBy.get(id) ?? [];
  const who = dec ?? (newest.length ? (s.decisions.get(newest[0] as string) as Decision) : null);
  return {
    id,
    kind: record.kind,
    code: record.code,
    title: record.title,
    statement: record.statement,
    status: d.status.get(id) as string,
    decidedBy: who?.decidedBy ?? null,
    date: who?.date ?? null,
    scope: record.kind === "decision" ? record.scope : null,
    area: record.kind === "spec" ? record.area : null,
    flags: flags(s, d, record, who, failing),
    quote: who && isAuthor(who) ? who.quote : null,
  };
}
export function level2(s: Snapshot, d: Derived, id: string, failing: ReadonlySet<string>): string {
  const dec = s.decisions.get(id);
  return dec ? dec.reasoning : level2Views(s, d, id, failing).map(head).join("\n\n");
}
export function level2Views(
  s: Snapshot,
  d: Derived,
  id: string,
  failing: ReadonlySet<string>,
): readonly Level1[] {
  return s.decisions.has(id)
    ? []
    : (d.changedBy.get(id) ?? []).map((i) => level1(s, d, i, failing));
}
export function level3(s: Snapshot, d: Derived, id: string): Level3 {
  const links: [string, string, string][] = [];
  const add = (relation: string, targets: readonly string[]) => {
    for (const target of targets) links.push([relation, target, d.status.get(target) ?? "unknown"]);
  };
  const dec = s.decisions.get(id);
  if (dec) {
    for (const c of uniqueChanges(dec.changes)) add(`changes (${c.action})`, [c.entry]);
    add("replaces", dec.replaces);
    add("narrows", dec.narrows);
    add("confirms", dec.confirms);
    add("replaced by", d.replacedBy.get(id) ?? []);
    add("narrowed by", d.narrowedBy.get(id) ?? []);
    add("confirmed by", d.confirmedBy.get(id) ?? []);
    return {
      quote: dec.quote,
      numbers: dec.numbers,
      workItem: dec.workItem,
      attachments: dec.attachments,
      importedFrom: dec.importedFrom,
      links,
    };
  }
  add("changed by", d.changedBy.get(id) ?? []);
  add("rests on", (s.entries.get(id) as SpecEntry).restsOn);
  add("supports", d.supports.get(id) ?? []);
  add("linked by", d.linkedBy.get(id) ?? []);
  return {
    quote: null,
    numbers: [],
    workItem: null,
    attachments: [],
    importedFrom: (s.entries.get(id) as SpecEntry).importedFrom,
    links,
  };
}
function quoteText(q: Quote): string {
  return `quote: "${q.text}" (${q.where}, ${q.when})`;
}
export function formatLevel1(v: Level1): string {
  return `${head(v)}\n\n${v.statement}${v.quote ? `\n\n${quoteText(v.quote)}` : ""}`;
}
export function formatLevel3(v: Level3): string {
  const lines: string[] = [];
  if (v.quote) lines.push(quoteText(v.quote));
  if (v.numbers.length)
    lines.push(`numbers: ${v.numbers.map((n) => `${n.value} (${n.handle})`).join("; ")}`);
  if (v.workItem) lines.push(`work item: ${v.workItem}`);
  if (v.attachments.length) lines.push(`attachments: ${v.attachments.join(", ")}`);
  if (v.importedFrom)
    lines.push(`imported from: ${v.importedFrom.file}, ${v.importedFrom.heading}`);
  for (const [relation, target, status] of v.links)
    lines.push(`${relation}: ${target} (${status})`);
  return lines.join("\n");
}
export function headParts(
  v: Level1,
): readonly [string, string | null, string, string | null, string | null, string | null] {
  return [
    v.id,
    v.code,
    v.status,
    v.decidedBy || (v.kind === "spec" ? "no decision" : null),
    v.date ? (v.date.split("T")[0] as string) : null,
    v.scope || v.area,
  ];
}
function head(v: Level1): string {
  const [id, code, status, who, day, place] = headParts(v);
  return (
    [code ? `${id} ${code}` : id, status, who, day, place, ...v.flags].filter(Boolean).join(" · ") +
    `\n${v.title}`
  );
}
function flags(
  s: Snapshot,
  d: Derived,
  record: Decision | SpecEntry,
  who: Decision | null,
  failing: ReadonlySet<string>,
): readonly string[] {
  const id = record.id,
    result: string[] = [];
  const replaced = d.replacedBy.get(id),
    narrowed = d.narrowedBy.get(id);
  if (replaced?.length) result.push(`replaced by ${replaced.join(", ")}`);
  if (narrowed?.length) result.push(`narrowed by ${narrowed.join(", ")}`);
  if (d.status.get(id) === "retired") {
    const retiring = (d.changedBy.get(id) ?? []).find(
      (i) =>
        !d.replacedBy.has(i) &&
        s.decisions.get(i)?.changes.some((c) => c.entry === id && c.action === Action.RETIRE),
    );
    if (retiring) result.push(`retired by ${retiring}`);
  }
  if (record.kind === "spec" && who) {
    const rep = d.replacedBy.get(who.id),
      nar = d.narrowedBy.get(who.id);
    if (rep?.length) result.push(`its decision replaced by ${rep.join(", ")}`);
    if (nar?.length) result.push(`its decision narrowed by ${nar.join(", ")}`);
  }
  if (d.awaitingAuthor.has(id)) result.push("awaiting the author");
  else {
    const waiting = d.touchedByFlagged.get(id);
    if (waiting?.length) result.push(`awaiting the author on ${waiting.join(", ")}`);
  }
  const confirmed = d.confirmedBy.get(id);
  if (record.kind === "decision" && confirmed?.length)
    result.push(`confirmed by the author (${confirmed.join(", ")})`);
  result.push(...(d.doubts.get(id) ?? []));
  if (record.kind === "spec")
    for (const target of record.restsOn) {
      if (d.status.get(target) === "retired") result.push(`rests on ${target}, retired`);
      else {
        const changes = d.changedBy.get(target);
        if (
          who &&
          changes?.length &&
          orderInstant((s.decisions.get(changes[0] as string) as Decision).date) >
            orderInstant(who.date)
        )
          result.push(`rests on ${target}, changed since`);
      }
    }
  if (record.importedFrom !== null) {
    result.push("imported");
    if (record.kind === "decision" && record.decidedBy === "author" && record.quote === null)
      result.push("unquoted");
  }
  if (failing.has(id)) result.push("fails check");
  if (record.kind === "spec" && who && failing.has(who.id)) result.push("decision fails check");
  return result;
}
