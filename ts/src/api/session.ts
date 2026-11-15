import { type Actor, person, stampOf } from "#app";
import { ApiError } from "./errors.ts";
import type { ApiOptions } from "./options.ts";
import { hashSecret } from "./tokens.ts";

const AGE = 2592000;
const attributes = "; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=";
export function sessionSecret(request: Request): string | null {
  return /(?:^|;\s*)lodge_session=([^;]*)/u.exec(request.headers.get("Cookie") ?? "")?.[1] ?? null;
}
export async function sessionActor(options: ApiOptions, request: Request): Promise<Actor> {
  const setup = await options.accounts.setup();
  if (!setup) throw new ApiError("unauthorised", "sign in again");
  if (request.headers.get("Origin") !== setup.origin)
    throw new ApiError("forbidden", "the request does not come from this server's page");
  const secret = sessionSecret(request);
  const expires = secret === null ? null : await options.accounts.sessionExpiry(hashSecret(secret));
  if (expires === null || Date.parse(expires) <= options.clock.now().epochMs)
    throw new ApiError("unauthorised", "sign in again");
  return person(setup.person);
}
export async function startSession(options: ApiOptions): Promise<string> {
  const secret = Buffer.from(options.random(32)).toString("base64url");
  await options.accounts.startSession(
    hashSecret(secret),
    stampOf({ ...options.clock.now(), epochMs: options.clock.now().epochMs + AGE * 1000 }),
  );
  return `lodge_session=${secret}${attributes}${AGE}`;
}
export async function endSession(options: ApiOptions, request: Request): Promise<string> {
  await options.accounts.endSession(hashSecret(sessionSecret(request) ?? ""));
  return `lodge_session=${attributes}0`;
}
