import { readFileSync } from "node:fs";
import { CliError } from "./errors.ts";

export function readExact(path: string, notUtf8: string): string {
  let bytes: Uint8Array;
  try {
    bytes = readFileSync(path);
  } catch (error) {
    const message = error instanceof Error ? error.message : String(error);
    const code = error !== null && typeof error === "object" && "code" in error ? error.code : null;
    const descriptions: Record<string, string> = {
      EISDIR: "Is a directory",
      ENOENT: "No such file or directory",
      EACCES: "Permission denied",
      EPERM: "Operation not permitted",
    };
    const description =
      (typeof code === "string" ? descriptions[code] : undefined) ??
      message.split(",")[0]?.replace(/^[A-Z]+: /u, "") ??
      message;
    const reason = description.charAt(0).toUpperCase() + description.slice(1);
    throw new CliError(`${path}: cannot be read: ${reason.replace(/[\r\n]+/gu, " ")}`);
  }
  try {
    return new TextDecoder("utf-8", { fatal: true, ignoreBOM: true }).decode(bytes);
  } catch {
    throw new CliError(`${path}: ${notUtf8}`);
  }
}
export function readDraft(path: string): string {
  return readExact(path, "not UTF-8 text").replace(/\r\n?/gu, "\n");
}
