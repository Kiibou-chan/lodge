import { expect, test } from "bun:test";
import {
  Action,
  derive,
  type Feedback,
  feedback,
  lengthGuidance,
  type Record,
  type Snapshot,
} from "#core";
import { at, decision, entry, snapshotOf } from "./builders.ts";

function given(snapshot: Snapshot, added: Record): Feedback[] {
  return feedback([added], snapshot, derive(snapshot), lengthGuidance());
}
function agentEditSheReplaces(): Record[] {
  return [
    entry({ id: "s-aaaaaa" }),
    decision({
      id: "d-aaaaaa",
      decidedBy: "author",
      date: at(0),
      changes: [{ entry: "s-aaaaaa", action: Action.CREATE }],
    }),
    decision({
      id: "d-bbbbbb",
      date: at(1),
      changes: [{ entry: "s-aaaaaa", action: Action.EDIT }],
    }),
  ];
}
test("author_replacing_an_agent_edit_is_asked_whether_it_edits_back", () => {
  const added = decision({
    id: "d-cccccc",
    decidedBy: "author",
    date: at(2),
    replaces: ["d-bbbbbb"],
  });
  const s = snapshotOf([...agentEditSheReplaces(), added]);
  expect(given(s, added)).toEqual([
    {
      recordId: "d-cccccc",
      message:
        "it replaces d-bbbbbb, whose edit of s-aaaaaa is still the latest edit of that entry; does d-cccccc edit s-aaaaaa back? If so, add an edit draft of s-aaaaaa and list it in changes with action edit",
    },
  ]);
});
test("no_edit_back_question_when_the_decision_edits_the_entry", () => {
  const edit = [{ entry: "s-aaaaaa", action: Action.EDIT }];
  const added = decision({
    id: "d-cccccc",
    decidedBy: "author",
    date: at(2),
    replaces: ["d-bbbbbb"],
    changes: edit,
  });
  expect(given(snapshotOf([...agentEditSheReplaces(), added]), added)).toEqual([]);
});
test("no_edit_back_question_when_a_later_change_stands", () => {
  const later = decision({
    id: "d-dddddd",
    date: at(3),
    changes: [{ entry: "s-aaaaaa", action: Action.EDIT }],
  });
  const added = decision({
    id: "d-cccccc",
    decidedBy: "author",
    date: at(2),
    replaces: ["d-bbbbbb"],
  });
  const s = snapshotOf([...agentEditSheReplaces(), added, later]);
  expect(given(s, added)).toEqual([]);
});
test("replacing_her_retirement_says_which_entry_comes_back", () => {
  const items = agentEditSheReplaces().slice(0, 2);
  const retire = decision({
    id: "d-bbbbbb",
    decidedBy: "author",
    date: at(1),
    changes: [{ entry: "s-aaaaaa", action: Action.RETIRE }],
  });
  const added = decision({
    id: "d-cccccc",
    decidedBy: "author",
    date: at(2),
    replaces: ["d-bbbbbb"],
  });
  expect(given(snapshotOf([...items, retire, added]), added)).toEqual([
    {
      recordId: "d-cccccc",
      message:
        "it replaces d-bbbbbb, the last standing retirement of s-aaaaaa, so s-aaaaaa becomes current again; to keep it retired, list it in changes with action retire",
    },
  ]);
});
