import { CliError } from "./errors.ts";
import type { ServerPlace } from "./settings.ts";
import { fromWire } from "./wire.ts";
export type Call = (operation: string, body: Readonly<Record<string, unknown>>) => Promise<unknown>;
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
    let answer: { error?: { kind: string; message: string }; result?: unknown };
    try {
      answer = (await response.json()) as typeof answer;
    } catch {
      throw new CliError(`${url} answered something other than JSON`);
    }
    if (response.status === 200 || answer.error?.kind === "check-failed")
      return fromWire(answer.result);
    if (answer.error?.kind === "no-project")
      throw new CliError("lodge has no data in this repository yet; run `lodge init`");
    if (answer.error?.kind === "unauthorised")
      throw new CliError(
        `${answer.error?.message ?? "the server returned an error"}; an agent token goes in LODGE_TOKEN, or in a cloud environment's network secret for this server`,
      );
    throw new CliError(
      answer.error?.message ?? "the server returned an error",
      answer.error?.kind === "conflict" ? 1 : 2,
    );
  };
}
