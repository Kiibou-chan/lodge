import { expect, test } from "bun:test";
import { AddOutcome, LodgeError } from "#app";
import { load, tree } from "#core";
import { areaText, decisionText, specText } from "../core/applying.ts";
import { MemoryStore } from "./fakes.ts";
import { AREA, raises, wired } from "./support.ts";

const LOG = ["run.log", "line one\nline two\n"] as const;
const PATH = "lodge/attachments/d-111111/run.log";
const ENTRY = specText("id: s-bbbbbb", "area: storage", { body: "Everything is kept." });
function newDecision(...extra: string[]): readonly [string, string] {
  return ["d.md", decisionText("changes:", "  - {entry: s-bbbbbb, action: create}", ...extra)];
}
test("attachment_is_written_beside_the_new_decision", async () => {
  const store = new MemoryStore([AREA]);
  const added = await wired(store).add([newDecision("attachments: [run.log]"), ["s.md", ENTRY]], {
    attachments: [LOG],
  });
  expect(added.outcome).toBe(AddOutcome.PUBLISHED);
  expect(store.files.get(PATH)).toBe(LOG[1]);
  expect(store.publishes[0]?.[0].has(PATH)).toBe(true);
  const s = load(tree({ rev: null, files: store.files }));
  expect(s.decisions.get("d-111111")?.attachments).toEqual(["run.log"]);
  expect(s.attachments.has(PATH)).toBe(true);
});
test("dry_run_writes_no_attachment", async () => {
  const store = new MemoryStore([AREA]);
  expect(
    (
      await wired(store).add([newDecision("attachments: [run.log]"), ["s.md", ENTRY]], {
        dryRun: true,
        attachments: [LOG],
      })
    ).outcome,
  ).toBe(AddOutcome.DRY_RUN);
  expect(store.publishes).toEqual([]);
  expect(store.files.has(PATH)).toBe(false);
});
test("attachment_needs_exactly_one_new_decision", async () => {
  const store = new MemoryStore([AREA]);
  await raises(
    wired(store).add([["a.md", areaText("name: storage")]], { attachments: [LOG] }),
    LodgeError,
    "--attach needs the add to create one decision, not 0",
  );
  await raises(
    wired(store).add([newDecision("attachments: [run.log]"), newDecision(), ["s.md", ENTRY]], {
      attachments: [LOG],
    }),
    LodgeError,
    "--attach needs the add to create one decision, not 2",
  );
  expect(store.attempts).toBe(0);
});
test("decision_must_list_exactly_the_attached_names", async () => {
  const store = new MemoryStore([AREA]);
  await raises(
    wired(store).add([newDecision(), ["s.md", ENTRY]], { attachments: [LOG] }),
    LodgeError,
    "lists [] in attachments, but the attached files are [run.log]",
  );
  await raises(
    wired(store).add([newDecision("attachments: [run.log, more.log]"), ["s.md", ENTRY]], {
      attachments: [LOG],
    }),
    LodgeError,
    "lists [more.log, run.log] in attachments",
  );
  expect(store.attempts).toBe(0);
});
test.each(["", ".", "..", "a/b", "a\\b", ".git"].map((c) => [c]))(
  "attachment_names_are_plain_file_names",
  async (name) => {
    await raises(
      wired(new MemoryStore([AREA])).add([newDecision("attachments: [x]"), ["s.md", ENTRY]], {
        attachments: [[name, "x"]],
      }),
      LodgeError,
      "not a plain file name",
    );
  },
);
test("two_attachments_with_one_name_are_refused", async () => {
  await raises(
    wired(new MemoryStore([AREA])).add([newDecision("attachments: [run.log]"), ["s.md", ENTRY]], {
      attachments: [LOG, LOG],
    }),
    LodgeError,
    /run\.log is attached twice/u,
  );
});
