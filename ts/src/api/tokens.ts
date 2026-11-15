import { type AgentToken, PROJECT_NAME, stampOf } from "#app";
import { ApiError } from "./errors.ts";
import type { ApiOptions } from "./options.ts";

const ALPHABET = "0123456789abcdefghjkmnpqrstvwxyz";
export function hashSecret(secret: string): string {
  return new Bun.CryptoHasher("sha256").update(secret).digest("hex");
}
export function tokenId(entropy: Uint8Array): string {
  if (entropy.length < 6) throw new RangeError("an identifier needs at least six entropy bytes");
  return `t-${Array.from(entropy.slice(0, 6), (b) => ALPHABET[b % 32]).join("")}`;
}
export async function issueToken(
  options: ApiOptions,
  project: string,
  label: string,
  role: string | null,
): Promise<{ readonly token: AgentToken; readonly secret: string }> {
  if (!PROJECT_NAME.pattern.test(project))
    throw new ApiError("usage", "project must be a project name");
  if (role !== null && !PROJECT_NAME.pattern.test(role))
    throw new ApiError("usage", "role must be a project name");
  if (label.length < 1 || label.length > 80 || /[\p{Cc}\p{Zl}\p{Zp}]/u.test(label))
    throw new ApiError(
      "usage",
      "label must be 1 to 80 characters without control characters or line breaks",
    );
  const secret = `lodge_${Buffer.from(options.random(32)).toString("base64url")}`;
  const token: AgentToken = {
    id: tokenId(options.random(6)),
    project,
    label,
    role,
    issued: stampOf(options.clock.now()),
    revoked: null,
  };
  await options.accounts.issueToken(token, hashSecret(secret));
  return { token, secret };
}
