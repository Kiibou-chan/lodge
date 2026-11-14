import {
  cleanText,
  confirmableIds,
  confirmationDraft,
  behindArea as coreBehindArea,
  level1,
  Scope,
  ValueError,
  VIEWER,
} from "#core";
import { Forbidden, LodgeError, StaleList } from "./errors.ts";
import { AddOutcome, type Behind, type Written, written } from "./results.ts";
import { notFound, readState, type State, type Wiring } from "./state.ts";
import { minuteOf } from "./time.ts";
import { add } from "./writes.ts";

function behindIds(state: State, name: string): readonly string[] {
  const s = state.snapshot;
  if (!s.areas.has(name) && [...s.entries.values()].every((e) => e.area !== name))
    throw notFound(state, `area named ${name}`, name);
  return coreBehindArea(s, state.derived, name);
}
export async function behindArea(w: Wiring, name: string): Promise<readonly Behind[]> {
  const state = await readState(w.store);
  const s = state.snapshot;
  return behindIds(state, name).map((id) => ({
    decision: level1(s, state.derived, id, state.failing),
    entries: [...new Set(s.decisions.get(id)?.changes.map((c) => c.entry))].flatMap((id) => {
      const e = s.entries.get(id);
      return e ? [[id, e.area] as const] : [];
    }),
  }));
}
function expectedIds(state: State, ids: readonly string[], area: string | null): readonly string[] {
  if (area !== null) return behindIds(state, area);
  if (ids.length === 1 && confirmableIds(state.snapshot, state.derived).has(ids[0] ?? ""))
    return ids;
  return [];
}
// Callers serialise confirmations across this entire operation, including retries and commit.
export async function confirmDecisions(
  w: Wiring,
  ids: readonly string[],
  words: string,
  area: string | null,
  commit: boolean,
): Promise<Written> {
  words = cleanText(words);
  if (words.includes("\r\n"))
    throw new LodgeError("your words hold a character lodge cannot store");
  if (!words) throw new LodgeError("your words are required; nothing was written");
  if (w.actor.kind !== "person") throw new Forbidden("only a person confirms; nothing was written");
  const state = await readState(w.store);
  if (!state.snapshot.people.has(w.actor.name))
    throw new Forbidden("only an owner of the project confirms; nothing was written");
  const expected = expectedIds(state, ids, area);
  const given = new Set(ids);
  if (!expected.length || ids.length !== expected.length || expected.some((id) => !given.has(id)))
    throw new StaleList("the list changed since the page was loaded; nothing was written");
  const scope = expected.some((id) => state.snapshot.decisions.get(id)?.scope === Scope.PRODUCT)
    ? Scope.PRODUCT
    : Scope.PROCESS;
  let draft: string;
  try {
    draft = confirmationDraft(expected, scope, words, minuteOf(w.clock.now()), area, w.actor.name);
  } catch (error) {
    if (!(error instanceof ValueError)) throw error;
    throw new LodgeError("your words hold a character lodge cannot store", { cause: error });
  }
  const added = await add(w, [[VIEWER, draft]]);
  const committed =
    added.outcome === AddOutcome.STAGED && commit
      ? await w.store.commit(added.paths, `Author confirmation from the viewer: ${added.ids[0]}`)
      : null;
  return written({ ids: added.ids, outcome: added.outcome, check: added.check, committed });
}
