import { AddOutcome } from "#app";
import { isObject } from "./args.ts";
import { authenticate } from "./auth.ts";
import { ApiError, mappedError, statuses } from "./errors.ts";
import { operate, operationArgs } from "./operations.ts";
import { type ApiOptions, MAX_REQUEST_BODY_SIZE } from "./options.ts";
import { PAGE, SCRIPT } from "./page.ts";
import { passkeys, publicOperations } from "./passkeys.ts";
import { isPersonOperation, personOperation } from "./person.ts";
import { sessionSecret } from "./session.ts";
import { toWire } from "./wire.ts";

const policies = {
  "Cache-Control": "no-store",
  "X-Content-Type-Options": "nosniff",
  "Referrer-Policy": "no-referrer",
  "Content-Security-Policy":
    "default-src 'none'; script-src 'self'; connect-src 'self'; base-uri 'none'; form-action 'none'; frame-ancestors 'none'",
};
export function handler(options: ApiOptions): (request: Request) => Promise<Response> {
  const ceremony = passkeys(options);
  const answer = (body: unknown, status = 200) =>
    new Response(JSON.stringify(body), {
      status,
      headers: {
        "Content-Type": "application/json; charset=utf-8",
        ...policies,
        "Lodge-Version": options.version,
      },
    });
  return async (request) => {
    try {
      const path = new URL(request.url).pathname;
      if (request.method === "GET" && (path === "/" || path === "/page.js"))
        return new Response(path === "/" ? PAGE : SCRIPT, {
          headers: {
            "Content-Type":
              path === "/" ? "text/html; charset=utf-8" : "text/javascript; charset=utf-8",
            ...policies,
          },
        });
      if (!path.startsWith("/api/v1/")) throw new ApiError("not-found", "nothing here");
      if (request.method !== "POST") throw new ApiError("usage", "use POST");
      if (
        request.headers.get("Content-Type")?.split(";")[0]?.trim().toLowerCase() !==
        "application/json"
      )
        throw new ApiError("usage", "send JSON");
      const operation = path.slice("/api/v1/".length);
      if (
        !publicOperations.includes(operation) &&
        !request.headers.has("Authorization") &&
        sessionSecret(request) === null
      )
        throw new ApiError("unauthorised", "sign in, or send an agent token");
      if (Number(request.headers.get("Content-Length")) > MAX_REQUEST_BODY_SIZE)
        throw new ApiError("usage", "the body exceeds 8 MiB");
      let body: unknown;
      try {
        body = await request.json();
      } catch {
        throw new ApiError("usage", "the body is not JSON");
      }
      if (!isObject(body)) throw new ApiError("usage", "the body is not a JSON object");
      if (publicOperations.includes(operation)) {
        const result = await ceremony(operation, body, request);
        const response = answer({ result: toWire(result.result) });
        if (result.cookie) response.headers.set("Set-Cookie", result.cookie);
        return response;
      }
      if (isPersonOperation(operation)) {
        const actor = await authenticate(options, request, null);
        const { result, checkFailed } = await personOperation(options, operation, body, actor);
        if (checkFailed)
          return answer(
            {
              error: { kind: "check-failed", message: "the check failed" },
              result: toWire(result),
            },
            422,
          );
        return answer({ result: toWire(result) });
      }
      const args = operationArgs(operation, body);
      const project = args.string("project");
      const actor = await authenticate(options, request, project);
      const result = await operate(options, args, project, actor);
      if (
        ["add", "ask", "reply", "close"].includes(operation) &&
        isObject(result) &&
        result["outcome"] === AddOutcome.CHECK_FAILED
      )
        return answer(
          { error: { kind: "check-failed", message: "the check failed" }, result: toWire(result) },
          422,
        );
      return answer({ result: toWire(result) });
    } catch (error) {
      const mapped = mappedError(error, options.log);
      return answer(
        { error: { kind: mapped.kind, message: mapped.message } },
        statuses[mapped.kind],
      );
    }
  };
}
