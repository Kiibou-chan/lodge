import { expect, test } from "bun:test";
import { LodgeError } from "#app";
import { encodeUtf8 } from "#core";
import { exportStore, readStore, runBytes } from "#git";
import { isolateGit } from "./isolated.ts";
import { bareRemote, clone, git, riggedRemote, seeded, worktree } from "./repos.ts";
import { zeroTwoRepository } from "./zero-two.ts";

isolateGit();
const files = new Map([
  ["lodge/decisions/.gitkeep", ""],
  ["lodge/spec/storage/record.md", "Record\n"],
]);
const target = (repository: string, remote: string | null = null, branch = "lodge") => ({
  repository,
  branch,
  remote,
});

test("first_export_makes_the_branch", async () => {
  const repo = bareRemote();
  const result = await exportStore(target(repo), files, "Export");
  expect(result).toEqual({ kind: "committed", commit: git(repo, "rev-parse", "lodge") });
  expect(git(repo, "ls-tree", "-r", "--name-only", "lodge").split("\n")).toEqual([...files.keys()]);
  for (const [path, text] of files)
    expect(runBytes(["show", `lodge:${path}`], repo)).toEqual(encodeUtf8(text));
  expect(git(repo, "show", "-s", "--format=%an <%ae>|%cn <%ce>", "lodge")).toBe(
    "lodge <lodge@export.invalid>|lodge <lodge@export.invalid>",
  );
  expect(git(repo, "show", "-s", "--format=%B", "lodge")).toBe("Export");
});
test("same_files_make_no_commit", async () => {
  const repo = bareRemote();
  await exportStore(target(repo), files, "First");
  const before = git(repo, "rev-parse", "lodge");
  expect(await exportStore(target(repo), files, "Again")).toEqual({ kind: "unchanged" });
  expect(git(repo, "rev-parse", "lodge")).toBe(before);
});
test("changed_file_makes_one_commit_on_the_last", async () => {
  const repo = bareRemote();
  await exportStore(target(repo), files, "First");
  const before = git(repo, "rev-parse", "lodge");
  await exportStore(
    target(repo),
    new Map([...files, ["lodge/spec/storage/record.md", "Changed\n"]]),
    "Changed",
  );
  expect(git(repo, "rev-parse", "lodge^")).toBe(before);
  expect(git(repo, "rev-list", "--count", `${before}..lodge`)).toBe("1");
  expect(git(repo, "show", "lodge:lodge/spec/storage/record.md")).toBe("Changed");
});
test("removed_file_leaves_the_tree", async () => {
  const repo = bareRemote();
  await exportStore(target(repo), files, "First");
  await exportStore(target(repo), new Map(), "Remove");
  expect(git(repo, "ls-tree", "-r", "lodge")).toBe("");
});
test("escaped_bytes_are_written_as_bytes", async () => {
  const repo = bareRemote();
  await exportStore(target(repo), new Map([["lodge/attachments/raw.bin", "\uDCFF"]]), "Bytes");
  expect(runBytes(["show", "lodge:lodge/attachments/raw.bin"], repo)).toEqual(
    new Uint8Array([255]),
  );
});
test.each([
  "README.md",
  "lodge/../x",
  "lodge/.git/x",
  "lodge//x",
  "lodge/./x",
  "lodge/a\\b",
  "lodge/a\0b",
  "lodge",
])("path_outside_lodge_is_refused %s", async (path) => {
  const result = exportStore(target(bareRemote()), new Map([[path, "x"]]), "Bad");
  await expect(result).rejects.toBeInstanceOf(LodgeError);
  await expect(result).rejects.toThrow(`${path} is outside lodge/, which is all the store writes`);
});
test("branch_with_other_files_is_refused", async () => {
  const repo = seeded(bareRemote());
  git(repo, "checkout", "--detach");
  await expect(exportStore(target(repo, null, "main"), files, "Bad")).rejects.toThrow(
    "main holds files outside lodge/, so it is not a branch lodge exports to; name a branch of its own",
  );
});
test("checked_out_branch_is_refused", async () => {
  const repo = seeded(bareRemote());
  const linked = worktree(repo);
  git(linked, "checkout", "-b", "lodge");
  await expect(exportStore(target(repo), files, "Bad")).rejects.toThrow(
    `lodge is checked out in a work tree of ${repo}; the export writes only a branch no work tree has checked out`,
  );
});
test("lodge_zero_two_branch_is_a_target", async () => {
  const source = await zeroTwoRepository("branch");
  const copy = await readStore(source.repository, source.rev, source.settingsRev);
  git(source.repository, "checkout", "main");
  expect(await exportStore(target(source.repository), copy.files, "Same")).toEqual({
    kind: "unchanged",
  });
});
test.each(["-x", "a..b", "a b"])("bad_branch_name_is_refused %s", async (branch) => {
  await expect(exportStore(target(bareRemote(), null, branch), files, "Bad")).rejects.toThrow(
    "export-target: branch must be a name of letters, digits, and . _ / -, not starting with a symbol",
  );
});
test("bad_remote_is_refused", async () => {
  await expect(exportStore(target(bareRemote(), "-r"), files, "Bad")).rejects.toThrow(
    "export-target: remote must not start with -",
  );
});
test("push_without_force", async () => {
  const remote = bareRemote();
  const repo = seeded(remote);
  const before = git(repo, "show-ref", "--heads");
  const result = await exportStore(target(repo, remote), files, "Export");
  expect(result).toEqual({ kind: "committed", commit: git(remote, "rev-parse", "lodge") });
  expect(git(repo, "show-ref", "--heads")).toBe(before);
  expect((await readStore(clone(remote), "origin/lodge")).files).toEqual(files);
});
test("moved_remote_branch_answers_moved", async () => {
  const { remote, mine, other } = riggedRemote("lodge");
  expect(await exportStore(target(mine, remote), files, "Race")).toEqual({ kind: "moved" });
  expect(git(remote, "rev-parse", "lodge")).toBe(other);
  expect((await exportStore(target(mine, remote), files, "Retry")).kind).toBe("committed");
  expect(git(remote, "rev-parse", "lodge^")).toBe(other);
});
test("exported_store_reads_back", async () => {
  const repo = bareRemote();
  const texts = new Map([
    ...files,
    ['lodge/a space\tand\nquote".md', "Text\n"],
    ["lodge/link", "../spec"],
  ]);
  await exportStore(target(repo), texts, "Export");
  expect((await readStore(repo, "lodge")).files).toEqual(texts);
  expect(git(repo, "ls-tree", "lodge", "lodge/link")).toStartWith("100644 blob");
});
