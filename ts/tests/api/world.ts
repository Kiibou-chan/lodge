import { type ApiOptions, handler, issueToken, lodgesOver } from "#api";
import { openDatabase, SqliteAccounts, SqliteProjects } from "#store";
import { CountingIds, FixedClock } from "../app/fakes.ts";

export async function world(setUp = true) {
  const database = await openDatabase(":memory:");
  const clock = new FixedClock();
  const accounts = new SqliteAccounts(database, clock);
  const projects = new SqliteProjects(database, clock);
  if (setUp)
    await accounts.setUp({
      origin: "https://lodge.test",
      person: "ada",
      at: "2026-10-29T09:30:00+01:00",
    });
  await projects.create("work", "ada");
  const logs: string[] = [];
  let counter = 0;
  const options: ApiOptions = {
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
  return { database, accounts, projects, options, logs, issued, request, fetch: handler(options) };
}
