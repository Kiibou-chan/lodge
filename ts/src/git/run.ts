import { LodgeError } from "#app";
import { decodeUtf8, encodeUtf8, splitLines, strip } from "#core";

export class GitMissing extends LodgeError {}
interface GitDone {
  readonly code: number;
  readonly stdout: Uint8Array;
  readonly stderr: Uint8Array;
}
export function attempt(
  args: readonly string[],
  cwd: string,
  env?: Readonly<Record<string, string>>,
  input?: Uint8Array | string,
): GitDone {
  try {
    const done = Bun.spawnSync(["git", "-C", cwd, ...args], {
      env: { ...process.env, LC_ALL: "C", GIT_TERMINAL_PROMPT: "0", ...env },
      stdin: typeof input === "string" ? encodeUtf8(input) : (input ?? "ignore"),
      stdout: "pipe",
      stderr: "pipe",
    });
    return { code: done.exitCode, stdout: done.stdout, stderr: done.stderr };
  } catch (error) {
    if (error instanceof Error && "code" in error && error.code === "ENOENT")
      throw new GitMissing("git is not installed or is not on the PATH");
    throw error;
  }
}
function firstLine(...streams: Uint8Array[]): string {
  for (const stream of streams) {
    for (const line of splitLines(new TextDecoder().decode(stream))) {
      if (strip(line)) return strip(line);
    }
  }
  return "";
}
export function runBytes(
  args: readonly string[],
  cwd: string,
  env?: Readonly<Record<string, string>>,
  input?: Uint8Array | string,
): Uint8Array {
  const done = attempt(args, cwd, env, input);
  if (done.code !== 0)
    throw new LodgeError(firstLine(done.stderr, done.stdout) || `git ${args[0]} failed`);
  return done.stdout;
}
export function run(
  args: readonly string[],
  cwd: string,
  env?: Readonly<Record<string, string>>,
  input?: Uint8Array | string,
): string {
  return decodeUtf8(runBytes(args, cwd, env, input)).replace(/\n+$/, "");
}
export function resolveRev(cwd: string, ref: string): string | null {
  const done = attempt(
    ["rev-parse", "--verify", "--quiet", "--end-of-options", `${ref}^{commit}`],
    cwd,
  );
  if (done.code === 0) return strip(decodeUtf8(done.stdout));
  if (done.code === 1) return null;
  throw new LodgeError(firstLine(done.stderr) || "git rev-parse failed");
}
