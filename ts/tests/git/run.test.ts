import { expect, test } from "bun:test";
import { LodgeError } from "#app";
import { attempt, GitMissing, resolveRev, run, runBytes } from "#git";
import { isolateGit } from "./isolated.ts";
import { commit, git, repository, temporaryFolder } from "./repos.ts";

isolateGit();
test("missing_git_is_one_sentence", () => {
  const dir = temporaryFolder();
  expect(() => attempt(["--version"], dir, { PATH: temporaryFolder() })).toThrow(GitMissing);
  expect(() => attempt(["--version"], dir, { PATH: temporaryFolder() })).toThrow(
    "git is not installed or is not on the PATH",
  );
});
test("failure_names_gits_first_line", () => {
  const repo = repository();
  expect(() => runBytes(["rev-parse", "--verify", "nope"], repo)).toThrow(LodgeError);
  expect(() => runBytes(["rev-parse", "--verify", "nope"], repo)).toThrow(
    "fatal: Needed a single revision",
  );
});
test("resolve_rev_gives_null_for_a_missing_ref", () => {
  const repo = repository();
  commit(repo, "README.md", "Made-up project\n", "Start");
  expect(resolveRev(repo, "nope")).toBeNull();
  expect(resolveRev(repo, "main")).toBe(git(repo, "rev-parse", "HEAD"));
});
test("input_reaches_git", () => {
  const repo = repository();
  for (const input of ["a\n", new Uint8Array([97, 10])]) {
    expect(run(["hash-object", "--stdin"], repo, undefined, input)).toBe(
      "78981922613b2afb6025042ff6bd878ac1994e85",
    );
  }
});
test("isolation_reaches_git", () => {
  const repo = repository();
  expect(run(["var", "GIT_AUTHOR_IDENT"], repo)).toStartWith("Test Author <test@example.com>");
  const result = attempt(["config", "--global", "--list"], repo);
  expect(result.code).toBe(0);
  expect(result.stdout).toHaveLength(0);
  expect(git(repo, "var", "GIT_AUTHOR_IDENT")).toStartWith("Test Author <test@example.com>");
  expect(git(repo, "config", "--global", "--list")).toBe("");
});
