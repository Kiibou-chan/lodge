import type { Derived } from "./derive.ts";
import { LookupError } from "./errors.ts";
import type { Decision, Scope } from "./model.ts";
import type { Snapshot } from "./snapshot.ts";
import { orderInstant } from "./stamps.ts";
import { byCodePoint, isDigit, strip } from "./text.ts";
import { type Level1, level1 } from "./views.ts";
import { words } from "./words.ts";

const NEVER = orderInstant("0001-01-01T00:00:00+00:00");
const TITLE_WEIGHT = 3,
  STATEMENT_WEIGHT = 1;
const RELATED_SCORE = 2,
  RELATED_WORDS = 2,
  COMMON_FROM = 5;
const NONE: ReadonlySet<string> = new Set();

export interface Filters {
  readonly kind: "decision" | "spec" | null;
  readonly scope: Scope | null;
  readonly status: "current" | "replaced" | "retired" | "any";
  readonly area: string | null;
  readonly decidedBy: string | null;
}
export function filters(value: Partial<Filters> = {}): Filters {
  return { kind: null, scope: null, status: "current", area: null, decidedBy: null, ...value };
}
export class AmbiguousRef extends LookupError {
  override name = "AmbiguousRef";
}
export function resolve(s: Snapshot, ref: string): string | null {
  const wanted = strip(ref).toLowerCase();
  if (s.decisions.has(wanted) || s.entries.has(wanted)) return wanted;
  const records = new Map<string, { readonly code: string | null }>([...s.decisions, ...s.entries]);
  const coded = [...records]
    .filter(([, r]) => r.code && r.code.toLowerCase() === wanted)
    .map(([id]) => id)
    .sort(byCodePoint);
  if (coded.length > 1)
    throw new AmbiguousRef(`the code ${ref} names more than one record: ${coded.join(", ")}`);
  return coded[0] ?? null;
}
export function search(s: Snapshot, d: Derived, query: string, f: Filters, limit = 20): string[] {
  return searchCounted(s, d, query, f, limit)[0];
}
export function searchCounted(
  s: Snapshot,
  d: Derived,
  query: string,
  f: Filters,
  limit: number,
): readonly [string[], number] {
  const views = newestFirst(s, d, f);
  if (!strip(query)) return [views.slice(0, limit).map((v) => v.id), views.length];
  const exact = strip(query).toLowerCase();
  const hits = views.filter((v) => exact === v.id || exact === (v.code ?? "").toLowerCase());
  const queryWords = words(query);
  const ranked = views
    .filter((v) => !hits.includes(v))
    .map((v) => ({ v, score: score(v, queryWords) }))
    .filter((p) => p.score > 0)
    .sort((a, b) => b.score - a.score);
  const found = [...hits, ...ranked.map((p) => p.v)].map((v) => v.id);
  return [found.slice(0, limit), found.length];
}
export function related(s: Snapshot, d: Derived, decision: Decision, limit = 3): string[] {
  const views = newestFirst(s, d, filters({ kind: "decision" })).filter(
    (v) => v.id !== decision.id,
  );
  const shared = new Set(decision.changes.map((c) => c.entry));
  const sharing = views.filter((v) =>
    s.decisions.get(v.id)?.changes.some((c) => shared.has(c.entry)),
  );
  const common = commonWords(views);
  const query = new Set(
    [...words(`${decision.title} ${decision.statement}`)].filter(
      (w) => !isDigit(w) && !common.has(w),
    ),
  );
  const ranked = views
    .filter((v) => !sharing.includes(v) && sharesWords(v, query))
    .map((v) => ({ v, score: score(v, query) }))
    .filter((p) => p.score >= RELATED_SCORE)
    .sort((a, b) => b.score - a.score);
  return [...sharing, ...ranked.map((p) => p.v)].slice(0, limit).map((v) => v.id);
}
function sharesWords(v: Level1, query: ReadonlySet<string>): boolean {
  const held = new Set([...words(v.title), ...words(v.statement)]);
  return [...query].filter((w) => held.has(w)).length >= RELATED_WORDS;
}
function commonWords(views: readonly Level1[]): ReadonlySet<string> {
  if (views.length < COMMON_FROM) return new Set();
  const counts = new Map<string, number>();
  for (const v of views)
    for (const word of new Set([...words(v.title), ...words(v.statement)]))
      counts.set(word, (counts.get(word) ?? 0) + 1);
  return new Set([...counts].filter(([, n]) => n * 3 > views.length).map(([word]) => word));
}
function newestFirst(s: Snapshot, d: Derived, f: Filters): Level1[] {
  const views = [...new Set([...s.decisions.keys(), ...s.entries.keys()])]
    .map((id) => level1(s, d, id, NONE))
    .filter((v) => passes(s, v, f));
  return views.sort((a, b) => when(b) - when(a) || byCodePoint(b.id, a.id));
}
function score(v: Level1, query: ReadonlySet<string>): number {
  const title = words(v.title),
    statement = words(v.statement);
  return (
    TITLE_WEIGHT * [...query].filter((w) => title.has(w)).length +
    STATEMENT_WEIGHT * [...query].filter((w) => statement.has(w)).length
  );
}
function when(v: Level1): number {
  return v.date ? orderInstant(v.date) : NEVER;
}
function passes(s: Snapshot, v: Level1, f: Filters): boolean {
  return (
    (f.kind === null || v.kind === f.kind) &&
    (f.scope === null || v.scope === f.scope) &&
    (f.status === "any" || v.status === f.status) &&
    (f.area === null || areas(s, v).has(f.area)) &&
    (f.decidedBy === null || v.decidedBy === f.decidedBy)
  );
}
function areas(s: Snapshot, v: Level1): ReadonlySet<string> {
  if (v.area !== null) return new Set([v.area]);
  const result = new Set<string>();
  for (const c of s.decisions.get(v.id)?.changes ?? []) {
    const entry = s.entries.get(c.entry);
    if (entry) result.add(entry.area);
  }
  return result;
}
