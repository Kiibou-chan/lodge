import { expect, test } from "bun:test";
import { resolve } from "node:path";
import { compareStores } from "../../scripts/round-trip.ts";
import { isolateGit } from "../git/isolated.ts";
import { zeroTwoRepository } from "../git/zero-two.ts";

isolateGit();
const decision = "lodge/decisions/d-40q44p-choice.md";
const thread = "lodge/threads/q-j2dsgk.md";
const original = "---\nkind: decision\ndecided_by: author\n---\n\nKeep logs.\n";

test.each([
  ["equal_bytes", decision, original, original, 1, 0, []],
  ["mapped_decision", decision, original, original.replace("author", "ana"), 0, 1, []],
  ["mapped_reply", thread, "## Message 2\n\nby: author\n", "## Message 2\n\nby: ana\n", 0, 1, []],
  [
    "body_change",
    decision,
    original,
    original.replace("author", "ana").replace("logs", "transcripts"),
    0,
    0,
    [{ path: decision, line: 6 }],
  ],
  [
    "body_author_is_not_metadata",
    decision,
    `${original}decided_by: author\n`,
    `${original.replace("author", "ana")}decided_by: ana\n`,
    0,
    0,
    [{ path: decision, line: 7 }],
  ],
  [
    "attachment_is_not_metadata",
    "lodge/attachments/d-40q44p/raw.bin",
    "by: author\n",
    "by: ana\n",
    0,
    0,
    [{ path: "lodge/attachments/d-40q44p/raw.bin", line: 1 }],
  ],
  ["binary_bytes", "lodge/attachments/d-40q44p/raw.bin", "\uDCFF\uDCFE", "\uDCFF\uDCFE", 1, 0, []],
] as const)("comparison %s", (_name, path, before, after, equal, mapped, differences) => {
  expect(compareStores(new Map([[path, before]]), new Map([[path, after]]), "ana")).toEqual({
    compared: 1,
    equal,
    mapped,
    differences: [...differences],
  });
});

test("comparison_reports_missing_and_extra_paths", () => {
  expect(
    compareStores(new Map([["lodge/missing", ""]]), new Map([["lodge/extra", ""]]), "ana"),
  ).toEqual({
    compared: 2,
    equal: 0,
    mapped: 0,
    differences: [
      { path: "lodge/extra", line: 1 },
      { path: "lodge/missing", line: 1 },
    ],
  });
});

test.each(["checkout", "branch"] as const)("script_round_trip %s", async (layout) => {
  const source = await zeroTwoRepository(
    layout,
    new Map([["lodge/attachments/d-q59cdf/raw.bin", "\uDCFF\uDCFE"]]),
  );
  const result = Bun.spawnSync(
    [
      process.execPath,
      resolve(import.meta.dir, "../../scripts/round-trip.ts"),
      source.repository,
      source.rev,
      ...(layout === "branch" ? [source.settingsRev] : []),
    ],
    { env: { ...process.env }, stdout: "pipe", stderr: "pipe" },
  );
  expect(new TextDecoder().decode(result.stderr)).toBe("");
  expect(result.exitCode).toBe(0);
  expect(new TextDecoder().decode(result.stdout)).toBe(
    "Files compared: 11\nFiles equal: 7\nFiles differing only in decided_by or a message's by: 4\nOther differences: 0\n",
  );
});
