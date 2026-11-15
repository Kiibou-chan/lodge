import { CliError } from "./errors.ts";
import type { ServerPlace } from "./settings.ts";
import { fromWire } from "./wire.ts";
export type Call = (operation: string, body: Readonly<Record<string, unknown>>) => Promise<unknown>;
function object(value: unknown): value is Record<string, unknown> {
  return value !== null && typeof value === "object" && !Array.isArray(value);
}
export function client(
  place: ServerPlace,
  token: string | null,
  io: { readonly fetch: (request: Request) => Promise<Response>; readonly version: string },
): Call {
  const { url, project } = place;
  return async (operation, body) => {
    const request = new Request(`${url}/api/v1/${operation}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...(token === null ? {} : { Authorization: `Bearer ${token}` }),
      },
      body: JSON.stringify({ project, ...body }),
    });
    let response: Response;
    try {
      response = await io.fetch(request);
    } catch (error) {
      throw new CliError(
        `cannot reach ${url}: ${error instanceof Error ? error.message : String(error)}`.replace(
          /[\r\n]+/gu,
          " ",
        ),
      );
    }
    const theirs = response.headers.get("Lodge-Version");
    if (theirs === null) throw new CliError(`${url} does not answer as a lodge server`);
    if (theirs !== io.version)
      throw new CliError(
        `the server at ${url} runs lodge ${theirs} and this command is lodge ${io.version}; use the same version`,
      );
    let answer: unknown;
    try {
      answer = await response.json();
    } catch {
      throw new CliError(`${url} answered something other than JSON`);
    }
    const malformed = () => new CliError(`${url} answered something other than a lodge answer`);
    if (!object(answer)) throw malformed();
    if (response.status === 200) {
      if (!Object.hasOwn(answer, "result")) throw malformed();
      return fromWire(answer["result"]);
    }
    const error = answer["error"];
    if (!object(error) || typeof error["kind"] !== "string" || typeof error["message"] !== "string")
      throw malformed();
    if (error["kind"] === "check-failed") {
      if (!Object.hasOwn(answer, "result")) throw malformed();
      return fromWire(answer["result"]);
    }
    if (error["kind"] === "no-project")
      throw new CliError("lodge has no data in this repository yet; run `lodge init`");
    if (error["kind"] === "unauthorised")
      throw new CliError(
        `${error["message"]}; an agent token goes in LODGE_TOKEN, or in a cloud environment's network secret for this server`,
      );
    throw new CliError(error["message"], error["kind"] === "conflict" ? 1 : 2);
  };
}
