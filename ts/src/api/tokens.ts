import { type AgentToken, stampOf } from "#app";
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
