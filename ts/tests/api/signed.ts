import { hashSecret, issueSetupCode } from "#api";
import { SoftAuthenticator } from "./authenticator.ts";
import { world } from "./world.ts";
export async function ceremony() {
  const w = await world();
  const code = await issueSetupCode(w.options);
  const a = new SoftAuthenticator();
  const call = async (
    op: string,
    body: unknown = {},
    cookie?: string,
    origin: string | null = "https://lodge.test",
  ) => {
    const req = w.request(op, body, null);
    if (cookie) req.headers.set("Cookie", cookie);
    if (origin !== null) req.headers.set("Origin", origin);
    return w.fetch(req);
  };
  const challenge = async (op: string, body: unknown = {}, cookie?: string) => {
    const r = await call(op, body, cookie);
    const b = await r.text().then(JSON.parse);
    return b.result.challenge as string;
  };
  const register = async () =>
    call("register", {
      setupCode: code,
      response: await a.create(await challenge("register-options", { setupCode: code })),
    });
  return { ...w, a, code, call, challenge, register };
}
export async function signed() {
  const w = await world();
  const secret = "synthetic-session";
  await w.accounts.startSession(
    hashSecret(secret),
    new Date(w.options.clock.now().epochMs + 2592000000).toISOString(),
  );
  const call = async (op: string, body: unknown = {}) => {
    const r = w.request(op, body, null);
    r.headers.set("Cookie", `lodge_session=${secret}`);
    r.headers.set("Origin", "https://lodge.test");
    return w.fetch(r);
  };
  return { ...w, call };
}
