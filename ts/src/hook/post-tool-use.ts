import { isAbsolute, join, relative } from "node:path";
import {
  FROZEN_TEXT,
  MOVED_FROZEN_TEXT,
  MOVED_RECORD_TEXT,
  MOVED_THREAD_TEXT,
  RECORD_TEXT,
  THREAD_TEXT,
} from "./texts.ts";

export interface HookContext {
  readonly repoRoot: string;
  readonly dataRoot: string | null;
  readonly frozen: readonly string[];
  readonly server: string | null;
}
export type Resolve = (path: string) => string;
interface HookOutput {
  readonly hookSpecificOutput: {
    readonly hookEventName: "PostToolUse";
    readonly additionalContext: string;
  };
}
function mapping(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null && !Array.isArray(value);
}
function editedPath(payload: unknown, fallback: string | null): string | null {
  if (!mapping(payload)) return null;
  const { tool_name: tool, tool_input: input, cwd: folder } = payload;
  if (typeof tool !== "string" || !["Edit", "Write", "MultiEdit"].includes(tool) || !mapping(input))
    return null;
  const { file_path: path } = input;
  if (typeof path !== "string" || !path) return null;
  const base = typeof folder === "string" && folder ? folder : fallback;
  // Resolution applies parent segments after the preceding symbolic links.
  return !base || isAbsolute(path) ? path : `${base}/${path}`;
}
function within(path: string, root: string): boolean {
  const part = relative(root, path);
  return part !== ".." && !part.startsWith("../") && !isAbsolute(part);
}
function glob(pattern: string): RegExp {
  let out = "";
  const chars = Array.from(pattern);
  for (let i = 0; i < chars.length; i++) {
    const ch = chars[i] as string;
    if (ch === "*" && chars[i + 1] === "*") {
      if (chars[i + 2] === "/") {
        out += "(?:.*/)?";
        i += 2;
      } else {
        out += ".*";
        i++;
      }
    } else if (ch === "*") out += "[^/]*";
    else if (ch === "?") out += "[^/]";
    else out += "^$\\.*+?()[]{}|/".includes(ch) ? `\\${ch}` : ch;
  }
  return new RegExp(`^(?:${out})$`, "u");
}
export function respond(
  payload: unknown,
  context: HookContext,
  resolve: Resolve,
  cwd: string | null = null,
): HookOutput | null {
  const root = resolve(context.repoRoot);
  const edited = editedPath(payload, cwd || root);
  if (edited === null) return null;
  const path = resolve(edited);
  const moved = context.server !== null;
  const data = moved
    ? resolve(join(root, "lodge"))
    : context.dataRoot === null
      ? null
      : resolve(context.dataRoot);
  let template: string;
  if (data !== null && within(path, data) && !within(path, join(data, "attachments"))) {
    const thread = within(path, join(data, "threads"));
    template = moved
      ? thread
        ? MOVED_THREAD_TEXT
        : MOVED_RECORD_TEXT
      : thread
        ? THREAD_TEXT
        : RECORD_TEXT;
  } else if (
    within(path, root) &&
    context.frozen.some((pattern) => glob(pattern).test(relative(root, path)))
  ) {
    template = moved ? MOVED_FROZEN_TEXT : FROZEN_TEXT;
  } else return null;
  const shown = within(path, root) ? relative(root, path) : path;
  return {
    hookSpecificOutput: {
      hookEventName: "PostToolUse",
      additionalContext: template.replace(/\{path\}|\{server\}/gu, (token) =>
        token === "{path}" ? shown : (context.server ?? ""),
      ),
    },
  };
}
export async function run(
  read: () => Promise<string>,
  out: (text: string) => void,
  context: (edited: string) => Promise<HookContext | null>,
  resolve: Resolve,
  cwd: string | null,
): Promise<0> {
  try {
    const payload: unknown = JSON.parse(await read());
    const edited = editedPath(payload, cwd);
    if (edited === null) return 0;
    const found = await context(edited);
    if (found === null) return 0;
    const response = respond(payload, found, resolve, cwd);
    if (response !== null) out(`${JSON.stringify(response)}\n`);
  } catch {
    return 0;
  }
  return 0;
}
