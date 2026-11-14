import type { Now } from "./ports.ts";

function localParts(now: Now): readonly [string, string, string] {
  const date = new Date(now.epochMs + now.offsetMinutes * 60_000);
  const pad = (n: number) => String(n).padStart(2, "0");
  return [
    `${String(date.getUTCFullYear()).padStart(4, "0")}-${pad(date.getUTCMonth() + 1)}-${pad(date.getUTCDate())}`,
    `${pad(date.getUTCHours())}:${pad(date.getUTCMinutes())}`,
    pad(date.getUTCSeconds()),
  ];
}
export function stampOf(now: Now): string {
  const [day, minute, second] = localParts(now);
  const offset = Math.abs(now.offsetMinutes);
  return `${day}T${minute}:${second}${now.offsetMinutes < 0 ? "-" : "+"}${String(Math.floor(offset / 60)).padStart(2, "0")}:${String(offset % 60).padStart(2, "0")}`;
}
export function minuteOf(now: Now): string {
  const [day, minute] = localParts(now);
  return `${day} ${minute}`;
}
