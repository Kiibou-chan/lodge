import { type Actor, agent } from "#app";
import { ApiError } from "./errors.ts";
import type { ApiOptions } from "./options.ts";
import { sessionActor } from "./session.ts";
import { hashSecret } from "./tokens.ts";
export async function authenticate(
  options: ApiOptions,
  request: Request,
  project: string | null,
): Promise<Actor> {
  const header = request.headers.get("Authorization");
  if (header === null) {
    if (!request.headers.has("Cookie"))
      throw new ApiError("unauthorised", "sign in, or send an agent token");
    return sessionActor(options, request);
  }
  const match = /^Bearer (\S+)$/u.exec(header);
  const token = match ? await options.accounts.tokenFor(hashSecret(match[1] ?? "")) : null;
  if (!token || token.revoked !== null)
    throw new ApiError("unauthorised", "the agent token is not known or was revoked");
  if (project !== null && token.project !== project)
    throw new ApiError("forbidden", `this agent token is for project ${token.project}`);
  return agent(token.role);
}
