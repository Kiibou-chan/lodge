import { expect, test } from "bun:test";
import {
  AddOutcome,
  actorText,
  added,
  agent,
  CommitOutcome,
  committed,
  gate,
  listed,
  person,
  read,
  written,
} from "#app";
import { checkResult, tree } from "#core";

test("actor_text_names_the_person_or_the_role", () => {
  expect(actorText(person("ada"))).toBe("ada");
  expect(actorText(agent())).toBe("agent");
  expect(actorText(agent("builder"))).toBe("agent builder");
});
test("default_filling_functions_fill_python_defaults", () => {
  const current = tree({ rev: null, files: new Map() });
  const reading = read({ freshness: null, unrecorded: [] });
  const check = checkResult([], []);
  expect(committed({ outcome: CommitOutcome.COMMITTED }).detail).toBe("");
  expect(gate({ published: current, checked: [["", current]] }).notes).toEqual([]);
  expect(reading.statuses).toEqual(new Map());
  expect(listed({ items: [], read: reading }).more).toBe(0);
  expect(added({ ids: [], feedback: [], check, outcome: AddOutcome.PUBLISHED })).toEqual({
    ids: [],
    feedback: [],
    check,
    outcome: AddOutcome.PUBLISHED,
    freshness: null,
    minted: [],
    paths: [],
    awaits: null,
    held: null,
  });
  expect(written({ ids: [], outcome: AddOutcome.PUBLISHED, check })).toEqual({
    ids: [],
    outcome: AddOutcome.PUBLISHED,
    check,
    committed: null,
    about: null,
    awaits: null,
    held: null,
  });
});

test("explicit_defaulted_fields_survive", () => {
  const current = tree({ rev: null, files: new Map() });
  const statuses = new Map([["s-aaaaaa", "current"]]);
  const reading = read({ freshness: null, unrecorded: [], statuses });
  const check = checkResult([], []);
  const commit = committed({ outcome: CommitOutcome.COMMITTED, detail: "x" });
  expect(commit.detail).toBe("x");
  expect(gate({ published: current, checked: [], notes: ["x"] }).notes).toEqual(["x"]);
  expect(reading.statuses).toBe(statuses);
  expect(listed({ items: [], read: reading, more: 2 }).more).toBe(2);
  expect(
    added({
      ids: [],
      feedback: [],
      check,
      outcome: AddOutcome.PUBLISHED,
      freshness: "x",
      minted: ["d-aaaaaa"],
      paths: ["x"],
    }),
  ).toMatchObject({ freshness: "x", minted: ["d-aaaaaa"], paths: ["x"] });
  expect(
    written({
      ids: [],
      outcome: AddOutcome.PUBLISHED,
      check,
      committed: commit,
      about: "s-aaaaaa",
    }),
  ).toMatchObject({ committed: commit, about: "s-aaaaaa" });
});
