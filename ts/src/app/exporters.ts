import {
  type ExportOutcome,
  type ExportTarget,
  type ExportTargets,
  exportFiles,
  exportMessage,
} from "./exporting.ts";
import type { Clock, Store } from "./ports.ts";

export interface ExportPorts {
  readonly clock: Clock;
  readonly targets: ExportTargets;
  readonly storeFor: (project: string) => Store;
  readonly write: (
    target: ExportTarget,
    files: ReadonlyMap<string, string>,
    message: string,
  ) => Promise<ExportOutcome>;
  readonly failed: (project: string, error: unknown) => void;
}
export const EXPORT_INTERVAL_SECONDS = 60;
interface ProjectRun {
  pending: boolean;
  lastCommit: number | null;
  running: Promise<void> | null;
}
export class Exporters {
  private readonly projects = new Map<string, ProjectRun>();
  constructor(private readonly ports: ExportPorts) {}

  written(project: string): Promise<void> {
    let state = this.projects.get(project);
    if (!state) {
      state = { pending: false, lastCommit: null, running: null };
      this.projects.set(project, state);
    }
    state.pending = true;
    state.running ??= this.run(project, state);
    return state.running;
  }

  async start(projects: readonly string[]): Promise<void> {
    await Promise.all(
      projects.map(async (project) => {
        if (await this.ports.targets.target(project)) await this.written(project);
      }),
    );
  }

  async settled(): Promise<void> {
    while (true) {
      const running = [...this.projects.values()].flatMap((state) =>
        state.running ? [state.running] : [],
      );
      if (!running.length) return;
      await Promise.all(running);
    }
  }

  private async run(project: string, state: ProjectRun): Promise<void> {
    const { clock } = this.ports;
    try {
      while (state.pending) {
        if (state.lastCommit !== null) {
          const seconds = EXPORT_INTERVAL_SECONDS - (clock.now().epochMs - state.lastCommit) / 1000;
          if (seconds > 0) await clock.sleep(seconds);
        }
        state.pending = false;
        let retry = false;
        try {
          const target = await this.ports.targets.target(project);
          if (target) {
            const store = this.ports.storeFor(project);
            const [current] = await store.trees();
            const files = exportFiles(current, await store.attachmentTexts());
            const outcome = await this.ports.write(target, files, exportMessage(files));
            if (outcome.kind === "committed") state.lastCommit = clock.now().epochMs;
            retry = outcome.kind === "moved";
          }
        } catch (error) {
          this.ports.failed(project, error);
          retry = true;
        }
        if (retry) {
          state.pending = true;
          await clock.sleep(EXPORT_INTERVAL_SECONDS);
        }
      }
    } finally {
      state.running = null;
    }
  }
}
