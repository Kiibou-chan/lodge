import { listen, lodgesOver, serverCommand, withoutYamlLogging } from "#api";
import {
  agent,
  type Clock,
  Exporters,
  exportFailedLine,
  exportingProjects,
  LodgeError,
  type Projects,
} from "#app";
import { CliError, run, zeroTwoCoreTable } from "#cli";
import { exportStore, readStore } from "#git";
import { openDatabase, SqliteAccounts, SqliteExportTargets, SqliteProjects } from "#store";
import pkg from "../package.json" with { type: "json" };

withoutYamlLogging(process.env);

const clock: Clock = {
  now: () => ({ epochMs: Date.now(), offsetMinutes: -new Date().getTimezoneOffset() }),
  sleep: (seconds) => new Promise((resolve) => setTimeout(resolve, seconds * 1000)),
};
const random = (bytes: number) => crypto.getRandomValues(new Uint8Array(bytes));
const ids = { entropy: () => random(8) };
const out = (text: string) => {
  process.stdout.write(text);
};
const err = (text: string) => {
  process.stderr.write(text);
};
let serving: { exporters: Exporters; projects: Projects } | undefined;
const argv = process.argv.slice(2);
process.exitCode =
  argv[0] === "server"
    ? await serverCommand(argv.slice(1), {
        out,
        err,
        listen: async (fetch, host, port) => {
          if (serving) {
            const { exporters, projects } = serving;
            void exporters
              .start(await projects.names())
              .catch((error: unknown) =>
                err(
                  `lodge: starting exports failed: ${error instanceof Error ? error.message : String(error)}\n`,
                ),
              );
          }
          await listen(fetch, host, port);
        },
        open: async (data) => {
          const database = await openDatabase(data);
          const accounts = new SqliteAccounts(database, clock);
          const inner = new SqliteProjects(database, clock);
          const targets = new SqliteExportTargets(database, clock);
          const exporters = new Exporters({
            clock,
            targets,
            storeFor: (project) => inner.storeFor(project, agent("exporter")),
            write: exportStore,
            failed: (project, error) => err(exportFailedLine(project, error)),
          });
          const projects = exportingProjects(inner, (project) => {
            void exporters
              .written(project)
              .catch((error: unknown) => err(exportFailedLine(project, error)));
          });
          serving = { exporters, projects };
          return {
            options: {
              moving: {
                targets,
                exporters,
                read: async (repository, rev, settingsRev) => {
                  const copy = await readStore(repository, rev, settingsRev);
                  try {
                    return {
                      ...copy,
                      settings: copy.settings === null ? {} : zeroTwoCoreTable(copy.settings),
                    };
                  } catch (error) {
                    if (error instanceof CliError) throw new LodgeError(error.message);
                    throw error;
                  }
                },
              },
              accounts,
              projects,
              lodgeFor: lodgesOver(projects, clock, ids),
              clock,
              random,
              version: pkg.version,
              log: err,
            },
          };
        },
      })
    : await run(argv, {
        cwd: process.cwd(),
        env: process.env,
        fetch,
        out,
        err,
        version: pkg.version,
      });
