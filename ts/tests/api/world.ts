import { type ApiOptions, handler, hashSecret, issueToken, lodgesOver, type Moving } from "#api";
import { agent, Exporters, exportFailedLine, exportingProjects, LodgeError } from "#app";
import { CliError, zeroTwoCoreTable } from "#cli";
import { exportStore, readStore } from "#git";
import { openDatabase, SqliteAccounts, SqliteExportTargets, SqliteProjects } from "#store";
import { CountingIds, FixedClock } from "../app/fakes.ts";

const SESSION_SECRET = "synthetic-session";
export const SESSION_COOKIE = `lodge_session=${SESSION_SECRET}`;

export async function world(setUp = true) {
  const database = await openDatabase(":memory:");
  const clock = new FixedClock();
  const accounts = new SqliteAccounts(database, clock);
  const inner = new SqliteProjects(database, clock);
  if (setUp)
    await accounts.setUp({
      origin: "https://lodge.test",
      person: "ada",
      at: "2026-10-29T09:30:00+01:00",
    });
  const logs: string[] = [];
  const log = (text: string) => logs.push(text);
  const targets = new SqliteExportTargets(database, clock);
  const exporters = new Exporters({
    clock,
    targets,
    storeFor: (project) => inner.storeFor(project, agent("exporter")),
    write: exportStore,
    failed: (project, error) => log(exportFailedLine(project, error)),
  });
  const projects = exportingProjects(inner, (project) => {
    void exporters
      .written(project)
      .catch((error: unknown) => log(exportFailedLine(project, error)));
  });
  await projects.create("work", "ada");
  const moving: Moving = {
    targets,
    exporters,
    read: async (repository, rev, settingsRev) => {
      const copy = await readStore(repository, rev, settingsRev);
      try {
        return { ...copy, settings: copy.settings === null ? {} : zeroTwoCoreTable(copy.settings) };
      } catch (error) {
        if (error instanceof CliError) throw new LodgeError(error.message);
        throw error;
      }
    },
  };
  let counter = 0;
  const options: ApiOptions = {
    moving,
    accounts,
    projects,
    clock,
    lodgeFor: lodgesOver(projects, clock, new CountingIds()),
    random: (n) => new Uint8Array(n).fill(++counter),
    version: "0.3.0",
    log: (text) => logs.push(text),
  };
  const issued = await issueToken(options, "work", "test", null);
  function request(operation: string, body: unknown = {}, secret: string | null = issued.secret) {
    return new Request(`https://lodge.test/api/v1/${operation}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(secret === null ? {} : { Authorization: `Bearer ${secret}` }),
      },
      body: JSON.stringify(body),
    });
  }
  const fetch = handler(options);
  let session = false;
  async function asPerson(operation: string, body: Readonly<Record<string, unknown>> = {}) {
    const secret = SESSION_SECRET;
    if (!session) {
      await accounts.startSession(
        hashSecret(secret),
        new Date(clock.now().epochMs + 2592000000).toISOString(),
      );
      session = true;
    }
    const req = request(operation, body, null);
    req.headers.set("Cookie", SESSION_COOKIE);
    req.headers.set("Origin", "https://lodge.test");
    return fetch(req);
  }
  const createProject = (project: string, settings: Readonly<Record<string, unknown>>) =>
    projects.create(project, "ada", settings);
  return {
    database,
    accounts,
    projects,
    options,
    logs,
    issued,
    request,
    fetch,
    clock,
    exporters,
    targets,
    createProject,
    asPerson,
  };
}
