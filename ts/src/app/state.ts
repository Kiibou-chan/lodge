import {
  AmbiguousRef,
  byCodePoint,
  type CheckResult,
  type CoreSettings,
  checkChange,
  checkResult,
  checkState,
  type Derived,
  derive,
  failingIds,
  load,
  resolve,
  type Snapshot,
  strip,
  type Tree,
  unrecordedProblems,
} from "#core";
import { LodgeError, NotFound } from "./errors.ts";
import type { Actor, Clock, IdSource, Store } from "./ports.ts";
import { type Read, read } from "./results.ts";
import { stampOf } from "./time.ts";

export interface Wiring {
  readonly actor: Actor;
  readonly store: Store;
  readonly clock: Clock;
  readonly ids: IdSource;
  readonly settings: CoreSettings;
}
export interface State {
  readonly current: Tree;
  readonly published: Tree;
  readonly snapshot: Snapshot;
  readonly derived: Derived;
  readonly result: CheckResult;
  readonly failing: ReadonlySet<string>;
  readonly read: Read;
}
// The current state read once, with its one-state checks.
export async function readState(store: Store): Promise<State> {
  const [current, published] = await store.trees();
  const snapshot = load(current),
    result = checkState(snapshot),
    derived = derive(snapshot);
  return {
    current,
    published,
    snapshot,
    derived,
    result,
    failing: failingIds(snapshot, result),
    read: read({
      freshness: await store.freshness(),
      unrecorded: unrecordedProblems(snapshot, result),
      statuses: derived.status,
    }),
  };
}
// Fold the checks against the published tree into the failing records.
export async function readChecked(w: Wiring): Promise<State> {
  const state = await readState(w.store);
  const change = checkChange(
    load(state.published),
    state.snapshot,
    w.settings,
    stampOf(w.clock.now()),
  );
  const known = new Set(state.result.problems.map((p) => JSON.stringify(p)));
  const problems = [
    ...state.result.problems,
    ...change.problems.filter((p) => !known.has(JSON.stringify(p))),
  ];
  problems.sort(
    (a, b) => byCodePoint(a.path, b.path) || a.check - b.check || byCodePoint(a.message, b.message),
  );
  const result = checkResult(problems, state.result.notes);
  return {
    ...state,
    result,
    failing: failingIds(state.snapshot, result),
    read: { ...state.read, unrecorded: unrecordedProblems(state.snapshot, result) },
  };
}
export function resolveRef(state: State, ref: string): string {
  let found: string | null;
  try {
    found = resolve(state.snapshot, ref);
  } catch (error) {
    if (!(error instanceof AmbiguousRef)) throw error;
    throw new LodgeError(error.message, { cause: error });
  }
  if (found === null) throw notFound(state, `record named ${ref}`, ref);
  return found;
}
export function notFound(state: State, what: string, needle: string): NotFound {
  const paths = state.read.unrecorded.filter((p) => p.check === 1).map((p) => p.path);
  const matching = paths.filter((p) => p.toLowerCase().includes(strip(needle).toLowerCase()));
  const named = matching.length ? matching : paths;
  return new NotFound(
    named.length
      ? `no ${what}; lodge could not read ${named.join(", ")}, which may hold it`
      : `no ${what}`,
  );
}
