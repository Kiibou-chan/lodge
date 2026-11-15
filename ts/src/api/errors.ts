import { Conflict, Forbidden, LodgeError, NotFound } from "#app";
export const statuses = {
  usage: 400,
  unauthorised: 401,
  forbidden: 403,
  "not-found": 404,
  "no-project": 404,
  conflict: 409,
  "check-failed": 422,
  internal: 500,
} as const;
export class ApiError extends Error {
  constructor(
    readonly kind: keyof typeof statuses,
    message: string,
  ) {
    super(message);
  }
}
export function mappedError(error: unknown, log: (text: string) => void): ApiError {
  if (error instanceof ApiError) return error;
  for (const [type, kind] of [
    [Conflict, "conflict"],
    [NotFound, "not-found"],
    [Forbidden, "forbidden"],
    [LodgeError, "usage"],
  ] as const) {
    if (error instanceof type) return new ApiError(kind, error.message);
  }
  log(error instanceof Error ? (error.stack ?? error.message) : "unexpected server error");
  return new ApiError("internal", "the server failed; see its log");
}
