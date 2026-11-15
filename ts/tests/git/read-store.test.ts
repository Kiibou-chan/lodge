import { expect, test } from "bun:test";
import { readFileSync, symlinkSync } from "node:fs";
import { join } from "node:path";
import { LodgeError } from "#app";
import { encodeUtf8 } from "#core";
import { readStore, run } from "#git";
import { ZERO_TWO_STORE } from "../core/zero-two-store.ts";
import { isolateGit } from "./isolated.ts";
import { commit, git, repository } from "./repos.ts";
import { zeroTwoRepository } from "./zero-two.ts";

isolateGit();
for (const layout of ["checkout", "branch"] as const) {
  test(`reads_the_${layout}_layout`, async () => {
    const source = await zeroTwoRepository(layout);
    const result = await readStore(
      source.repository,
      source.rev,
      layout === "branch" ? source.settingsRev : undefined,
    );
    expect(result.rev).toBe(source.rev);
    expect(result.files).toEqual(
      new Map([...ZERO_TWO_STORE].filter(([p]) => p.startsWith("lodge/"))),
    );
    expect(result.files.size).toBe(10);
    expect(result.settings).toBe(ZERO_TWO_STORE.get(".lodge.toml") as string);
  });
}
test("branch_layout_without_a_settings_revision_has_no_settings", async () => {
  const source = await zeroTwoRepository("branch");
  expect((await readStore(source.repository, source.rev)).settings).toBeNull();
});
test.each(["rev", "settingsRev"])("revision_that_is_no_commit_is_refused %s", async (which) => {
  const source = await zeroTwoRepository("checkout");
  const result = readStore(source.repository, which === "rev" ? "nope" : source.rev, "nope");
  await expect(result).rejects.toBeInstanceOf(LodgeError);
  await expect(result).rejects.toThrow(`nope is not a commit in ${source.repository}`);
});
test("revision_without_lodge_is_refused", async () => {
  const source = await zeroTwoRepository("branch");
  await expect(readStore(source.repository, "main")).rejects.toThrow(
    "main holds no lodge/ folder, so it is not a lodge 0.2 store",
  );
});
test("undecodable_record_reads_as_escapes", async () => {
  const path = "lodge/decisions/d-bad.md";
  const source = await zeroTwoRepository("checkout", new Map([[path, "record\uDCFF\n"]]));
  expect((await readStore(source.repository, source.rev)).files.get(path)).toBe("record\uDCFF\n");
});
test("undecodable_attachment_keeps_its_bytes", async () => {
  const path = "lodge/attachments/d-q59cdf/raw.bin";
  const source = await zeroTwoRepository("checkout", new Map([[path, "\uDCFF\uDCFE"]]));
  expect(new Uint8Array(readFileSync(join(source.repository, path)))).toEqual(
    new Uint8Array([255, 254]),
  );
  const text = (await readStore(source.repository, source.rev)).files.get(path) as string;
  expect(text).toBe("\uDCFF\uDCFE");
  expect(encodeUtf8(text)).toEqual(new Uint8Array([255, 254]));
});
test("undecodable_name_reads_as_escapes", async () => {
  const source = await zeroTwoRepository("checkout");
  const sha = run(["hash-object", "-w", "--stdin"], source.repository, undefined, "raw\n");
  run(
    ["update-index", "-z", "--index-info"],
    source.repository,
    undefined,
    `100644 ${sha}\tlodge/spec/storage/\uDCFF.md\0`,
  );
  git(source.repository, "commit", "-m", "Raw name");
  expect(
    (await readStore(source.repository, "HEAD")).files.get("lodge/spec/storage/\uDCFF.md"),
  ).toBe("raw\n");
});
test("symbolic_link_reads_as_the_path_it_names", async () => {
  const source = await zeroTwoRepository("checkout");
  symlinkSync("../spec", join(source.repository, "lodge/link"));
  git(source.repository, "add", "--", "lodge/link");
  git(source.repository, "commit", "-m", "Link");
  expect((await readStore(source.repository, "HEAD")).files.get("lodge/link")).toBe("../spec");
});
test("settings_absent_is_null", async () => {
  const repo = repository();
  commit(repo, "lodge/decisions/.gitkeep", "", "Store without settings");
  expect((await readStore(repo, "HEAD")).settings).toBeNull();
});
