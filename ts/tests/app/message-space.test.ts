import { expect, test } from "bun:test";
import { AddOutcome, LodgeError } from "#app";
import { Raises } from "#core";
import { project, raises, wired } from "./support.ts";

test.each([
  ["\u001c", null, "by needs a non-empty role"],
  ["author", "\u0085", "a message by author needs where, the place of the author's words"],
] as const)("message_strips_python_space %p %p", async (by, where, message) => {
  await raises(
    wired(project()).ask("s-aaaaaa", Raises.QUESTION, by, "Why?", { where }),
    LodgeError,
    message,
  );
});
test("message_keeps_bom_role", async () => {
  const result = await wired(project()).ask("s-aaaaaa", Raises.QUESTION, "\ufeff", "Why?");
  expect(result.outcome).toBe(AddOutcome.PUBLISHED);
  expect(result.ids).toEqual(["q-111111"]);
});
