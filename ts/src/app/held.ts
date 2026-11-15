import { cleanText } from "#core";
import { Forbidden, LodgeError, NotFound } from "./errors.ts";
import type { Held, HeldAdd } from "./ports.ts";
import type { Approved } from "./results.ts";
import type { Wiring } from "./state.ts";
import { writeMessage } from "./threads.ts";
import { add } from "./writes.ts";

export async function held(w: Wiring): Promise<readonly Held[]> {
  return w.store.held();
}
async function authorised<K extends Held["kind"] = Held["kind"]>(
  w: Wiring,
  seq: number,
  kind?: K,
): Promise<Extract<Held, { kind: K }>> {
  const found = (await w.store.held()).find(
    (h): h is Extract<Held, { kind: K }> =>
      h.seq === seq && (kind === undefined || h.kind === kind),
  );
  if (!found) throw new NotFound(`nothing is held under number ${seq}`);
  if (w.actor.kind !== "person" || w.actor.name !== found.person)
    throw new Forbidden(`only ${found.person} approves this; nothing was written`);
  return found;
}
export async function approve(w: Wiring, seq: number): Promise<Approved> {
  const initial = await authorised(w, seq);
  if (initial.kind === "message") {
    return {
      kind: "message",
      written: await writeMessage(
        w,
        initial.ref,
        initial.raises,
        initial.person,
        initial.text ?? "",
        { where: initial.where, when: initial.when, close: initial.operation === "close" },
        seq,
      ),
    };
  }
  const refresh = (): Promise<HeldAdd> => authorised(w, seq, "add");
  const found = await refresh();
  return {
    kind: "add",
    added: await add(
      w,
      found.drafts,
      {
        importing: found.importing,
        attachments: found.attachments,
      },
      { seq, refresh },
    ),
  };
}
export async function decline(w: Wiring, seq: number, reason: string): Promise<void> {
  await authorised(w, seq);
  reason = cleanText(reason);
  if (!reason) throw new LodgeError("a reason is required; nothing was written");
  await w.store.decline(seq, reason);
}
