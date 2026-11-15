import {
  type Accounts,
  type Actor,
  type Clock,
  type Exporters,
  type ExportTargets,
  type IdSource,
  Lodge,
  type Projects,
  type ZeroTwoCopy,
} from "#app";
import type { CoreSettings } from "#core";
export interface Moving {
  readonly read: (repository: string, rev: string, settingsRev: string) => Promise<ZeroTwoCopy>;
  readonly targets: ExportTargets;
  readonly exporters: Exporters;
}

export interface ApiOptions {
  readonly moving?: Moving;
  readonly accounts: Accounts;
  readonly projects: Projects;
  readonly lodgeFor: (project: string, settings: CoreSettings, actor: Actor) => Lodge;
  readonly clock: Clock;
  readonly random: (bytes: number) => Uint8Array;
  readonly version: string;
  readonly log: (text: string) => void;
}
export function lodgesOver(
  projects: Projects,
  clock: Clock,
  ids: IdSource,
): ApiOptions["lodgeFor"] {
  return (project, settings, actor) =>
    new Lodge(projects.storeFor(project, actor), clock, ids, settings, actor);
}

export const MAX_REQUEST_BODY_SIZE = 8 * 1024 * 1024;
