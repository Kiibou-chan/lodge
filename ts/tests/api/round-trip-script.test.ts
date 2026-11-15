import { expect, test } from "bun:test";
import { symlinkSync } from "node:fs";
import { resolve } from "node:path";
import { compareStores, comparisonExitCode } from "../../scripts/round-trip.ts";
import { isolateGit } from "../git/isolated.ts";
import { commit, repository, temporaryFolder } from "../git/repos.ts";
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
    [{ path: decision, detail: "source: Keep logs.\nexport: Keep transcripts." }],
  ],
  [
    "body_author_is_not_metadata",
    decision,
    `${original}decided_by: author\n`,
    `${original.replace("author", "ana")}decided_by: ana\n`,
    0,
    0,
    [{ path: decision, detail: "source: decided_by: author\nexport: decided_by: ana" }],
  ],
  [
    "attachment_is_not_metadata",
    "lodge/attachments/d-40q44p/raw.bin",
    "by: author\n",
    "by: ana\n",
    0,
    0,
    [{ path: "lodge/attachments/d-40q44p/raw.bin", detail: "source: by: author\nexport: by: ana" }],
  ],
  [
    "shorter_export",
    thread,
    "same\nremoved",
    "same",
    0,
    0,
    [{ path: thread, detail: "source: removed\nexport: (end of file)" }],
  ],
  [
    "longer_export",
    thread,
    "same",
    "same\nadded",
    0,
    0,
    [{ path: thread, detail: "source: (end of file)\nexport: added" }],
  ],
  ["binary_bytes", "lodge/attachments/d-40q44p/raw.bin", "\uDCFF\uDCFE", "\uDCFF\uDCFE", 1, 0, []],
] as const)("comparison %s", (_name, path, before, after, equal, mapped, differences) => {
  const counts = compareStores(new Map([[path, before]]), new Map([[path, after]]), "ana");
  expect(comparisonExitCode(counts)).toBe(differences.length ? 1 : 0);
  expect(counts).toEqual({
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
      { path: "lodge/extra", detail: "extra in the export" },
      { path: "lodge/missing", detail: "missing from the export" },
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

function script(...args: string[]) {
  return Bun.spawnSync(
    [process.execPath, resolve(import.meta.dir, "../../scripts/round-trip.ts"), ...args],
    { env: { ...process.env }, stdout: "pipe", stderr: "pipe" },
  );
}

test.each([[], ["repo"], ["repo", "HEAD", "HEAD", "extra"]])(
  "script_rejects_wrong_argument_count %j",
  (...args) => {
    const result = script(...args);
    expect(result.exitCode).toBe(2);
    expect(new TextDecoder().decode(result.stderr)).toBe(
      "Usage: round-trip.ts REPOSITORY REV [SETTINGS_REV]\n",
    );
    expect(new TextDecoder().decode(result.stdout)).toBe("");
  },
);

test("script_exits_one_when_import_is_refused", async () => {
  const source = await zeroTwoRepository(
    "checkout",
    new Map([["lodge/decisions/broken.md", "invalid record\n"]]),
  );
  const result = script(source.repository, source.rev);
  expect(result.exitCode).toBe(1);
  expect(JSON.parse(new TextDecoder().decode(result.stderr))).toMatchObject({
    kind: "check-failed",
    stage: "lodge 0.2",
  });
  expect(new TextDecoder().decode(result.stdout)).toBe("");
});

test("script_exits_one_without_a_lodge_folder", () => {
  const repo = repository();
  commit(repo, "README.md", "A made-up project\n", "Start");
  const result = script(repo, "HEAD");
  expect(result.exitCode).toBe(1);
  expect(new TextDecoder().decode(result.stderr)).toContain("lodge/");
  expect(new TextDecoder().decode(result.stdout)).toBe("");
});

test("shell_reports_missing_bun_before_cloning", () => {
  const folder = temporaryFolder();
  symlinkSync("/usr/bin/dirname", resolve(folder, "dirname"));
  const result = Bun.spawnSync(
    ["/bin/sh", resolve(import.meta.dir, "../../../scripts/round-trip.sh")],
    { env: { ...process.env, PATH: folder }, stdout: "pipe", stderr: "pipe" },
  );
  expect(result.exitCode).toBe(2);
  expect(new TextDecoder().decode(result.stderr)).toBe("bun is not installed\n");
});
