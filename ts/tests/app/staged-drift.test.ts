import { expect, test } from "bun:test";
import { AddOutcome } from "#app";
import { Raises, writeRecord } from "#core";
import { filesOf, thread } from "../core/builders.ts";
import { FIRST, project, wired } from "./support.ts";

function drift() {
  const store = project({ staged: true });
  for (const path of store.files.keys())
    if (path.startsWith("lodge/decisions/")) store.files.delete(path);
  return store;
}
test.each(["ask", "reply"] as const)("%s_checks_against_the_published_tree", async (operation) => {
  const store = drift();
  const existing = filesOf(thread({ id: "q-aaaaaa" }));
  for (const [path, text] of existing) {
    store.files.set(path, text);
    store.published.set(path, text);
  }
  const lodge = wired(store);
  const result =
    operation === "ask"
      ? await lodge.ask("s-aaaaaa", Raises.DOUBT, "coordinator", "Why?")
      : await lodge.reply("q-aaaaaa", "coordinator", "Because.");
  expect(result.outcome).toBe(AddOutcome.CHECK_FAILED);
  expect(result.check.ok).toBe(false);
  expect(store.publishes).toEqual([]);
  expect(store.attempts).toBe(0);
});
test("add_refuses_a_rewrite_already_present_in_current", async () => {
  const store = drift();
  const text = writeRecord({ ...FIRST, statement: "Changed." });
  const path = [...store.published.keys()].find((path) => path.startsWith("lodge/decisions/"));
  if (!path) throw new Error("missing published decision");
  store.files.set(path, text);
  const lodge = wired(store);
  const result = await lodge.add([["rewrite.md", await lodge.draft("d-aaaaaa")]]);
  expect(result.outcome).toBe(AddOutcome.CHECK_FAILED);
  expect(result.check.ok).toBe(false);
  expect(store.publishes).toEqual([]);
  expect(store.attempts).toBe(0);
});
