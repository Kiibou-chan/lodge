import { type Io, run } from "#cli";
import { project } from "../e2e/project.ts";

export const failure = (err: string) => ({ code: 2, out: "", err });
export async function clientHarness() {
  const cli = await project();
  async function invoke(fetch: Io["fetch"], token?: string, argv = ["search"]) {
    let out = "",
      err = "";
    const code = await run(argv, {
      cwd: cli.root,
      env: { LODGE_TOKEN: token },
      version: "0.3.0",
      fetch,
      out: (t) => {
        out += t;
      },
      err: (t) => {
        err += t;
      },
    });
    return { code, out, err };
  }
  return { cli, invoke };
}
export function answer(body: unknown, version: string | null = "0.3.0", status = 200) {
  return new Response(JSON.stringify(body), {
    status,
    headers: version === null ? {} : { "Lodge-Version": version },
  });
}
