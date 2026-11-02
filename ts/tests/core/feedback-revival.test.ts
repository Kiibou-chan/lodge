import { expect, test } from "bun:test";
import {
  Action,
  derive,
  type Feedback,
  feedback,
  lengthGuidance,
  load,
  newRecordPath,
  type Record,
  type Snapshot,
  tree,
} from "#core";
import { at, decision, entry, filesOf, snapshotOf } from "./builders.ts";

const CREATE = [{ entry: "s-aaaaaa", action: Action.CREATE }];
const EDIT = [{ entry: "s-aaaaaa", action: Action.EDIT }];
const RETIRE = [{ entry: "s-aaaaaa", action: Action.RETIRE }];
function given(snapshot: Snapshot, added: Record): Feedback[] {
  return feedback([added], snapshot, derive(snapshot), lengthGuidance());
}
function herCreation(): Record[] {
  return [
    entry({ id: "s-aaaaaa" }),
    decision({ id: "d-aaaaaa", decidedBy: "author", date: at(0), changes: CREATE }),
  ];
}
test("dangling_replaces_leaves_the_revival_line_and_does_not_raise", () => {
  const retire = decision({ id: "d-bbbbbb", decidedBy: "author", date: at(1), changes: RETIRE });
  const added = decision({
    id: "d-cccccc",
    decidedBy: "author",
    date: at(2),
    replaces: ["d-zzzzzz", "d-bbbbbb"],
  });
  const found = given(snapshotOf([...herCreation(), retire, added]), added);
  expect(found.map((f) => f.message.slice(0, 30))).toEqual(["it replaces d-bbbbbb, the last"]);
});
test("rejecting_an_agent_edit_and_a_later_agent_retirement_asks_to_edit_back", () => {
  const edit = decision({ id: "d-bbbbbb", date: at(1), changes: EDIT });
  const retire = decision({ id: "d-cccccc", date: at(2), changes: RETIRE });
  const added = decision({
    id: "d-dddddd",
    decidedBy: "author",
    date: at(3),
    replaces: ["d-bbbbbb", "d-cccccc"],
  });
  const found = given(snapshotOf([...herCreation(), edit, retire, added]), added);
  expect(found).toEqual([
    {
      recordId: "d-dddddd",
      message:
        "it replaces d-bbbbbb, whose edit of s-aaaaaa is still the latest edit of that entry; does d-dddddd edit s-aaaaaa back? If so, add an edit draft of s-aaaaaa and list it in changes with action edit",
    },
    {
      recordId: "d-dddddd",
      message:
        "it replaces d-cccccc, the last standing retirement of s-aaaaaa, so s-aaaaaa becomes current again; to keep it retired, list it in changes with action retire",
    },
  ]);
});
test("one_revival_line_names_every_replaced_retirement", () => {
  const first = decision({ id: "d-bbbbbb", decidedBy: "author", date: at(1), changes: RETIRE });
  const second = decision({ id: "d-cccccc", decidedBy: "author", date: at(2), changes: RETIRE });
  const added = decision({
    id: "d-dddddd",
    decidedBy: "author",
    date: at(3),
    replaces: ["d-bbbbbb", "d-cccccc"],
  });
  const found = given(snapshotOf([...herCreation(), first, second, added]), added);
  expect(found).toEqual([
    {
      recordId: "d-dddddd",
      message:
        "it replaces d-bbbbbb and d-cccccc, the last standing retirements of s-aaaaaa, so s-aaaaaa becomes current again; to keep it retired, list it in changes with action retire",
    },
  ]);
});
test("no_revival_line_when_the_entry_stays_retired", () => {
  const first = decision({ id: "d-bbbbbb", decidedBy: "author", date: at(1), changes: RETIRE });
  const added = decision({
    id: "d-cccccc",
    decidedBy: "author",
    date: at(2),
    replaces: ["d-bbbbbb"],
  });
  const again = decision({ id: "d-dddddd", decidedBy: "author", date: at(3), changes: RETIRE });
  expect(given(snapshotOf([...herCreation(), first, added, again]), added)).toEqual([]);
});
function givenFiles(files: Map<string, string>, added: Record): Feedback[] {
  return given(load(tree({ rev: null, files: files })), added);
}
function unparsable(files: Map<string, string>, record: Record): void {
  const path = newRecordPath(record);
  const text = files.get(path);
  if (text === undefined) throw new Error("missing fixture record");
  files.set(path, text.replace("title:", "titel:"));
}
test("unparsable_decision_in_replaces_does_not_crash", () => {
  const retire = decision({ id: "d-bbbbbb", decidedBy: "author", date: at(1), changes: RETIRE });
  const bad = decision({ id: "d-zzzzzz", date: at(1), changes: RETIRE });
  const added = decision({ id: "d-cccccc", date: at(2), replaces: ["d-zzzzzz", "d-bbbbbb"] });
  const files = filesOf(...herCreation(), retire, bad, added);
  unparsable(files, bad);
  const found = givenFiles(files, added);
  expect(
    found.filter((f) => f.message.startsWith("it replaces")).map((f) => f.message.slice(0, 30)),
  ).toEqual(["it replaces d-bbbbbb, the last"]);
});
test("revival_of_an_unparsable_entry_does_not_crash", () => {
  const retire = decision({ id: "d-bbbbbb", decidedBy: "author", date: at(1), changes: RETIRE });
  const added = decision({ id: "d-cccccc", date: at(2), replaces: ["d-bbbbbb"] });
  const files = filesOf(...herCreation(), retire, added);
  unparsable(files, entry({ id: "s-aaaaaa" }));
  expect(givenFiles(files, added).some((f) => f.message.startsWith("it replaces"))).toBe(false);
});
test("revival_of_a_dangling_entry_does_not_crash", () => {
  const ghost = decision({
    id: "d-bbbbbb",
    decidedBy: "author",
    date: at(1),
    changes: [{ entry: "s-zzzzzz", action: Action.RETIRE }],
  });
  const added = decision({ id: "d-cccccc", date: at(2), replaces: ["d-bbbbbb"] });
  const found = given(snapshotOf([...herCreation(), ghost, added]), added);
  expect(found.some((f) => f.message.startsWith("it replaces"))).toBe(false);
});
test("revival_line_names_only_retirements_that_were_standing", () => {
  const first = decision({ id: "d-bbbbbb", decidedBy: "author", date: at(1), changes: RETIRE });
  const second = decision({ id: "d-cccccc", decidedBy: "author", date: at(2), changes: RETIRE });
  const earlier = decision({
    id: "d-dddddd",
    decidedBy: "author",
    date: at(3),
    replaces: ["d-bbbbbb"],
  });
  const added = decision({
    id: "d-eeeeee",
    decidedBy: "author",
    date: at(4),
    replaces: ["d-bbbbbb", "d-cccccc"],
  });
  const found = given(snapshotOf([...herCreation(), first, second, earlier, added]), added);
  expect(found.map((f) => f.message.slice(0, 50))).toEqual([
    "d-bbbbbb is already replaced by d-dddddd",
    "it replaces d-cccccc, the last standing retirement",
  ]);
});
test("replacing_a_decision_another_decision_already_replaced_says_so", () => {
  const old = decision({ id: "d-aaaaaa", date: at(0) });
  const first = decision({ id: "d-bbbbbb", date: at(1), replaces: ["d-aaaaaa"] });
  const added = decision({ id: "d-cccccc", date: at(2), replaces: ["d-aaaaaa"] });
  const found = given(snapshotOf([old, first, added]), added);
  expect(found).toEqual([
    { recordId: "d-cccccc", message: "d-aaaaaa is already replaced by d-bbbbbb" },
  ]);
});
test("replacing_a_decision_only_this_decision_replaces_is_silent", () => {
  const old = decision({ id: "d-aaaaaa", date: at(0) });
  const added = decision({ id: "d-cccccc", date: at(2), replaces: ["d-aaaaaa"] });
  expect(given(snapshotOf([old, added]), added)).toEqual([]);
});
