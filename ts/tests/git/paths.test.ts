import { expect, test } from "bun:test";
import { mkdirSync, symlinkSync } from "node:fs";
import { join } from "node:path";
import { LodgeError } from "#app";
import { isFolder, repoRootOf, resolvePath } from "#git";
import { isolateGit } from "./isolated.ts";
import { repository, temporaryFolder } from "./repos.ts";

isolateGit();
test("resolve_follows_links", () => {
  const root = temporaryFolder();
  mkdirSync(join(root, "real", "child"), { recursive: true });
  symlinkSync(join(root, "real", "child"), join(root, "linked"));
  expect(resolvePath(join(root, "linked", "file.md"))).toBe(join(root, "real", "child", "file.md"));
  expect(resolvePath(`${root}/linked/../file.md`)).toBe(join(root, "real", "file.md"));
});
test("resolve_takes_dot_dot_through_missing_folders", () => {
  const root = temporaryFolder();
  expect(resolvePath(`${root}/docs/../lodge/decisions/d.md`)).toBe(
    join(root, "lodge/decisions/d.md"),
  );
});
test("repo_root_of_a_file_that_does_not_exist_yet", async () => {
  const repo = repository();
  expect(await repoRootOf(join(repo, "lodge/decisions/d.md"))).toBe(repo);
});
test("repo_root_outside_a_repository_is_one_sentence", async () => {
  const root = temporaryFolder();
  const result = repoRootOf(join(root, "missing/d.md"));
  await expect(result).rejects.toBeInstanceOf(LodgeError);
  await expect(result).rejects.toThrow(`${root} is not inside a git repository`);
});
test("is_folder_says_whether_a_folder_exists", () => {
  const root = temporaryFolder();
  expect(isFolder(root)).toBe(true);
  expect(isFolder(join(root, "absent"))).toBe(false);
  symlinkSync(root, join(root, "link"));
  expect(isFolder(join(root, "link"))).toBe(true);
});
