import { expect, test } from "bun:test";
import { run } from "#git";
import { isolateGit } from "./isolated.ts";
import { git, repository } from "./repos.ts";

isolateGit();
test("git_helper_uses_python_strip", () => {
  const repo = repository();
  for (const [text, expected] of [
    ["\u0085record\u0085", "record"],
    ["\uFEFFrecord\uFEFF", "\uFEFFrecord\uFEFF"],
  ]) {
    const sha = run(["hash-object", "-w", "--stdin"], repo, undefined, text);
    expect(git(repo, "cat-file", "blob", sha)).toBe(expected as string);
  }
});
