import {
  applyDrafts,
  areaFeedback,
  attachmentPath,
  checkChange,
  type Draft,
  derive,
  feedback,
  instant,
  load,
  mintId,
  type Problem,
  parseDraft,
  type Record,
  rstrip,
  type Snapshot,
  tree,
} from "#core";
import { awaitsPerson } from "./awaits.ts";
import { Conflict, LodgeError } from "./errors.ts";
import {
  actorText,
  type Clock,
  type HeldAdd,
  type IdSource,
  type Now,
  PublishOutcome,
} from "./ports.ts";
import { type Added, AddOutcome, added } from "./results.ts";
import { readState, type State, type Wiring } from "./state.ts";
import { stampOf } from "./time.ts";
import { attached, requireListed } from "./write-attachments.ts";

const MINT_DRAWS = 10,
  ATTEMPTS = 3,
  WAITS = 3;
interface Request {
  readonly drafts: readonly Draft[];
  readonly raw: readonly (readonly [string, string])[];
  readonly attachments: readonly (readonly [string, string])[];
  readonly approves: number | null;
  readonly importing: boolean;
  readonly dryRun: boolean;
  readonly attached: ReadonlyMap<string, string>;
}
export interface AddOptions {
  readonly importing?: boolean;
  readonly dryRun?: boolean;
  readonly attachments?: readonly (readonly [string, string])[];
}
export async function mint(w: Wiring, prefix: "d" | "s"): Promise<string> {
  const s = (await readState(w.store)).snapshot;
  return mintUnused(w.ids, prefix, new Set([...s.decisions.keys(), ...s.entries.keys()]));
}
// A rejected publish starts again from reading the store.
export async function add(
  w: Wiring,
  drafts: readonly (readonly [string, string])[],
  { importing = false, dryRun = false, attachments = [] }: AddOptions = {},
  approval: { readonly seq: number; readonly refresh: () => Promise<HeldAdd> } | null = null,
): Promise<Added> {
  const parsed = parse(drafts);
  let request: Request = {
    drafts: parsed,
    raw: drafts,
    attachments,
    approves: approval?.seq ?? null,
    importing,
    dryRun,
    attached: attached(attachments, parsed),
  };
  let first: Snapshot | null = null;
  for (let i = 0; i < ATTEMPTS; i++) {
    if (approval) {
      const fresh = await approval.refresh();
      const parsed = parse(fresh.drafts);
      request = {
        ...request,
        raw: fresh.drafts,
        drafts: parsed,
        importing: fresh.importing,
        attachments: fresh.attachments,
        attached: attached(fresh.attachments, parsed),
      };
    }
    const state = await readState(w.store);
    first ??= state.snapshot;
    const result = await attempt(w, state, first, request);
    if (result !== null) return result;
  }
  if (approval) await approval.refresh();
  throw new Conflict(
    "other changes reached the store three times while this one was being published; nothing was written, so add the drafts again",
  );
}
async function attempt(
  w: Wiring,
  state: State,
  first: Snapshot,
  request: Request,
): Promise<Added | null> {
  const { drafts, importing } = request,
    s = state.snapshot;
  const now = await afterNewest(w.clock, s),
    newIds: string[] = [];
  for (const d of drafts) {
    if (d.kind === "decision" && !d.header.has("id"))
      newIds.push(
        mintUnused(w.ids, "d", new Set([...s.decisions.keys(), ...s.entries.keys(), ...newIds])),
      );
  }
  const applied = applyDrafts(s, state.current, drafts, newIds, stampOf(now), importing);
  if (Array.isArray(applied)) throw refusal(applied, raced(drafts, first, s));
  const current = state.current;
  const files = new Map([...applied.files].filter(([p, t]) => current.files.get(p) !== t));
  const placed = new Map(
    [...request.attached].map(([name, text]) => [
      attachmentPath(required(newIds[0], "minted ID"), name),
      text,
    ]),
  );
  const after = load(
    tree({
      rev: current.rev,
      people: current.people,
      files: new Map([...current.files, ...files]),
      attachments: new Set([...current.attachments, ...placed.keys()]),
    }),
  );
  if (request.attached.size)
    requireListed(
      required(after.decisions.get(required(newIds[0], "minted ID")), "applied decision"),
      request.attached,
    );
  const check = checkChange(load(state.published), after, w.settings, stampOf(now), s);
  const notes = [
    ...feedback(written(s, after, applied.ids), after, derive(after), w.settings.length),
    ...areaFeedback(after, [...files.keys()]),
  ];
  if (!check.ok)
    return added({
      ids: applied.ids,
      feedback: notes,
      check,
      outcome: AddOutcome.CHECK_FAILED,
      freshness: state.read.freshness,
      minted: newIds,
    });
  const awaits = awaitsPerson(s, after, w.actor);
  if (request.dryRun)
    return added({
      ids: applied.ids,
      feedback: notes,
      check,
      outcome: AddOutcome.DRY_RUN,
      awaits,
      minted: newIds,
    });
  if (awaits !== null) {
    const held = await w.store.hold({
      kind: "add",
      person: awaits,
      by: actorText(w.actor),
      drafts: request.raw,
      attachments: request.attachments,
      importing,
      message: message(after, applied.ids),
    });
    return added({
      ids: applied.ids,
      feedback: notes,
      check,
      outcome: AddOutcome.HELD,
      minted: newIds,
      awaits,
      held,
    });
  }
  if (!files.size && request.approves === null)
    return added({ ids: applied.ids, feedback: notes, check, outcome: AddOutcome.UNCHANGED });
  const outcome = await w.store.publish(
    current,
    new Map([...files, ...placed]),
    message(after, applied.ids),
    request.approves,
  );
  if (outcome === PublishOutcome.REJECTED) return null;
  return added({
    ids: applied.ids,
    feedback: notes,
    check,
    outcome: outcome === PublishOutcome.PUBLISHED ? AddOutcome.PUBLISHED : AddOutcome.STAGED,
    paths: [...files.keys(), ...placed.keys()],
  });
}
// Wait until the clock's whole second follows the newest decision, up to three waits.
async function afterNewest(clock: Clock, s: Snapshot): Promise<Now> {
  const dates = [...s.decisions.values()].map((d) => instant(d.date));
  const newest = dates.length ? Math.max(...dates) : null;
  let now = clock.now();
  if (newest !== null && (newest - now.epochMs) / 1000 > WAITS) return now;
  for (let i = 0; i < WAITS; i++) {
    if (newest === null || Math.floor(now.epochMs / 1000) * 1000 > newest) break;
    await clock.sleep(1 - (now.epochMs % 1000) / 1000);
    now = clock.now();
  }
  return now;
}
function parse(drafts: readonly (readonly [string, string])[]): Draft[] {
  if (!drafts.length) throw new LodgeError("no drafts to add");
  const parsed = drafts.map(([source, text]) => parseDraft(source, text));
  const problems = parsed.filter((p): p is Problem => p.kind === "problem");
  if (problems.length) throw refusal(problems);
  return parsed.filter((d): d is Draft => d.kind !== "problem");
}
function refusal(problems: readonly Problem[], raced = false): LodgeError {
  const lines = problems.map((p) => `${p.path}${p.line ? `:${p.line}` : ""}: ${p.message}`);
  const conflict = raced || problems.some((p) => "stale" in p && p.stale === true);
  return new (conflict ? Conflict : LodgeError)(lines.join("\n"));
}
function raced(drafts: readonly Draft[], first: Snapshot, now: Snapshot): boolean {
  for (const draft of drafts) {
    if (draft.kind === "area") {
      const name = draft.header.get("name");
      if (typeof name === "string" && now.areas.has(name) && !first.areas.has(name)) return true;
    } else if (draft.kind === "spec") {
      const id = draft.header.get("id");
      if (typeof id === "string" && now.entries.has(id) && !first.entries.has(id)) return true;
    }
  }
  return false;
}
export function mintUnused(
  ids: IdSource,
  prefix: "d" | "s" | "q",
  taken: ReadonlySet<string>,
): string {
  for (let i = 0; i < MINT_DRAWS; i++) {
    const candidate = mintId(prefix, ids.entropy());
    if (!taken.has(candidate)) return candidate;
  }
  throw new LodgeError("no unused ID was found in ten draws");
}
function written(before: Snapshot, after: Snapshot, ids: readonly string[]): Record[] {
  const found: Record[] = [];
  for (const id of ids) {
    const entry = after.entries.get(id),
      decision = after.decisions.get(id);
    if (entry) found.push(entry);
    else if (decision && !before.decisions.has(id)) found.push(decision);
  }
  return found;
}
function message(after: Snapshot, ids: readonly string[]): string {
  const records = new Map<string, Record>([...after.decisions, ...after.entries]);
  const title = ids.length
    ? required(records.get(required(ids[0], "written ID")), "applied record").title
    : "";
  return rstrip(`lodge: add ${ids.join(", ") || "areas"} ${title}`);
}

function required<T>(value: T | undefined, what: string): T {
  if (value === undefined) throw new Error(`missing ${what}`);
  return value;
}
