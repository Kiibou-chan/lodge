import { expect, test } from "bun:test";
import {
  Action,
  type Change,
  confirmableIds,
  derive,
  feedback,
  lengthGuidance,
  load,
  type Record,
  tree,
  writeThread,
} from "#core";
import { at, decision, entry, filesOf, message, thread } from "./builders.ts";

const people = new Set(["ada"]);
const quote = { text: "Do it.", where: "a session", when: "2026-10-28 10:00" };
const s = (...items: Record[]) => load(tree({ rev: null, files: filesOf(...items), people }));

test("confirmable_and_confirmed_by_follow_the_person", () => {
  const own = decision({ decidedBy: "ada", quote });
  const agent = decision({ date: at(1) });
  const before = s(own, agent);
  expect(confirmableIds(before, derive(before))).toEqual(new Set([agent.id]));
  const c = decision({ decidedBy: "ada", quote, date: at(2), confirms: [agent.id] });
  const after = s(own, agent, c);
  expect(derive(after).confirmedBy.get(agent.id)).toEqual([c.id]);
});
test("own_replacement_is_not_flagged", () => {
  const d1 = decision({ decidedBy: "ada", quote });
  const d2 = decision({ decidedBy: "ada", quote, date: at(1), replaces: [d1.id] });
  expect(derive(s(d1, d2)).awaitingAuthor).toEqual(new Set());
});
test("agent_replaces_a_decision_she_confirmed", () => {
  const a = decision({ decidedBy: "ada", quote, date: at(0) });
  const first = decision({ date: at(1), narrows: [a.id] });
  const c = decision({ decidedBy: "ada", quote, date: at(2), confirms: [first.id] });
  const second = decision({ date: at(3), replaces: [first.id] });
  expect(derive(s(a, first, c, second)).awaitingAuthor).toEqual(new Set([second.id]));
});
test("agent_edit_after_she_replaced_an_agent_edit_flagged", () => {
  const spec = entry();
  const change: readonly Change[] = [{ entry: spec.id, action: Action.EDIT }];
  const a = decision({ decidedBy: "ada", quote, date: at(0), changes: change });
  const agent1 = decision({ date: at(1), changes: change });
  const hers = decision({ decidedBy: "ada", quote, date: at(2), replaces: [agent1.id] });
  const agent2 = decision({ date: at(3), changes: change });
  expect(derive(s(spec, a, agent1, hers, agent2)).awaitingAuthor).toEqual(new Set([agent2.id]));
});
test("touched_by_flagged_names_her_entry_edit", () => {
  const spec = entry();
  const change: readonly Change[] = [{ entry: spec.id, action: Action.EDIT }];
  const a = decision({ decidedBy: "ada", quote, date: at(0), changes: change });
  const agent = decision({ date: at(1), changes: change });
  const got = derive(s(spec, a, agent));
  expect(got.touchedByFlagged.get(a.id)).toEqual([agent.id]);
});
test("edit_back_asked_of_a_person", () => {
  const spec = entry();
  const a = decision({
    decidedBy: "ada",
    quote,
    date: at(0),
    changes: [{ entry: spec.id, action: Action.CREATE }],
  });
  const agent = decision({ date: at(1), changes: [{ entry: spec.id, action: Action.EDIT }] });
  const added = decision({ decidedBy: "ada", quote, date: at(2), replaces: [agent.id] });
  const after = s(spec, a, agent, added);
  expect(feedback([added], after, derive(after), lengthGuidance()).map((f) => f.message)).toEqual([
    `it replaces ${agent.id}, whose edit of ${spec.id} is still the latest edit of that entry; does ${added.id} edit ${spec.id} back? If so, add an edit draft of ${spec.id} and list it in changes with action edit`,
  ]);
});
test("person_message_writes_a_quoted_minute", () => {
  const t = thread({ messages: [message({ by: "ada", when: quote.when, where: quote.where })] });
  expect(writeThread(t, people)).toContain(`when: "${quote.when}"`);
});
test("agent_edit_after_she_corrected_her_own_edit_flagged", () => {
  const spec = entry();
  const change: readonly Change[] = [{ entry: spec.id, action: Action.EDIT }];
  const first = decision({ decidedBy: "ada", quote, date: at(0), changes: change });
  const fix = decision({ decidedBy: "ada", quote, date: at(1), replaces: [first.id] });
  const agent = decision({ date: at(2), changes: change });
  expect(derive(s(spec, first, fix, agent)).awaitingAuthor).toEqual(new Set([agent.id]));
});
test("no_edit_back_when_she_replaces_her_own", () => {
  const spec = entry();
  const a = decision({
    decidedBy: "ada",
    quote,
    date: at(0),
    changes: [{ entry: spec.id, action: Action.CREATE }],
  });
  const mine = decision({
    decidedBy: "ada",
    quote,
    date: at(1),
    changes: [{ entry: spec.id, action: Action.EDIT }],
  });
  const added = decision({ decidedBy: "ada", quote, date: at(2), replaces: [mine.id] });
  const after = s(spec, a, mine, added);
  expect(feedback([added], after, derive(after), lengthGuidance())).toEqual([]);
});
