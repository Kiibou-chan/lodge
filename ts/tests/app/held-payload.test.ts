import { expect, test } from "bun:test";
import { AddOutcome, person } from "#app";
import { CountingIds } from "./fakes.ts";
import { draft, setup } from "./held-support.ts";
import { wired } from "./support.ts";

test.each([false, true])("a_held_add_keeps_its_payload (importing %s)", async (importing) => {
  const { store, clock, lodge } = setup();
  const drafts = [
    ["d.md", draft().replace("scope: process", "scope: process\nattachments: [a.txt]")],
  ] as const;
  const attachments = [["a.txt", "Kept attachment.\n"]] as const;
  const options = { importing, attachments };
  const held = await lodge.add(drafts, options);
  expect(held.outcome).toBe(AddOutcome.HELD);
  const direct = setup(person("ada"));
  expect((await direct.lodge.add(drafts, options)).outcome).toBe(AddOutcome.PUBLISHED);
  const message = direct.store.publishes[0]?.[1];
  expect(message).toBeTruthy();
  expect(await lodge.held()).toMatchObject([{ attachments, importing, message }]);
  const ada = wired(store, clock, new CountingIds(), person("ada"));
  const approved = await ada.approve(held.held as number);
  expect(approved.kind).toBe("add");
  if (approved.kind !== "add") throw new Error("expected add");
  expect(approved.added.outcome).toBe(AddOutcome.PUBLISHED);
  const path = `lodge/attachments/${approved.added.ids[0]}/a.txt`;
  expect(approved.added.paths).toContain(path);
  expect(store.files.get(path)).toBe(attachments[0][1]);
  expect(store.publishes[0]?.[1]).toBe(message);
  expect(await ada.held()).toEqual([]);
});
