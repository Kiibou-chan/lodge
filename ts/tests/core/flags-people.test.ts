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
test("a_persons_decision_is_not_flagged_for_another", () => {
  const spec = entry();
  const changes = [{ entry: spec.id, action: Action.EDIT }];
  for (const own of [
    decision({ decidedBy: "bo", quote, date: at(1), narrows: [ada.id] }),
    decision({ decidedBy: "bo", quote, date: at(1), changes }),
  ]) {
    const s = snapshot(spec, { ...ada, changes }, own);
    expect(derive(s).awaiting).toEqual(new Map());
    expect(
      feedback([own], s, derive(s), lengthGuidance())
        .map((f) => f.message)
        .filter((message) => message.startsWith("this decision will wait for")),
    ).toEqual([]);
  }
});
test("entry_waiting_people_are_in_code_point_order", () => {
  const spec = entry();
  const changes = [{ entry: spec.id, action: Action.EDIT }];
  const first = decision({ date: at(1), changes, narrows: [ada.id] });
  const second = decision({ date: at(2), changes, narrows: [bo.id] });
  const s = snapshot(spec, ada, bo, first, second);
  expect(flags(s, spec.id)).toContain(`awaiting ada and bo on ${second.id}, ${first.id}`);
});
test("three_waiting_people_have_an_oxford_comma", () => {
  const cy = decision({ decidedBy: "cy", quote });
  const edit = decision({ date: at(1), narrows: [cy.id, bo.id, ada.id] });
  const s = load(
    tree({ rev: null, files: filesOf(ada, bo, cy, edit), people: new Set(["cy", "bo", "ada"]) }),
  );
  expect(flags(s, edit.id)).toContain("awaiting ada, bo, and cy");
});
test("behind_edits_count_only_for_people_still_waited_for", () => {
  const spec = entry();
  const changes = [{ entry: spec.id, action: Action.EDIT }];
  const first = { ...ada, changes };
  const edit = decision({ date: at(1), changes, narrows: [bo.id] });
  const confirmation = decision({ decidedBy: "ada", quote, date: at(2), confirms: [edit.id] });
  const s = snapshot(spec, first, bo, edit, confirmation);
  expect(derive(s).awaiting.get(edit.id)).toEqual(["bo"]);
  expect(derive(s).touchedByFlagged.has(first.id)).toBe(false);
});
