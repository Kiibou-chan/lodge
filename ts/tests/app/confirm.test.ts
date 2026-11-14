import { expect, test } from "bun:test";
import { AddOutcome, LodgeError, NotFound, StaleList } from "#app";
import { Action, type Decision, load, Scope, tree } from "#core";
import { area, at, decision, entry } from "../core/builders.ts";
import { MemoryStore } from "./fakes.ts";
import { raises, wired } from "./support.ts";

const AGENT = decision({ id: "d-aaaaaa", changes: [{ entry: "s-aaaaaa", action: Action.CREATE }] });
const OTHER = decision({
  id: "d-bbbbbb",
  date: at(1),
  changes: [{ entry: "s-bbbbbb", action: Action.CREATE }],
});
function storeFor(staged = false) {
  return new MemoryStore([area(), entry({ id: "s-aaaaaa" }), AGENT], { staged });
}
function made(store: MemoryStore): Decision {
  return load(tree({ rev: null, files: store.files })).decisions.get("d-111111") as Decision;
}
function both() {
  return new MemoryStore([
    area(),
    entry({ id: "s-aaaaaa" }),
    entry({ id: "s-bbbbbb" }),
    AGENT,
    OTHER,
  ]);
}

test("confirm_one_decision", async () => {
  const store = storeFor();
  const result = await wired(store).confirm([AGENT.id], "Read.");
  expect(result.outcome).toBe(AddOutcome.PUBLISHED);
  expect(made(store).decidedBy).toBe("author");
  expect(made(store).confirms).toEqual([AGENT.id]);
  expect(made(store).quote?.when).toBe("2026-10-29 09:30");
  expect(store.commits).toEqual([]);
});
test("confirm_writes_only_a_new_decision_file", async () => {
  const store = storeFor();
  const before = new Set(store.files.keys());
  await wired(store).confirm([AGENT.id], "Read.");
  const paths = [...(store.publishes[0]?.[0].keys() ?? [])];
  expect(paths).toHaveLength(1);
  expect(paths.every((p) => p.startsWith("lodge/decisions/") && !before.has(p))).toBe(true);
});
test("confirmed_decision_keeps_decided_by_and_clears_its_flag", async () => {
  const author = decision({ id: "d-cccccc", decidedBy: "author", date: at(0) });
  const agent = { ...AGENT, date: at(1), narrows: [author.id] };
  const store = new MemoryStore([area(), entry({ id: "s-aaaaaa" }), author, agent]);
  const lodge = wired(store);
  expect((await lodge.waitingAll())[0].items.length).toBeGreaterThan(0);
  await lodge.confirm([agent.id], "Read.");
  expect(load(tree({ rev: null, files: store.files })).decisions.get(agent.id)?.decidedBy).toBe(
    agent.decidedBy,
  );
  expect((await lodge.waitingAll())[0].items).toEqual([]);
});
test("scope_product_when_any_listed_is_product", async () => {
  const store = new MemoryStore([
    area(),
    entry({ id: "s-aaaaaa" }),
    entry({ id: "s-bbbbbb" }),
    AGENT,
    { ...OTHER, scope: Scope.PROCESS },
  ]);
  await wired(store).confirm([AGENT.id, OTHER.id], "Read.", { area: "storage" });
  expect(made(store).scope).toBe(Scope.PRODUCT);
});
test("scope_process_when_all_are_process", async () => {
  const store = new MemoryStore([{ ...AGENT, scope: Scope.PROCESS, changes: [] }]);
  await wired(store).confirm([AGENT.id], "Read.");
  expect(made(store).scope).toBe(Scope.PROCESS);
});
test("area_confirms_exactly_the_listed", async () => {
  const store = both();
  await wired(store).confirm([OTHER.id, AGENT.id], "Read.", { area: "storage" });
  expect(made(store).confirms).toEqual([AGENT.id, OTHER.id]);
});
test("stale_area_list_writes_nothing", async () => {
  const store = both();
  await wired(store).confirm([OTHER.id], "Read.");
  store.publishes.length = 0;
  await raises(
    wired(store).confirm([AGENT.id, OTHER.id], "Read.", { area: "storage" }),
    StaleList,
    "the list changed since the page was loaded; nothing was written",
  );
  expect(store.publishes).toEqual([]);
});
test("second_identical_confirmation_is_stale", async () => {
  const store = storeFor(true);
  const lodge = wired(store);
  await lodge.confirm([AGENT.id], "Read.");
  await expect(lodge.confirm([AGENT.id], "Read.")).rejects.toThrow(StaleList);
  expect(store.publishes).toHaveLength(1);
});
test.each([[""], [" \r\n\t"]])("words_required %j", async (words) => {
  const store = storeFor();
  await raises(
    wired(store).confirm([AGENT.id], words),
    LodgeError,
    "your words are required; nothing was written",
  );
  expect(store.publishes).toEqual([]);
});
test("words_with_specials_kept_verbatim", async () => {
  const store = storeFor();
  const words =
    'Read: "yes" \\ # [x]\r\n\tCaveat: café.\rInside.\n## Reasoning\nMore.\n---\nStill here.';
  await wired(store).confirm([AGENT.id], ` \n${words} \n`);
  const expected = words.replaceAll("\r\n", "\n");
  expect(made(store).reasoning).toBe(expected);
  expect(made(store).quote?.text).toBe(expected);
});
test("words_with_unstorable_character_refused", async () => {
  const store = storeFor();
  await raises(
    wired(store).confirm([AGENT.id], "\x00"),
    LodgeError,
    "your words hold a character lodge cannot store",
  );
  expect(store.publishes).toEqual([]);
});
test("commit_after_staged", async () => {
  const store = storeFor(true);
  const result = await wired(store).confirm([AGENT.id], "Read.", { commit: true });
  const path = [...(store.publishes[0]?.[0].keys() ?? [])][0] as string;
  expect(store.commits).toEqual([[[path], "Author confirmation from the viewer: d-111111"]]);
  expect(result.committed).toEqual(store.commitResult);
});
test("behind_area_lists_entries_in_other_areas", async () => {
  const agent = {
    ...AGENT,
    changes: [
      ...AGENT.changes,
      { entry: "s-bbbbbb", action: Action.EDIT },
      { entry: "s-bbbbbb", action: Action.LINK },
      { entry: "s-cccccc", action: Action.EDIT },
    ],
  };
  const lodge = wired(
    new MemoryStore([
      area(),
      entry({ id: "s-aaaaaa" }),
      entry({ id: "s-bbbbbb", area: "other" }),
      agent,
    ]),
  );
  const rows = await lodge.behindArea("storage");
  expect(rows[0]?.decision.id).toBe(AGENT.id);
  expect(rows[0]?.entries).toEqual([
    ["s-aaaaaa", "storage"],
    ["s-bbbbbb", "other"],
  ]);
  await expect(lodge.behindArea("unknown")).rejects.toThrow(NotFound);
});
test("show_marks_confirmable", async () => {
  const store = storeFor();
  const lodge = wired(store);
  expect((await lodge.show(AGENT.id)).confirmable).toBe(true);
  expect((await lodge.show("s-aaaaaa")).confirmable).toBe(false);
  await lodge.confirm([AGENT.id], "Read.");
  expect((await lodge.show(AGENT.id)).confirmable).toBe(false);
  expect((await lodge.show("d-111111")).confirmable).toBe(false);
});
test.each([
  [false, true],
  [true, false],
])("confirmation_does_not_commit_unless_staged_and_requested %j %j", async (staged, commit) => {
  const store = storeFor(staged);
  const result = await wired(store).confirm([AGENT.id], "Read.", { commit });
  expect(result.outcome).toBe(staged ? AddOutcome.STAGED : AddOutcome.PUBLISHED);
  expect(result.committed).toBeNull();
  expect(store.commits).toEqual([]);
});
test("confirmation_failed_check_writes_and_commits_nothing", async () => {
  const store = new MemoryStore([{ ...AGENT, date: "2026-10-29T09:31:00+01:00" }], {
    staged: true,
  });
  const result = await wired(store).confirm([AGENT.id], "Read.", { commit: true });
  expect(result.outcome).toBe(AddOutcome.CHECK_FAILED);
  expect(result.check.ok).toBe(false);
  expect(store.publishes).toEqual([]);
  expect(store.commits).toEqual([]);
});
test("repeated_cr_before_lf_is_refused", async () => {
  const store = storeFor();
  await raises(
    wired(store).confirm([AGENT.id], "a\r\r\nb"),
    LodgeError,
    "your words hold a character lodge cannot store",
  );
  expect(store.publishes).toEqual([]);
});
test("second_area_confirmation_is_stale", async () => {
  const store = storeFor(true);
  const lodge = wired(store);
  await lodge.confirm([AGENT.id], "Read.", { area: "storage" });
  await expect(lodge.confirm([AGENT.id], "Read.", { area: "storage" })).rejects.toThrow(StaleList);
  expect(store.publishes).toHaveLength(1);
});
test("duplicate_confirmation_ids_are_stale", async () => {
  const store = storeFor();
  await expect(
    wired(store).confirm([AGENT.id, AGENT.id], "Read.", { area: "storage" }),
  ).rejects.toThrow(StaleList);
  expect(store.publishes).toEqual([]);
});
test("empty_confirmation_ids_are_stale", async () => {
  const store = storeFor();
  await expect(wired(store).confirm([], "Read.")).rejects.toThrow(StaleList);
  expect(store.publishes).toEqual([]);
});
test("same_length_wrong_area_subset_is_stale", async () => {
  const store = both();
  await expect(
    wired(store).confirm([AGENT.id, "d-cccccc"], "Read.", { area: "storage" }),
  ).rejects.toThrow(StaleList);
  expect(store.publishes).toEqual([]);
});
test("confirmation_defaults_to_no_commit", async () => {
  const store = storeFor(true);
  const result = await wired(store).confirm([AGENT.id], "Read.");
  expect(result.outcome).toBe(AddOutcome.STAGED);
  expect(result.committed).toBeNull();
  expect(store.commits).toEqual([]);
});
