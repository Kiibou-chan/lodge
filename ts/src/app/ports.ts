import type { Tree } from "#core";

export interface Now {
  readonly epochMs: number;
  readonly offsetMinutes: number;
}
export interface Clock {
  now(): Now;
  // Wait so that now moves on by at least seconds.
  sleep(seconds: number): Promise<void>;
}
export interface IdSource {
  // At least six random bytes.
  entropy(): Uint8Array;
}
export const PublishOutcome = {
  PUBLISHED: "published",
  STAGED: "staged",
  REJECTED: "rejected",
} as const;
export type PublishOutcome = (typeof PublishOutcome)[keyof typeof PublishOutcome];
export const CommitOutcome = {
  COMMITTED: "committed",
  ON_BASE: "on the base branch",
  DETACHED: "on a detached HEAD",
  IN_PROGRESS: "during a merge, rebase, cherry-pick, or revert",
  LOCKED: "git's index is locked by another process",
  FAILED: "git could not commit",
} as const;
export type CommitOutcome = (typeof CommitOutcome)[keyof typeof CommitOutcome];
export interface Committed {
  readonly outcome: CommitOutcome;
  readonly detail: string;
}
export function committed(value: Pick<Committed, "outcome"> & Partial<Committed>): Committed {
  return { detail: "", ...value };
}
export interface Gate {
  readonly published: Tree;
  readonly checked: readonly (readonly [string, Tree])[];
  readonly notes: readonly string[];
}
export function gate(value: Omit<Gate, "notes"> & Partial<Gate>): Gate {
  return { notes: [], ...value };
}
export interface Store {
  // Commit exactly these paths with checkout identity and hooks, leaving other staged files staged.
  // The outcome explains why when no commit is made.
  commit(paths: readonly string[], message: string): Promise<Committed>;
  // The current and published states from one read.
  trees(): Promise<readonly [Tree, Tree]>;
  // Every attachment’s text by path.
  attachmentTexts(): Promise<ReadonlyMap<string, string>>;
  // Freshness of shared branch data, or null for local data.
  freshness(): Promise<string | null>;
  // Compare the returned current tree; throw LodgeError if there is no published state.
  gate(current: Tree): Promise<Gate>;
  // Write on base; reject when a written path or the branch tip no longer matches base.
  publish(
    base: Tree,
    writes: ReadonlyMap<string, string>,
    message: string,
  ): Promise<PublishOutcome>;
}
export type Actor =
  | { readonly kind: "person"; readonly name: string }
  | { readonly kind: "agent"; readonly role: string | null };
export function person(name: string): Actor {
  return { kind: "person", name };
}
export function agent(role: string | null = null): Actor {
  return { kind: "agent", role };
}
export function actorText(actor: Actor): string {
  return actor.kind === "person"
    ? actor.name
    : actor.role === null
      ? "agent"
      : `agent ${actor.role}`;
}
export const Role = { OWNER: "owner", MEMBER: "member" } as const;
export type Role = (typeof Role)[keyof typeof Role];
export interface Projects {
  create(project: string, owner: string): Promise<void>;
  members(project: string): Promise<ReadonlyMap<string, Role>>;
  addMember(project: string, person: string, role: Role, by: Actor): Promise<void>;
  storeFor(project: string, actor: Actor): Store;
}
