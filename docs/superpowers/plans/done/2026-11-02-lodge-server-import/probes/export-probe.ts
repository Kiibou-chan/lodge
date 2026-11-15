// Commit a whole lodge/ tree into a branch through a temporary index, as gitstore's commit_files does,
// with the blobs hashed in one `hash-object --stdin-paths` and the index filled in one `update-index --index-info`.
import { mkdtempSync, mkdirSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";

const env = { ...process.env, GIT_CONFIG_GLOBAL: "/dev/null", GIT_CONFIG_NOSYSTEM: "1", GIT_AUTHOR_NAME: "lodge", GIT_AUTHOR_EMAIL: "lodge@export.invalid", GIT_COMMITTER_NAME: "lodge", GIT_COMMITTER_EMAIL: "lodge@export.invalid" };
function git(cwd: string, args: string[], input?: string, extra: Record<string, string> = {}): { code: number; out: string; err: string } {
  const p = Bun.spawnSync(["git", "-C", cwd, ...args], { env: { ...env, ...extra }, stdin: input === undefined ? "ignore" : Buffer.from(input) });
  return { code: p.exitCode, out: p.stdout.toString().trim(), err: p.stderr.toString().trim() };
}
function exportTree(repo: string, branch: string, files: Map<string, string>, message: string): string {
  const tip = git(repo, ["rev-parse", "--verify", "-q", `refs/heads/${branch}^{commit}`]).out || null;
  const tmp = mkdtempSync(join(tmpdir(), "export-"));
  try {
    const paths = [...files.keys()].sort();
    paths.forEach((p, i) => writeFileSync(join(tmp, `b${i}`), files.get(p) as string));
    const shas = git(repo, ["hash-object", "-w", "--no-filters", "--stdin-paths"], paths.map((_, i) => join(tmp, `b${i}`)).join("\n") + "\n").out.split("\n");
    const index = { GIT_INDEX_FILE: join(tmp, "index") };
    const info = paths.map((p, i) => `100644 blob ${shas[i]}\t${p}\0`).join("");
    const filled = git(repo, ["update-index", "-z", "--index-info"], info, index);
    if (filled.code !== 0) throw new Error(filled.err);
    const tree = git(repo, ["write-tree"], undefined, index).out;
    if (tip && git(repo, ["rev-parse", `${tip}^{tree}`]).out === tree) return "unchanged";
    const commit = git(repo, ["commit-tree", tree, ...(tip ? ["-p", tip] : []), "-F", "-"], message + "\n").out;
    const moved = git(repo, ["update-ref", `refs/heads/${branch}`, commit, tip ?? "0".repeat(40)]);
    if (moved.code !== 0) throw new Error(moved.err);
    return commit;
  } finally {
    rmSync(tmp, { recursive: true, force: true });
  }
}
const root = mkdtempSync(join(tmpdir(), "probe-"));
const bare = join(root, "target.git");
mkdirSync(bare);
git(bare, ["init", "-q", "--bare", "-b", "main"]);
const files = new Map<string, string>();
for (let i = 0; i < 400; i++) files.set(`lodge/decisions/d-${String(i).padStart(6, "0")}-x.md`, `---\nid: d-${i}\n---\n\nText ${i}, «é».\n`);
files.set("lodge/decisions/.gitkeep", "");
files.set("lodge/spec/.gitkeep", "");
let t = performance.now();
const first = exportTree(bare, "lodge", files, "Export lodge records");
console.log(`bare target, 402 files: first export ${first.slice(0, 7)} in ${Math.round(performance.now() - t)} ms`);
t = performance.now();
console.log(`same files again: ${exportTree(bare, "lodge", files, "x")} in ${Math.round(performance.now() - t)} ms`);
files.set("lodge/decisions/d-000001-x.md", "changed\n");
const second = exportTree(bare, "lodge", files, "Export lodge records");
console.log(`one file changed: parent of the new commit is the first: ${git(bare, ["rev-parse", `${second}^`]).out === first}`);
console.log(`files at the tip: ${git(bare, ["ls-tree", "-r", "--name-only", "lodge"]).out.split("\n").length}; text kept: ${git(bare, ["show", "lodge:lodge/decisions/d-000002-x.md"]).out.includes("«é»")}`);
console.log(`author: ${git(bare, ["log", "-1", "--format=%an <%ae>", "lodge"]).out}`);
const stale = git(bare, ["update-ref", "refs/heads/lodge", first, first]);
console.log(`update-ref with a stale old value: exit ${stale.code}: ${stale.err.split("\n")[0]}`);
const work = join(root, "work");
git(root, ["clone", "-q", bare, work]);
git(work, ["checkout", "-q", "lodge"]);
console.log(`worktree list names the checked-out branch: ${git(work, ["worktree", "list", "--porcelain"]).out.split("\n").filter((l) => l.startsWith("branch ")).join(", ")}`);
rmSync(root, { recursive: true, force: true });
