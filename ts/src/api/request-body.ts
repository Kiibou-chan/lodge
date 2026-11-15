import { ApiError } from "./errors.ts";
import { MAX_REQUEST_BODY_SIZE } from "./options.ts";

export class BodyTooLarge extends ApiError {
  constructor() {
    super("usage", "the body exceeds 8 MiB");
  }
}

export async function requestBody(request: Request): Promise<unknown> {
  if (Number(request.headers.get("Content-Length")) > MAX_REQUEST_BODY_SIZE) {
    await request.body?.cancel();
    throw new BodyTooLarge();
  }
  const reader = request.body?.getReader();
  const bytes = new Uint8Array(MAX_REQUEST_BODY_SIZE);
  let size = 0;
  if (reader) {
    try {
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        if (size + value.byteLength > MAX_REQUEST_BODY_SIZE) {
          await reader.cancel();
          throw new BodyTooLarge();
        }
        bytes.set(value, size);
        size += value.byteLength;
      }
    } catch (error) {
      if (error instanceof BodyTooLarge) throw error;
      throw new ApiError("usage", "the body is not JSON");
    } finally {
      reader.releaseLock();
    }
  }
  try {
    return JSON.parse(new TextDecoder().decode(bytes.subarray(0, size)));
  } catch {
    throw new ApiError("usage", "the body is not JSON");
  }
}
