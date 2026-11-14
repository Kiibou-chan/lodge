import { expect, test } from "bun:test";
import { Action, derive, feedback, lengthGuidance, level1, load, tree } from "#core";
import { at, decision, entry, filesOf } from "./builders.ts";

const people = new Set(["bo", "ada"]);
const quote = { text: "Agreed.", where: "a session", when: "2026-10-28 10:00" };
const ada = decision({ decidedBy: "ada", quote });
const bo = decision({ decidedBy: "bo", quote });
const agent = decision({ date: at(1), narrows: [ada.id] });
function snapshot(...items: Parameters<typeof filesOf>) {
  return load(tree({ rev: null, files: filesOf(...items), people }));
}
function flags(s: ReturnType<typeof snapshot>, id: string) {
  return level1(s, derive(s), id, new Set()).flags;
}
test("flag_waits_for_the_person_whose_decision_it_touches", () => {
  const s = snapshot(ada, agent);
  expect(derive(s).awaiting).toEqual(new Map([[agent.id, ["ada"]]]));
  expect(flags(s, agent.id)).toContain("awaiting ada");
  expect(flags(s, ada.id)).toContain(`awaiting ada on ${agent.id}`);
});
test("another_persons_confirmation_leaves_it", () => {
  const s = snapshot(
    ada,
    agent,
    decision({ decidedBy: "bo", quote, date: at(2), confirms: [agent.id] }),
  );
  expect(derive(s).awaitingAuthor).toEqual(new Set([agent.id]));
});
test("that_persons_confirmation_clears_it", () => {
  const s = snapshot(
    ada,
    agent,
    decision({ decidedBy: "ada", quote, date: at(2), confirms: [agent.id] }),
  );
  expect(derive(s).awaiting).toEqual(new Map());
});
test("that_persons_replacement_clears_it", () => {
  const s = snapshot(
    ada,
    agent,
    decision({ decidedBy: "ada", quote, date: at(2), replaces: [agent.id] }),
  );
  expect(derive(s).awaiting).toEqual(new Map());
});
test("touching_two_people_waits_for_both", () => {
  const both = { ...agent, narrows: [bo.id, ada.id] };
  const s = snapshot(ada, bo, both);
  expect(derive(s).awaiting.get(agent.id)).toEqual(["ada", "bo"]);
  expect(flags(s, agent.id)).toContain("awaiting ada and bo");
  const confirmed = snapshot(
    ada,
    bo,
    both,
    decision({ decidedBy: "ada", quote, date: at(2), confirms: [agent.id] }),
  );
  expect(flags(confirmed, agent.id)).toContain("awaiting bo");
  expect(derive(confirmed).awaiting.get(agent.id)).toEqual(["bo"]);
});
test("a_confirmed_agent_text_counts_for_its_confirmer", () => {
  const spec = entry();
  const changes = [{ entry: spec.id, action: Action.EDIT }];
  const first = decision({ changes });
  const confirmation = decision({ decidedBy: "bo", quote, date: at(1), confirms: [first.id] });
  const edit = decision({ changes, date: at(2) });
  const s = snapshot(spec, first, confirmation, edit);
  expect(derive(s).awaiting.get(edit.id)).toEqual(["bo"]);
  expect(flags(s, spec.id)).toContain(`awaiting bo on ${edit.id}`);
});
test("feedback_names_who_it_waits_for", () => {
  const s = snapshot(ada, agent);
  expect(feedback([agent], s, derive(s), lengthGuidance()).map((f) => f.message)).toContain(
    "this decision will wait for ada: it takes effect at once, and a later decision of ada that confirms or replaces it clears the flag",
  );
});
test("confirmed_by_names_each_person", () => {
  const a = decision({ decidedBy: "ada", quote, date: at(2), confirms: [agent.id] });
  const b = decision({ decidedBy: "bo", quote, date: at(3), confirms: [agent.id] });
  const s = snapshot(ada, agent, b, a);
  expect(flags(s, agent.id)).toContain(`confirmed by ada (${a.id}) and bo (${b.id})`);
});
