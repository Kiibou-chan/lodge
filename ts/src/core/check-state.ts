import { checkAreas } from "./check-areas.ts";
import { checkCycles } from "./check-cycles.ts";
import { isAuthor } from "./derive.ts";
import { type Decision, type Problem, problem, type Record } from "./model.ts";
import { attachmentPath, type Snapshot } from "./snapshot.ts";
import { byCodePoint, casefold, strip } from "./text.ts";
export interface CheckResult {
  readonly problems: readonly Problem[];
  readonly notes: readonly string[];
  readonly ok: boolean;
}
export function sortKey(p: Problem): readonly [string, number, string] {
  return [p.path, p.check, p.message];
}
export function problemAt(s: Snapshot, recordId: string, check: number, message: string): Problem {
  return problem({ path: s.paths.get(recordId) ?? "", check, message: `${recordId}: ${message}` });
}
function decisions(s: Snapshot): Decision[] {
  return [...s.decisions.keys()].sort(byCodePoint).map((id) => s.decisions.get(id) as Decision);
}
export function newDecisions(published: Snapshot, after: Snapshot): Decision[] {
  return decisions(after).filter((d) => !published.decisions.has(d.id));
}
function records(s: Snapshot): Record[] {
  return [
    ...decisions(s),
    ...[...s.entries.keys()].sort(byCodePoint).map((id) => s.entries.get(id) as Record),
  ];
}
function* fileNames(s: Snapshot): Generator<Problem> {
  for (const r of [...records(s), ...s.threads.values()]) {
    const name = (s.paths.get(r.id) as string).split("/").at(-1) as string;
    if (name !== `${r.id}.md` && !name.startsWith(`${r.id}-`))
      yield problemAt(s, r.id, 1, `the file name ${name} does not start with the ID`);
  }
}
function* unresolved(s: Snapshot): Generator<Problem> {
  for (const t of s.threads.values())
    if (!s.decisions.has(t.about) && !s.entries.has(t.about))
      yield problemAt(s, t.id, 2, `about ${t.about}, which does not exist`);
  for (const id of [...s.entries.keys()].sort(byCodePoint)) {
    const e = s.entries.get(id);
    for (const target of new Set(e?.restsOn)) {
      if (target === id) yield problemAt(s, id, 2, "rests_on itself");
      else if (!s.entries.has(target))
        yield problemAt(s, id, 2, `rests_on ${target}, which does not exist`);
    }
  }
  for (const d of decisions(s)) {
    const targets: readonly [string, readonly string[], ReadonlyMap<string, unknown>][] = [
      ["changes", d.changes.map((c) => c.entry), s.entries],
      ["replaces", d.replaces, s.decisions],
      ["narrows", d.narrows, s.decisions],
      ["confirms", d.confirms, s.decisions],
    ];
    for (const [key, ids, known] of targets)
      for (const target of new Set(ids)) {
        if (target === d.id) yield problemAt(s, d.id, 2, `${key} itself`);
        else if (!known.has(target))
          yield problemAt(s, d.id, 2, `${key} ${target}, which does not exist`);
      }
  }
}
function* codes(s: Snapshot): Generator<Problem> {
  const groups = new Map<string, Record[]>();
  for (const r of records(s))
    if (r.code !== null) {
      const key = casefold(r.code),
        group = groups.get(key) ?? [];
      group.push(r);
      groups.set(key, group);
    }
  for (const group of groups.values())
    if (group.length > 1)
      for (const r of group)
        yield problemAt(
          s,
          r.id,
          2,
          `code ${r.code} is shared with another record, compared without regard to case`,
        );
}
function* attachments(s: Snapshot): Generator<Problem> {
  for (const d of decisions(s))
    for (const name of new Set(d.attachments))
      if (!s.attachments.has(attachmentPath(d.id, name)))
        yield problemAt(
          s,
          d.id,
          2,
          `lists attachment ${name}, which does not exist; pass the file with --attach`,
        );
}
function* quotes(s: Snapshot): Generator<Problem> {
  for (const d of decisions(s)) {
    if (!isAuthor(d) && casefold(strip(d.decidedBy)).includes("author"))
      yield problemAt(
        s,
        d.id,
        3,
        `decided_by is ${d.decidedBy}; write author exactly, with a quote, or use your own role`,
      );
    if (!isAuthor(d) || d.importedFrom !== null) continue;
    if (d.quote === null) {
      yield problemAt(
        s,
        d.id,
        3,
        "decided_by is author, but there is no quote; add quote: {text, where, when} with the author's words, or record it under your own role",
      );
      continue;
    }
    for (const [key, value] of [
      ["where", d.quote.where],
      ["when", d.quote.when],
    ] as const)
      if (!strip(value)) yield problemAt(s, d.id, 3, `quote.${key} is empty`);
  }
}
function* confirmations(s: Snapshot): Generator<Problem> {
  for (const d of decisions(s))
    if (d.confirms.length && !isAuthor(d))
      yield problemAt(
        s,
        d.id,
        3,
        `confirms is for author decisions, but decided_by is ${d.decidedBy}`,
      );
}
export function checkState(s: Snapshot): CheckResult {
  const found = [
    ...s.problems,
    ...fileNames(s),
    ...unresolved(s),
    ...codes(s),
    ...attachments(s),
    ...quotes(s),
    ...confirmations(s),
    ...checkAreas(s),
    ...checkCycles(s),
  ];
  found.sort((a, b) => {
    const x = sortKey(a),
      y = sortKey(b);
    return byCodePoint(x[0], y[0]) || x[1] - y[1] || byCodePoint(x[2], y[2]);
  });
  return {
    problems: found,
    notes: [],
    get ok() {
      return this.problems.length === 0;
    },
  };
}
