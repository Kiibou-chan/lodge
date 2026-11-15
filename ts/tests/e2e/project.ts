import { afterAll } from "bun:test";
import { mkdirSync, mkdtempSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { run } from "#cli";
import { version } from "../../package.json";
import { type TestClock, type TestServer, testServer } from "./server.ts";
export interface Result {
  readonly code: number;
  readonly out: string;
  readonly err: string;
}
const cleanups: (() => void)[] = [];
afterAll(() => {
  for (const cleanup of cleanups) cleanup();
});
export class Project {
  constructor(
    readonly root: string,
    readonly url: string,
    private server: TestServer,
    private unreachable: boolean,
    private binary: string | undefined,
  ) {}
  async run(...argv: string[]): Promise<Result> {
    return this.runIn(this.root, ...argv);
  }
  async runIn(cwd: string, ...argv: string[]): Promise<Result> {
    if (this.binary) {
      const child = Bun.spawn([this.binary, ...argv], {
        cwd,
        env: { PATH: process.env["PATH"], LODGE_TOKEN: this.server.token },
        stdout: "pipe",
        stderr: "pipe",
      });
      const [code, out, err] = await Promise.all([
        child.exited,
        new Response(child.stdout).text(),
        new Response(child.stderr).text(),
      ]);
      return { code, out, err };
    }
    let out = "",
      err = "";
    const code = await run(argv, {
      cwd,
      env: { LODGE_TOKEN: this.server.token },
      fetch: this.unreachable
        ? async () => {
            throw new TypeError("Unable to connect");
          }
        : this.server.fetch,
      version,
      out: (text) => {
        out += text;
      },
      err: (text) => {
        err += text;
      },
    });
    return { code, out, err };
  }
  configure(text: string): void {
    writeFileSync(
      join(this.root, ".lodge.toml"),
      `[server]\nurl = "${this.url}"\nproject = "work"\n${text}`,
    );
  }
  draft(name: string, text: string): string {
    const path = join(this.root, "..", "drafts", name);
    mkdirSync(join(this.root, "..", "drafts"), { recursive: true });
    writeFileSync(path, text);
    return path;
  }
  stored(path: string) {
    return this.server.stored("work", path);
  }
  paths() {
    return this.server.paths("work");
  }
  handEdit(files: Readonly<Record<string, string>>) {
    return this.server.handEdit("work", files);
  }
  approve(seq: number) {
    return this.server.approve("work", seq);
  }
  standStill(): TestClock {
    this.server.clock.standStill();
    return this.server.clock;
  }
}
export async function project({ unreachable = false } = {}): Promise<Project> {
  const server = await testServer(),
    folder = mkdtempSync(join(tmpdir(), "lodge-e2e-")),
    root = join(folder, "work");
  mkdirSync(join(root, ".git"), { recursive: true });
  cleanups.push(() => rmSync(folder, { recursive: true, force: true }));
  const binary = process.env["LODGE_E2E_BINARY"];
  let url = server.origin;
  if (binary) {
    const listener = Bun.serve({ hostname: "127.0.0.1", port: 0, fetch: server.fetch });
    url = `http://127.0.0.1:${listener.port}`;
    if (unreachable) listener.stop(true);
    else cleanups.push(() => listener.stop(true));
  }
  const p = new Project(root, url, server, unreachable, binary);
  p.configure("");
  return p;
}
