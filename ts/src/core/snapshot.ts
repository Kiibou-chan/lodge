import { parseArea, parseRecord } from "./fileformat.ts";
import {
  type Area,
  type Decision,
  type Problem,
  problem,
  type SpecEntry,
  type Thread,
} from "./model.ts";
import { byCodePoint } from "./text.ts";
import { parseThread } from "./threads.ts";
export type Files = ReadonlyMap<string, string>;
export interface Tree {
  // Revision read from git, or null for a tree not read from git.
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
// Unreadable files and repeated IDs become problems; the first ID is kept.
export function load(tree: Tree): Snapshot {
  const threads = new Map<string, Thread>(),
    decisions = new Map<string, Decision>(),
    entries = new Map<string, SpecEntry>(),
    areas = new Map<string, Area>(),
    paths = new Map<string, string>(),
    problems: Problem[] = [],
    attachments = new Set(tree.attachments);
  for (const path of [...tree.files.keys()].sort(byCodePoint)) {
    const text = tree.files.get(path) as string;
    if (path.startsWith(ATTACHMENTS)) {
      attachments.add(path);
      continue;
    }
    if (THREAD_FILE.test(path)) keepThread(path, parseThread(path, text), threads, paths, problems);
    else if (AREA_FILE.test(path)) keepArea(parseArea(path, text), areas, problems);
    else if (DECISION_FILE.test(path) || SPEC_FILE.test(path))
      keepRecord(path, parseRecord(path, text), decisions, entries, paths, problems);
    else if (path.startsWith("lodge/") && !path.endsWith("/.gitkeep"))
      problems.push(problem({ path, check: 1, message: STRAY }));
  }
  return { decisions, entries, areas, paths, problems, attachments, threads };
}

const THREAD_FILE = /^lodge\/threads\/[^/]+\.md$/u;
const DECISION_FILE = /^lodge\/decisions\/[^/]+\.md$/u;
const AREA_FILE = /^lodge\/spec\/[^/]+\/_area\.md$/u;
const SPEC_FILE = /^lodge\/spec\/[^/]+\/[^/]+\.md$/u;
function keepArea(parsed: Area | Problem, areas: Map<string, Area>, problems: Problem[]): void {
  if (parsed.kind === "problem") problems.push(parsed);
  else areas.set(parsed.name, parsed);
}
function keepRecord(
  path: string,
  parsed: Decision | SpecEntry | Problem,
  decisions: Map<string, Decision>,
  entries: Map<string, SpecEntry>,
  paths: Map<string, string>,
  problems: Problem[],
): void {
  if (parsed.kind === "problem") {
    problems.push(parsed);
    return;
  }
  if (path.startsWith("lodge/decisions/") !== (parsed.kind === "decision")) {
    const home = parsed.kind === "decision" ? "lodge/decisions/" : "lodge/spec/<area>/";
    problems.push(problem({ path, check: 1, message: `this record belongs in ${home}` }));
  } else if (paths.has(parsed.id))
    problems.push(...duplicate(paths.get(parsed.id) as string, path, parsed.id));
  else {
    paths.set(parsed.id, path);
    if (parsed.kind === "decision") decisions.set(parsed.id, parsed);
    else entries.set(parsed.id, parsed);
  }
}
function keepThread(
  path: string,
  parsed: Thread | Problem,
  threads: Map<string, Thread>,
  paths: Map<string, string>,
  problems: Problem[],
): void {
  if (parsed.kind === "problem") problems.push(parsed);
  else if (paths.has(parsed.id))
    problems.push(...duplicate(paths.get(parsed.id) as string, path, parsed.id));
  else {
    paths.set(parsed.id, path);
    threads.set(parsed.id, parsed);
  }
}
function duplicate(kept: string, path: string, id: string): Problem[] {
  const message = `the ID ${id} is in both ${kept} and ${path}; the first is kept`;
  return [problem({ path: kept, check: 2, message }), problem({ path, check: 2, message })];
}
