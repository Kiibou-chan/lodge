import { cleanText } from "#core";
import { Forbidden, LodgeError, NotFound } from "./errors.ts";
import type { Held, HeldAdd } from "./ports.ts";
import type { Approved } from "./results.ts";
import type { Wiring } from "./state.ts";
import { add } from "./writes.ts";

export async function held(w: Wiring): Promise<readonly Held[]> {
  return w.store.held();
}
async function authorised(w: Wiring, seq: number): Promise<Held> {
  const found = (await w.store.held()).find((h) => h.seq === seq);
  if (!found) throw new NotFound(`nothing is held under number ${seq}`);
  if (w.actor.kind !== "person" || w.actor.name !== found.person)
    throw new Forbidden(`only ${found.person} approves this; nothing was written`);
  return found;
}
export async function approve(w: Wiring, seq: number): Promise<Approved> {
  const refresh = async (): Promise<HeldAdd> => {
    const found = await authorised(w, seq);
    if (found.kind === "message")
      throw new LodgeError(`hold ${seq} is a thread message, which this build cannot approve yet`);
    return found;
  };
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
