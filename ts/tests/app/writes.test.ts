import { expect, test } from "bun:test";
import { AddOutcome, LodgeError } from "#app";
import { checkState, load, parseRecord, tree } from "#core";
import { areaText, decisionText, specText } from "../core/applying.ts";
import { at, decision, entry } from "../core/builders.ts";
import { CountingIds, FixedClock, MemoryStore, START } from "./fakes.ts";
import { AREA, FIRST, project, raises, wired } from "./support.ts";

const NEW_DECISION = decisionText("changes:", "  - {entry: s-bbbbbb, action: create}");
const NEW_ENTRY = specText("id: s-bbbbbb", "area: storage", { body: "Everything is kept." });
const PAIR = [
  ["decision.md", NEW_DECISION],
  ["entry.md", NEW_ENTRY],
] as const;
test("add_new_decision_entry_area", async () => {
  const store = new MemoryStore();
  const added = await wired(store).add([...PAIR, ["area.md", areaText("name: storage")]]);
  expect(added.outcome).toBe(AddOutcome.PUBLISHED);
  expect(added.ids).toEqual(["d-111111", "s-bbbbbb"]);
  expect([...store.files.keys()].sort()).toEqual([
    "lodge/decisions/d-111111-keep-transcripts.md",
    "lodge/spec/storage/_area.md",
    "lodge/spec/storage/s-bbbbbb-transcripts.md",
  ]);
  expect(store.publishes[0]?.[1]).toBe("lodge: add d-111111, s-bbbbbb Keep transcripts");
  expect(checkState(load(tree({ rev: null, files: store.files }))).ok).toBe(true);
});
test("add_fills_id_and_date_from_ports", async () => {
  const store = new MemoryStore([AREA]);
  await wired(
    store,
    new FixedClock({ ...START, epochMs: START.epochMs + 999 }),
    new CountingIds(7),
  ).add(PAIR);
  expect(
    parseRecord("x", store.files.get("lodge/decisions/d-777777-keep-transcripts.md") ?? ""),
  ).toMatchObject({ id: "d-777777", date: "2026-10-29T09:30:00+01:00" });
});
test("add_date_and_check_time_from_one_reading", async () => {
  const clock = new FixedClock(START, 1000);
  expect((await wired(new MemoryStore([AREA]), clock).add(PAIR)).outcome).toBe(
    AddOutcome.PUBLISHED,
  );
  expect(clock.calls).toBe(1);
});
test("add_failing_check_publishes_nothing", async () => {
  const store = project();
  const added = await wired(store).add([["entry.md", NEW_ENTRY]]);
  expect(added.outcome).toBe(AddOutcome.CHECK_FAILED);
  expect(added.check.problems.map((p) => p.check)).toEqual([4]);
  expect(store.attempts).toBe(0);
  expect(store.publishes).toEqual([]);
});
test("add_returns_feedback_and_notes", async () => {
  const added = await wired(project()).add(PAIR);
  expect(added.outcome).toBe(AddOutcome.PUBLISHED);
  expect(added.feedback.map((f) => f.recordId)).toEqual(["d-111111"]);
  expect(added.feedback[0]?.message).toContain("d-aaaaaa");
  expect(added.check.notes).toEqual(["area storage: order changed"]);
});
test("add_refuses_unreadable_or_unusable_drafts", async () => {
  const store = project();
  const lodge = wired(store);
  const broken = lodge.add([["broken.md", "---\ntitle: [unclosed\n---\n"]]);
  await raises(broken, LodgeError, /broken\.md:2/u);
  await expect(broken).rejects.toMatchObject({ exitCode: 2 });
  await raises(
    lodge.add([["entry.md", specText("id: s-bbbbbb")]]),
    LodgeError,
    /entry\.md.*needs an area/u,
  );
  await raises(lodge.add([]), LodgeError, "no drafts");
  expect(store.attempts).toBe(0);
});
test("add_imports_only_when_asked", async () => {
  const drafts = [
    ["d.md", decisionText("imported_from: {file: notes.md, heading: Storage}")],
  ] as const;
  await raises(wired(project()).add(drafts), LodgeError, "--import");
  expect((await wired(project()).add(drafts, { importing: true })).outcome).toBe(
    AddOutcome.CHECK_FAILED,
  );
});
test("dry_run_publishes_nothing", async () => {
  const store = project();
  expect((await wired(store).add(PAIR, { dryRun: true })).outcome).toBe(AddOutcome.DRY_RUN);
  expect(store.attempts).toBe(0);
  expect(store.files).toEqual(project().files);
});
test("dry_run_reports_feedback_and_check", async () => {
  const real = await wired(project()).add(PAIR),
    dry = await wired(project()).add(PAIR, { dryRun: true });
  expect([dry.ids, dry.feedback, dry.check]).toEqual([real.ids, real.feedback, real.check]);
  expect((await wired(project()).add([["entry.md", NEW_ENTRY]], { dryRun: true })).outcome).toBe(
    AddOutcome.CHECK_FAILED,
  );
});
test("mint_skips_taken", async () => {
  const ids = new CountingIds();
  expect(
    await wired(
      new MemoryStore([FIRST, decision({ id: "d-111111", date: at(5) })]),
      undefined,
      ids,
    ).mint("d"),
  ).toBe("d-222222");
  expect(ids.draws).toBe(2);
  expect(await wired(new MemoryStore([AREA, entry({ id: "s-111111" })])).mint("s")).toBe(
    "s-222222",
  );
});
test("mint_gives_up_after_ten_draws", async () => {
  const ids = new CountingIds(1, 0);
  await raises(
    wired(new MemoryStore([decision({ id: "d-111111", date: at(5) })]), undefined, ids).mint("d"),
    LodgeError,
    "ten",
  );
  expect(ids.draws).toBe(10);
});
test("add_area_sharing_a_rank_gives_feedback", async () => {
  const lodge = wired(new MemoryStore());
  await lodge.add([["a.md", areaText("name: other", "rank: 1")]]);
  const added = await lodge.add([["b.md", areaText("name: storage", "rank: 1")]]);
  expect(added.outcome).not.toBe(AddOutcome.CHECK_FAILED);
  expect(added.feedback).toContainEqual({
    recordId: "area:storage",
    message: "rank 1 is shared with area other; areas that share a rank are ordered by name",
  });
});
test("rest_on_entry_retired_in_the_same_add_is_refused", async () => {
  const store = project();
  const added = await wired(store).add([
    ["b.md", specText("id: s-bbbbbb", "area: storage", "rests_on: [s-aaaaaa]")],
    [
      "d.md",
      decisionText(
        "changes: [{entry: s-aaaaaa, action: retire}, {entry: s-bbbbbb, action: create}]",
      ),
    ],
  ]);
  expect(added.outcome).toBe(AddOutcome.CHECK_FAILED);
  expect(
    added.check.problems.some(
      (p) => p.check === 6 && p.message === "s-bbbbbb: rests on s-aaaaaa, which is retired",
    ),
  ).toBe(true);
  expect(store.publishes).toEqual([]);
});
