import { expect, test } from "bun:test";
import {
  checkState,
  confirmationDraft,
  derive,
  isAuthor,
  level1,
  load,
  parseThread,
  Scope,
  tree,
  ValueError,
  writeThread,
} from "#core";
import { at, decision, filesOf, message, thread } from "./builders.ts";
import { check } from "./checks.ts";

const people = new Set(["ada", "bo"]);
const quote = { text: "Do it.", where: "a session", when: "2026-10-28 10:00" };
function snapshot(...items: Parameters<typeof filesOf>) {
  return load(tree({ rev: null, files: filesOf(...items), people }));
}
function problems(d: ReturnType<typeof decision>) {
  return checkState(snapshot(d)).problems.map((p) => p.message);
}
test("a_person_is_a_name_in_people", () => {
  expect(isAuthor(decision({ decidedBy: "ada" }), people)).toBe(true);
  expect(isAuthor(decision({ decidedBy: "author" }), people)).toBe(false);
  expect(isAuthor(decision({ decidedBy: "builder" }), people)).toBe(false);
});
test("tree_defaults_to_lodge_0_2_people", () => {
  const t = tree({ rev: null, files: new Map() });
  expect(t.people).toEqual(new Set(["author"]));
  expect(load(t).people).toBe(t.people);
  expect(snapshot().people).toBe(people);
});
test("person_decision_needs_a_quote", () => {
  const d = decision({ decidedBy: "ada" });
  expect(problems(d)).toContain(
    `${d.id}: decided_by is ada, but there is no quote; add quote: {text, where, when} with ada's words, or record it under your own role`,
  );
  expect(problems(decision({ decidedBy: "ada", quote }))).toEqual([]);
});
test("author_is_a_role_where_no_person_is_author", () => {
  const d = decision({ decidedBy: "author" });
  expect(problems(d)).toContain(
    `${d.id}: decided_by is author; name a person of the project exactly, with a quote, or use your own role`,
  );
});
test("confirms_is_for_a_person", () => {
  const d = decision({ confirms: ["d-aaaaaa"] });
  expect(problems(d)).toContain(
    `${d.id}: confirms is for a person's decisions, but decided_by is coordinator`,
  );
  expect(
    problems(decision({ decidedBy: "ada", quote, confirms: ["d-aaaaaa"] })).some((m) =>
      m.includes("confirms is for"),
    ),
  ).toBe(false);
});
test("immutable_names_the_person", () => {
  const d = decision({ decidedBy: "ada", quote, reasoning: "Before." });
  expect(
    check(snapshot(d), snapshot({ ...d, reasoning: "After." })).problems.map((p) => p.message),
  ).toEqual([
    `${d.id}: reasoning of a published decision of ada was changed; a correction or a shorter reasoning is a new decision that replaces it`,
  ]);
});
test("quote_and_unquoted_follow_the_person", () => {
  const d = decision({ decidedBy: "ada", quote });
  const s = snapshot(d);
  expect(level1(s, derive(s), d.id, new Set()).quote).toEqual(quote);
  const imported = { ...d, quote: null, importedFrom: { file: "notes.md", heading: "Storage" } };
  const old = snapshot(imported);
  expect(level1(old, derive(old), d.id, new Set()).flags).toContain("unquoted");
});
test("person_message_needs_where_and_a_minute", () => {
  const t = thread({ messages: [message({ by: "ada", when: quote.when, where: quote.where })] });
  const text = writeThread(t, people);
  expect(parseThread("thread", text, people)).toEqual(t);
  expect(
    load(
      tree({ rev: null, files: new Map([[`lodge/threads/${t.id}.md`, text]]), people }),
    ).threads.get(t.id),
  ).toEqual(t);
  const missing = text.replace('where: "a session"\n', "");
  expect(parseThread("thread", missing, people)).toMatchObject({
    kind: "problem",
    message: "a message by ada needs where",
  });
  expect(() =>
    writeThread(
      { ...t, messages: [message({ by: "ada", when: quote.when, where: null })] },
      people,
    ),
  ).toThrow(ValueError);
  expect(parseThread("thread", text)).toMatchObject({ kind: "problem" });
});
test("confirmation_draft_names_the_person", () => {
  const text = confirmationDraft(["d-aaaaaa"], Scope.PRODUCT, "Agreed.", quote.when, null, "ada");
  expect(text).toContain("decided_by: ada\n");
  expect(text).toContain("ada confirms d-aaaaaa.");
});
test("agent_change_to_a_persons_decision_is_flagged", () => {
  const d = decision({ decidedBy: "ada", quote });
  const agent = decision({ date: at(1), replaces: [d.id] });
  const s = snapshot(d, agent);
  expect(derive(s).awaitingAuthor).toEqual(new Set([agent.id]));
  const confirmed = snapshot(
    d,
    agent,
    decision({ decidedBy: "ada", quote, date: at(2), confirms: [agent.id] }),
  );
  expect(derive(confirmed).awaitingAuthor).toEqual(new Set());
});
