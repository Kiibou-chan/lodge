import type { Branch, CheckResult, Feedback, Level1, Level3, Problem, Thread } from "#core";
import type { Committed } from "./ports.ts";

export const AddOutcome = {
  PUBLISHED: "published",
  STAGED: "staged",
  CHECK_FAILED: "check failed",
  DRY_RUN: "dry run",
  UNCHANGED: "nothing changed",
} as const;
export type AddOutcome = (typeof AddOutcome)[keyof typeof AddOutcome];
export interface Read {
  readonly freshness: string | null;
  readonly unrecorded: readonly Problem[];
  readonly statuses: ReadonlyMap<string, string>;
}
export function read(value: Omit<Read, "statuses"> & Partial<Read>): Read {
  return { statuses: new Map(), ...value };
}
export interface Shown {
  readonly level1: Level1;
  readonly level2: string | null;
  readonly level3: Level3 | null;
  readonly read: Read;
  readonly changing: readonly Level1[];
  readonly threads: readonly Thread[];
  readonly confirmable: boolean;
  readonly restsOn: readonly Branch[];
  readonly supports: readonly Level1[];
}
export interface Listed {
  readonly items: readonly Level1[];
  readonly read: Read;
  readonly more: number;
}
export function listed(value: Omit<Listed, "more"> & Partial<Listed>): Listed {
  return { more: 0, ...value };
}
export interface Added {
  readonly ids: readonly string[];
  readonly feedback: readonly Feedback[];
  readonly check: CheckResult;
  readonly outcome: AddOutcome;
  readonly freshness: string | null;
  readonly minted: readonly string[];
  readonly paths: readonly string[];
}
export function added(
  value: Omit<Added, "freshness" | "minted" | "paths"> & Partial<Added>,
): Added {
  return { freshness: null, minted: [], paths: [], ...value };
}
export interface Written {
  readonly ids: readonly string[];
  readonly outcome: AddOutcome;
  readonly check: CheckResult;
  readonly committed: Committed | null;
  readonly about: string | null;
}
export function written(value: Omit<Written, "committed" | "about"> & Partial<Written>): Written {
  return { committed: null, about: null, ...value };
}
export interface ThreadList {
  readonly items: readonly Thread[];
  readonly titles: ReadonlyMap<string, string>;
  readonly read: Read;
}
export interface ThreadShown {
  readonly thread: Thread;
  readonly about: Level1 | null;
  readonly read: Read;
}
export interface ThreadsWaiting {
  readonly forAgent: readonly Thread[];
  readonly forAuthor: readonly Thread[];
  readonly titles: ReadonlyMap<string, string>;
  readonly read: Read;
}
export interface Behind {
  readonly decision: Level1;
  readonly entries: readonly (readonly [string, string])[];
}
