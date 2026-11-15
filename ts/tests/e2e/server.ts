import { expect } from "bun:test";
import { type ApiOptions, handler, issueSetupCode, lodgesOver } from "#api";
import { type Approved, agent, type Clock, type Now } from "#app";
import { fromWire } from "#cli";
import { openDatabase, SqliteAccounts, SqliteProjects } from "#store";
import { SoftAuthenticator } from "../api/authenticator.ts";
import { CountingIds, START } from "../app/fakes.ts";
export interface TestClock extends Clock {
  minutes(): void;
  standStill(): void;
  readonly slept: number[];
}
export interface TestServer {
  readonly fetch: (request: Request) => Promise<Response>;
  readonly origin: string;
  readonly token: string;
  readonly clock: TestClock;
  approve(project: string, seq: number): Promise<readonly string[]>;
  handEdit(project: string, files: Readonly<Record<string, string>>): Promise<void>;
  stored(project: string, path: string): Promise<string | null>;
  paths(project: string): Promise<readonly string[]>;
}
export async function testServer(): Promise<TestServer> {
  let at = START.epochMs,
    moving = false;
  const slept: number[] = [];
  const clock: TestClock = {
    slept,
    now(): Now {
      if (moving) at += 60000;
      return { epochMs: at, offsetMinutes: 60 };
    },
    async sleep(seconds) {
      slept.push(seconds);
      at += seconds * 1000;
    },
    minutes() {
      at = START.epochMs;
      moving = true;
    },
    standStill() {
      at = START.epochMs + 250;
      moving = false;
    },
  };
  const database = await openDatabase(":memory:");
  const accounts = new SqliteAccounts(database, clock),
    projects = new SqliteProjects(database, clock);
  const origin = "https://lodge.test";
  await accounts.setUp({ origin, person: "author", at: "2026-10-29T09:30:00+01:00" });
  let random = 0;
  const options: ApiOptions = {
    accounts,
    projects,
    clock,
    lodgeFor: lodgesOver(projects, clock, new CountingIds()),
    random: (n) => new Uint8Array(n).fill(++random),
    version: "0.3.0",
    log: () => {},
  };
  const fetch = handler(options);
  let cookie = "";
  async function person(op: string, body: unknown) {
    const response = await fetch(
      new Request(`${origin}/api/v1/${op}`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Origin: origin, Cookie: cookie },
        body: JSON.stringify(body),
      }),
    );
    const answer = (await response.json()) as { result: unknown };
    expect(response.status, JSON.stringify(answer)).toBe(200);
    const set = response.headers.get("Set-Cookie");
    if (set) cookie = set.split(";")[0] ?? "";
    return fromWire(answer.result);
  }
  const setupCode = await issueSetupCode(options),
    auth = new SoftAuthenticator();
  const registration = (await person("register-options", { setupCode })) as { challenge: string };
  await person("register", { setupCode, response: await auth.create(registration.challenge) });
  const issued = (await person("token-issue", { project: "work", label: "test", role: null })) as {
    secret: string;
  };
  clock.minutes();
  const store = (project: string) => projects.storeFor(project, agent("hand"));
  return {
    fetch,
    origin,
    token: issued.secret,
    clock,
    async approve(project, seq) {
      const approved = (await person("approve", { project, seq })) as Approved;
      const result = approved.kind === "add" ? approved.added : approved.written;
      expect(result.outcome).toBe("published");
      return result.ids;
    },
    async handEdit(project, files) {
      const s = store(project);
      const [current] = await s.trees();
      expect(await s.publish(current, new Map(Object.entries(files)), "hand edit")).toBe(
        "published",
      );
    },
    async stored(project, path) {
      const s = store(project);
      if (path.startsWith("lodge/attachments/"))
        return (await s.attachmentTexts()).get(path) ?? null;
      return (await s.trees())[0].files.get(path) ?? null;
    },
    async paths(project) {
      const s = store(project);
      return [...(await s.trees())[0].files.keys(), ...(await s.attachmentTexts()).keys()].sort();
    },
  };
}
