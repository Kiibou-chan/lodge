import type { Tree } from "#core";
import type { ExportTarget } from "./export-rules.ts";
import { type Actor, type Projects, PublishOutcome, type Store } from "./ports.ts";

export interface ExportTargets {
  target(project: string): Promise<ExportTarget | null>;
  setTarget(project: string, target: ExportTarget | null, by: Actor): Promise<void>;
}
export const KEPT: readonly string[] = ["lodge/decisions/.gitkeep", "lodge/spec/.gitkeep"];

export function exportFiles(
  current: Tree,
  attachmentTexts: ReadonlyMap<string, string>,
): ReadonlyMap<string, string> {
  return new Map([
    ...[...current.files].filter(([path]) => !path.endsWith("/.gitkeep")),
    ...attachmentTexts,
    ...KEPT.map((path) => [path, ""] as const),
  ]);
}

export function exportMessage(files: ReadonlyMap<string, string>): string {
  let decisions = 0,
    entries = 0,
    areas = 0,
    threads = 0;
  for (const path of files.keys()) {
    if (/^lodge\/decisions\/[^/]+\.md$/u.test(path)) decisions++;
    else if (/^lodge\/spec\/[^/]+\/_area\.md$/u.test(path)) areas++;
    else if (/^lodge\/spec\/[^/]+\/[^/]+\.md$/u.test(path)) entries++;
    else if (/^lodge\/threads\/[^/]+\.md$/u.test(path)) threads++;
  }
  return `Export lodge records: ${decisions} decisions, ${entries} entries, ${areas} areas, ${threads} threads`;
}

export function exportFailedLine(project: string, error: unknown): string {
  return `lodge: the export of ${project} failed: ${error instanceof Error ? error.message : String(error)}\n`;
}

export function exportingProjects(
  projects: Projects,
  written: (project: string) => void,
): Projects {
  return new Proxy(projects, {
    get(target, key) {
      if (key === "storeFor")
        return (project: string, actor: Actor): Store => {
          const store = target.storeFor(project, actor);
          return new Proxy(store, {
            get(inner, member) {
              if (member === "publish")
                return async (...args: Parameters<Store["publish"]>) => {
                  const outcome = await inner.publish(...args);
                  if (outcome === PublishOutcome.PUBLISHED) written(project);
                  return outcome;
                };
              return boundMember(inner, member);
            },
          });
        };
      return boundMember(target, key);
    },
  });
}

function boundMember(target: object, key: PropertyKey): unknown {
  const value = Reflect.get(target, key, target);
  return typeof value === "function" ? value.bind(target) : value;
}
