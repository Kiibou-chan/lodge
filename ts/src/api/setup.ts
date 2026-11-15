import { stampOf } from "#app";
import { handler } from "./http.ts";
import type { ApiOptions } from "./options.ts";
import { hashSecret } from "./tokens.ts";
/** @public */
export interface ServerParts {
  readonly options: ApiOptions;
}
export interface ServerIo {
  readonly out: (text: string) => void;
  readonly err: (text: string) => void;
  readonly open: (data: string) => Promise<ServerParts>;
  readonly listen: (
    fetch: (request: Request) => Promise<Response>,
    host: string,
    port: number,
  ) => Promise<void>;
}
export async function issueSetupCode(options: ApiOptions): Promise<string> {
  const alphabet = "0123456789ABCDEFGHJKMNPQRSTVWXYZ";
  const entropy = options.random(13);
  let bits = 0,
    value = 0,
    code = "";
  for (const byte of entropy) {
    value = (value << 8) | byte;
    bits += 8;
    while (bits >= 5 && code.length < 20) {
      bits -= 5;
      code += alphabet[(value >>> bits) & 31];
    }
  }
  await options.accounts.issueSetupCode(
    hashSecret(code.toLowerCase()),
    stampOf({ ...options.clock.now(), epochMs: options.clock.now().epochMs + 900000 }),
  );
  return code.match(/.{5}/gu)?.join("-") ?? "";
}
const usage = "usage: lodge server {setup,serve} [options]\n";
function originValid(text: string): boolean {
  try {
    const url = new URL(text);
    if (
      url.username ||
      url.password ||
      url.search ||
      url.hash ||
      url.pathname !== "/" ||
      text !== url.origin
    )
      return false;
    const host = url.hostname;
    if (host.startsWith("[") || /^[0-9.]+$/u.test(host)) return false;
    return (
      url.protocol === "https:" ||
      (url.protocol === "http:" && host === "localhost" && url.port !== "")
    );
  } catch {
    return false;
  }
}
export async function serverCommand(argv: readonly string[], io: ServerIo): Promise<number> {
  if (argv.includes("--help")) {
    io.out(
      `${usage}  setup --data PATH --origin URL --person NAME\n  serve --data PATH [--host HOST] [--port PORT]\n`,
    );
    return 0;
  }
  const command = argv[0];
  const values = new Map<string, string>();
  const allowed =
    command === "setup"
      ? ["--data", "--origin", "--person"]
      : command === "serve"
        ? ["--data", "--host", "--port"]
        : [];
  const fail = (message: string) => {
    io.err(`${usage}lodge: ${message}\n`);
    return 2;
  };
  if (!command || allowed.length === 0) return fail("choose setup or serve");
  for (let i = 1; i < argv.length; i += 2) {
    const key = argv[i] ?? "",
      value = argv[i + 1];
    if (!allowed.includes(key) || values.has(key) || value === undefined || value.startsWith("--"))
      return fail("invalid server arguments");
    values.set(key, value);
  }
  const data = values.get("--data");
  if (!data) return fail("--data is required");
  if (command === "setup") {
    const origin = values.get("--origin"),
      person = values.get("--person");
    if (!origin || !person) return fail("--origin and --person are required");
    if (!originValid(origin))
      return fail("the origin must be https://<host> or http://localhost:<port>, with no path");
    if (!/^[a-z][a-z0-9-]{0,31}$/u.test(person))
      return fail(
        "the person's name must be lower-case letters, digits, and hyphens, starting with a letter",
      );
    const { options } = await io.open(data);
    const setup = await options.accounts.setup();
    if (setup && (setup.origin !== origin || setup.person !== person)) {
      io.err(`lodge: the server is set up for ${setup.origin} and ${setup.person}\n`);
      return 2;
    }
    if ((await options.accounts.passkeys()).length) {
      io.err(`lodge: a passkey is registered; sign in on ${origin} to add another\n`);
      return 2;
    }
    if (!setup) await options.accounts.setUp({ origin, person, at: stampOf(options.clock.now()) });
    const code = await issueSetupCode(options);
    io.out(
      `setup code: ${code}\nit works once, for 15 minutes: open ${origin}, enter it, and register a passkey\n`,
    );
    return 0;
  }
  const host = values.get("--host") ?? "127.0.0.1",
    portText = values.get("--port") ?? "8787";
  const port = Number(portText);
  if (!/^[0-9]+$/u.test(portText) || !Number.isInteger(port) || port < 1 || port > 65535)
    return fail("--port must be a whole number from 1 to 65535");
  const { options } = await io.open(data);
  const setup = await options.accounts.setup();
  if (!setup) {
    io.err("lodge: the server is not set up; run lodge server setup\n");
    return 2;
  }
  io.out(`serving ${setup.origin} on http://${host}:${port}\n`);
  await io.listen(handler(options), host, port);
  return 0;
}
