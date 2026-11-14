import { PublishOutcome } from "#app";
import type { Area, Decision, SpecEntry } from "#core";
import { filesOf } from "../core/builders.ts";
import { setup } from "./support.ts";

export async function seeded(...items: (Area | Decision | SpecEntry)[]) {
  const { database, store } = await setup("storage-notes", "author");
  if (
    (await store.publish((await store.trees())[0], filesOf(...items), "seed")) !==
    PublishOutcome.PUBLISHED
  )
    throw new Error("seed did not publish");
  return { database, store };
}
