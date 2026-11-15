import { mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import {
  type ExportOutcome,
  type ExportTarget,
  exportTargetProblem,
  LodgeError,
  lodgePathProblem,
} from "#app";
import { decodeUtf8, encodeUtf8, splitLines, strip } from "#core";
import { attempt, resolveRev, run } from "./run.ts";

function validate(target: ExportTarget, files: ReadonlyMap<string, string>): void {
  for (const path of files.keys()) {
    const problem = lodgePathProblem(path);
    if (problem !== null) throw new LodgeError(problem);
  }
  const problem = exportTargetProblem(target);
  if (problem !== null) throw new LodgeError(problem);
}
function remoteTip(target: ExportTarget): string | null {
  const ref = `refs/heads/${target.branch}`;
  const out = run(["ls-remote", target.remote as string, ref], target.repository);
  for (const line of splitLines(out)) {
    const [sha, name] = line.split("\t");
    if (name === ref) return sha as string;
  }
  return null;
}
function makeTree(repository: string, files: ReadonlyMap<string, string>): string {
  const folder = mkdtempSync(join(tmpdir(), "lodge-export-"));
  try {
    const env = { GIT_INDEX_FILE: join(folder, "index") };
    const paths: string[] = [];
    let number = 0;
    for (const text of files.values()) {
      const path = join(folder, `blob-${number++}`);
      writeFileSync(path, encodeUtf8(text));
      paths.push(path);
    }
    const shas = paths.length
      ? run(
          ["hash-object", "-w", "--no-filters", "--stdin-paths"],
          repository,
          env,
          `${paths.join("\n")}\n`,
        ).split("\n")
      : [];
    const entries = [...files.keys()].map((path, i) => `100644 ${shas[i]}\t${path}\0`).join("");
    run(["update-index", "-z", "--index-info"], repository, env, encodeUtf8(entries));
    return run(["write-tree"], repository, env);
  } finally {
    rmSync(folder, { recursive: true, force: true });
  }
}
function failure(stderr: Uint8Array, stdout: Uint8Array, command: string): LodgeError {
  const lines = [...splitLines(decodeUtf8(stderr)), ...splitLines(decodeUtf8(stdout))];
  return new LodgeError(lines.map(strip).find(Boolean) || `git ${command} failed`);
}
export async function exportStore(
  target: ExportTarget,
  files: ReadonlyMap<string, string>,
  message: string,
): Promise<ExportOutcome> {
  validate(target, files);
  const { repository, branch, remote } = target;
  const ref = `refs/heads/${branch}`;
  const tip = remote !== null ? remoteTip(target) : resolveRev(repository, ref);
  if (remote !== null && tip !== null)
    run(["fetch", "--quiet", "--no-tags", remote, ref], repository);
  if (
    remote === null &&
    splitLines(run(["worktree", "list", "--porcelain"], repository)).includes(`branch ${ref}`)
  )
    throw new LodgeError(
      `${branch} is checked out in a work tree of ${repository}; the export writes only a branch no work tree has checked out`,
    );
  if (tip !== null) {
    const paths = run(["ls-tree", "-r", "-z", "--name-only", tip], repository)
      .split("\0")
      .filter(Boolean);
    if (paths.some((path) => !path.startsWith("lodge/")))
      throw new LodgeError(
        `${branch} holds files outside lodge/, so it is not a branch lodge exports to; name a branch of its own`,
      );
  }
  const tree = makeTree(repository, files);
  if (tip !== null && tree === run(["rev-parse", `${tip}^{tree}`], repository))
    return { kind: "unchanged" };
  const identity = {
    GIT_AUTHOR_NAME: "lodge",
    GIT_AUTHOR_EMAIL: "lodge@export.invalid",
    GIT_COMMITTER_NAME: "lodge",
    GIT_COMMITTER_EMAIL: "lodge@export.invalid",
  };
  const commit = run(
    ["commit-tree", tree, ...(tip === null ? [] : ["-p", tip]), "-F", "-"],
    repository,
    identity,
    `${message.replace(/\n+$/, "")}\n`,
  );
  const args =
    remote !== null
      ? ["push", "--porcelain", remote, `${commit}:${ref}`]
      : ["update-ref", ref, commit, tip ?? "0".repeat(40)];
  const done = attempt(args, repository);
  if (done.code === 0) return { kind: "committed", commit };
  const error = failure(done.stderr, done.stdout, args[0] as string);
  let current: string | null;
  try {
    current = remote !== null ? remoteTip(target) : resolveRev(repository, ref);
  } catch {
    throw error;
  }
  if (current !== tip) return { kind: "moved" };
  throw error;
}
