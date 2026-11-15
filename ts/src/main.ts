import { listen, lodgesOver, serverCommand, withoutYamlLogging } from "#api";
import type { Clock } from "#app";
import { run } from "#cli";
import { openDatabase, SqliteAccounts, SqliteProjects } from "#store";
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
const argv = process.argv.slice(2);
process.exitCode =
  argv[0] === "server"
    ? await serverCommand(argv.slice(1), {
        out,
        err,
        listen,
        open: async (data) => {
          const database = await openDatabase(data);
          const accounts = new SqliteAccounts(database, clock);
          const projects = new SqliteProjects(database, clock);
          return {
            options: {
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
