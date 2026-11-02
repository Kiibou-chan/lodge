import { parseArea, parseRecord } from "./fileformat.ts";
import {
  type Area,
  type Decision,
  type Problem,
  problem,
  type SpecEntry,
  type Thread,
} from "./model.ts";
import { parseThread } from "./threads.ts";
export type Files = ReadonlyMap<string, string>;
export interface Tree {
  readonly rev: string | null;
  readonly files: Files;
  readonly attachments: ReadonlySet<string>;
}
export function tree(value: Omit<Tree, "attachments"> & Partial<Pick<Tree, "attachments">>): Tree {
  return { attachments: new Set(), ...value };
}
export interface Snapshot {
  readonly decisions: ReadonlyMap<string, Decision>;
  readonly entries: ReadonlyMap<string, SpecEntry>;
  readonly areas: ReadonlyMap<string, Area>;
  readonly paths: ReadonlyMap<string, string>;
  readonly problems: readonly Problem[];
  readonly attachments: ReadonlySet<string>;
  readonly threads: ReadonlyMap<string, Thread>;
}
export const ATTACHMENTS = "lodge/attachments/";
export function attachmentPath(decisionId: string, name: string): string {
  return `${ATTACHMENTS}${decisionId}/${name}`;
}
const STRAY =
  "this file is not a record; lodge holds decisions in lodge/decisions/, specification entries in lodge/spec/<area>/, and attachments in lodge/attachments/";
function compare(a: string, b: string): number {
  const x = Array.from(a, (c) => c.codePointAt(0) as number),
    y = Array.from(b, (c) => c.codePointAt(0) as number);
  for (let i = 0; i < Math.min(x.length, y.length); i++) {
    const d = (x[i] as number) - (y[i] as number);
    if (d) return d;
  }
  return x.length - y.length;
}
export function load(tree: Tree): Snapshot {
  const threads = new Map<string, Thread>(),
    decisions = new Map<string, Decision>(),
    entries = new Map<string, SpecEntry>(),
    areas = new Map<string, Area>(),
    paths = new Map<string, string>(),
    problems: Problem[] = [],
    attachments = new Set(tree.attachments);
  for (const path of [...tree.files.keys()].sort(compare)) {
    const text = tree.files.get(path) as string;
    if (path.startsWith(ATTACHMENTS)) {
      attachments.add(path);
      continue;
    }
    if (/^lodge\/spec\/[^/]+\/_area\.md$/u.test(path)) {
      const parsed = parseArea(path, text);
      if (parsed.kind === "problem") problems.push(parsed);
      else areas.set(parsed.name, parsed);
      continue;
    }
    const threadFile = /^lodge\/threads\/[^/]+\.md$/u.test(path);
    if (
      threadFile ||
      /^lodge\/decisions\/[^/]+\.md$/u.test(path) ||
      /^lodge\/spec\/[^/]+\/[^/]+\.md$/u.test(path)
    ) {
      const parsed = threadFile ? parseThread(path, text) : parseRecord(path, text);
      if (parsed.kind === "problem") {
        problems.push(parsed);
        continue;
      }
      if (
        parsed.kind !== "thread" &&
        path.startsWith("lodge/decisions/") !== (parsed.kind === "decision")
      ) {
        const home = parsed.kind === "decision" ? "lodge/decisions/" : "lodge/spec/<area>/";
        problems.push(problem({ path, check: 1, message: `this record belongs in ${home}` }));
        continue;
      }
      const kept = paths.get(parsed.id);
      if (kept !== undefined) {
        const message = `the ID ${parsed.id} is in both ${kept} and ${path}; the first is kept`;
        problems.push(
          problem({ path: kept, check: 2, message }),
          problem({ path, check: 2, message }),
        );
        continue;
      }
      paths.set(parsed.id, path);
      if (parsed.kind === "thread") threads.set(parsed.id, parsed);
      else if (parsed.kind === "decision") decisions.set(parsed.id, parsed);
      else entries.set(parsed.id, parsed);
    } else if (path.startsWith("lodge/") && !path.endsWith("/.gitkeep"))
      problems.push(problem({ path, check: 1, message: STRAY }));
  }
  return { decisions, entries, areas, paths, problems, attachments, threads };
}
