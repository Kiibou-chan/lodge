import type { Tree } from "#core";
import { type Actor, type Projects, PublishOutcome, type Store } from "./ports.ts";

export interface ExportTarget {
  readonly repository: string;
  readonly branch: string;
  readonly remote: string | null;
}
export type ExportOutcome =
  | { readonly kind: "committed"; readonly commit: string }
  | { readonly kind: "unchanged" }
  | { readonly kind: "moved" };
export interface ExportTargets {
  target(project: string): Promise<ExportTarget | null>;
  setTarget(project: string, target: ExportTarget | null, by: Actor): Promise<void>;
}
export const KEPT: readonly string[] = ["lodge/decisions/.gitkeep", "lodge/spec/.gitkeep"];

export function exportTargetProblem(target: ExportTarget): string | null {
  if (!target.repository.startsWith("/"))
    return "export-target: repository must be an absolute path";
  if (
    !/^[A-Za-z0-9]/.test(target.branch) ||
    /[^A-Za-z0-9._/-]/.test(target.branch) ||
    target.branch.includes("..")
  )
    return "export-target: branch must be a name of letters, digits, and . _ / -, not starting with a symbol";
  if (target.remote?.startsWith("-")) return "export-target: remote must not start with -";
  return null;
}

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
              const value = Reflect.get(inner, member, inner);
              return typeof value === "function" ? value.bind(inner) : value;
            },
          });
        };
      const value = Reflect.get(target, key, target);
      return typeof value === "function" ? value.bind(target) : value;
    },
  });
}
