import { checkEntries } from "./check-entries.ts";
import { checkImmutable } from "./check-immutable.ts";
import {
  type CheckResult,
  checkResult,
  checkState,
  compareProblems,
  newDecisions,
  problemAt,
  sortKey,
} from "./check-state.ts";
import { derive } from "./derive.ts";
import { Action, type Problem, uniqueChanges } from "./model.ts";
import type { CoreSettings } from "./settings.ts";
import type { Snapshot } from "./snapshot.ts";
import { instant } from "./stamps.ts";
import { byCodePoint } from "./text.ts";

export function checkChange(
  published: Snapshot,
  after: Snapshot,
  settings: CoreSettings,
  now: string,
  current: Snapshot | null = null,
): CheckResult {
  const known = new Set(checkState(published).problems.map((p) => JSON.stringify(sortKey(p))));
  const problems: Problem[] = [],
    notes: string[] = [];
  for (const found of checkState(after).problems) {
    if (known.has(JSON.stringify(sortKey(found))))
      notes.push(`already published, check ${found.check}: ${found.path}: ${found.message}`);
    else problems.push(found);
  }
  problems.push(
    ...missing(published, after),
    ...dates(published, after, now, current),
    ...importsOverLive(published, after),
    ...checkEntries(published, after, settings),
    ...checkImmutable(published, after),
    ...linksToDead(published, after),
  );
  notes.push(...areaNotes(published, after));
  problems.sort(compareProblems);
  return checkResult(problems, notes);
}

function* missing(published: Snapshot, after: Snapshot): Generator<Problem> {
  const ids = new Set([
    ...published.decisions.keys(),
    ...published.entries.keys(),
    ...published.threads.keys(),
  ]);
  for (const id of [...ids].sort(byCodePoint))
    if (!after.decisions.has(id) && !after.entries.has(id) && !after.threads.has(id))
      yield problemAt(published, id, 2, "was published and is missing from this state");
}
function* dates(
  published: Snapshot,
  after: Snapshot,
  now: string,
  current: Snapshot | null,
): Generator<Problem> {
  const earlier = new Map([...published.decisions, ...(current?.decisions ?? [])]);
  for (const d of newDecisions(published, after)) {
    if (current?.decisions.has(d.id)) continue;
    if (instant(d.date) > instant(now))
      yield problemAt(after, d.id, 1, `dated ${d.date}, which is after the time of this change`);
    if (d.importedFrom !== null) continue;
    const entries = new Set(d.changes.map((c) => c.entry));
    for (const target of [...earlier.keys()].sort(byCodePoint)) {
      const old = earlier.get(target);
      if (!old) continue;
      let reason = "";
      if (d.replaces.includes(target)) reason = "which it replaces";
      else if (d.narrows.includes(target)) reason = "which it narrows";
      else if (d.confirms.includes(target)) reason = "which it confirms";
      else {
        const shared = [
          ...new Set(old.changes.map((c) => c.entry).filter((id) => entries.has(id))),
        ].sort(byCodePoint);
        if (shared.length) reason = `which shares ${shared[0]} with it`;
      }
      if (reason && instant(d.date) <= instant(old.date))
        yield problemAt(after, d.id, 1, `dated ${d.date}, no later than ${target}, ${reason}`);
    }
  }
}
function* importsOverLive(published: Snapshot, after: Snapshot): Generator<Problem> {
  const live = new Set(
    [...published.decisions.values()]
      .filter((d) => d.importedFrom === null)
      .flatMap((d) => d.changes.map((c) => c.entry)),
  );
  for (const d of newDecisions(published, after))
    if (d.importedFrom !== null)
      for (const entry of new Set(d.changes.map((c) => c.entry).filter((id) => live.has(id))))
        yield problemAt(
          after,
          d.id,
          1,
          `imported, changes ${entry}, which a live decision already changed`,
        );
}
function* linksToDead(published: Snapshot, after: Snapshot): Generator<Problem> {
  const status = derive(published).status,
    standing = derive(after).status;
  for (const id of [...after.entries.keys()].sort(byCodePoint)) {
    const e = after.entries.get(id);
    const previous = published.entries.get(id)?.restsOn ?? [];
    for (const target of new Set(e?.restsOn))
      if (!previous.includes(target) && standing.get(target) === "retired")
        yield problemAt(after, id, 6, `rests on ${target}, which is retired`);
  }
  for (const d of newDecisions(published, after)) {
    for (const [verb, targets] of [
      ["narrows", d.narrows],
      ["confirms", d.confirms],
    ] as const)
      for (const target of new Set(targets))
        if (status.get(target) === "replaced")
          yield problemAt(after, d.id, 6, `${verb} ${target}, which is replaced`);
    for (const change of uniqueChanges(d.changes)) {
      const retired =
        status.get(change.entry) === "retired" && standing.get(change.entry) === "retired";
      if (change.action !== Action.RETIRE && retired)
        yield problemAt(
          after,
          d.id,
          6,
          `changes ${change.entry} with action ${change.action}, but the entry is retired`,
        );
    }
  }
}
function* areaNotes(published: Snapshot, after: Snapshot): Generator<string> {
  for (const name of [...after.areas.keys()]
    .filter((n) => !published.areas.has(n))
    .sort(byCodePoint))
    yield `area ${name}: added`;
  for (const name of [...published.areas.keys()]
    .filter((n) => !after.areas.has(n))
    .sort(byCodePoint))
    yield `area ${name}: removed`;
  for (const name of [...published.areas.keys()]
    .filter((n) => after.areas.has(n))
    .sort(byCodePoint)) {
    const before = published.areas.get(name),
      now = after.areas.get(name);
    if (!before || !now) continue;
    for (const field of ["title", "intro", "order", "rank"] as const) {
      const a = before[field],
        b = now[field];
      const same =
        Array.isArray(a) && Array.isArray(b)
          ? a.length === b.length && a.every((v, i) => v === b[i])
          : a === b;
      if (!same) yield `area ${name}: ${field} changed`;
    }
  }
}
