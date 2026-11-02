import { ValueError } from "./errors.ts";

const ALPHABET = "0123456789abcdefghjkmnpqrstvwxyz";
export function isId(text: string): boolean {
  return /^[dsq]-[0123456789abcdefghjkmnpqrstvwxyz]{6}$/u.test(text);
}
export function mintId(prefix: "d" | "s" | "q", entropy: Uint8Array): string {
  if (entropy.length < 6)
    throw new ValueError(`an identifier needs at least six entropy bytes, got ${entropy.length}`);
  return `${prefix}-${Array.from(entropy.slice(0, 6), (b) => ALPHABET[b % 32]).join("")}`;
}
