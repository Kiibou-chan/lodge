import { ValueError } from "./errors.ts";

export const WORD_CLASS = "[\\p{L}\\p{N}_]";
export const PY_SPACE_CLASS =
  "[\\u{9}-\\u{d}\\u{1c}-\\u{1f}\\u{20}\\u{85}\\u{a0}\\u{1680}\\u{2000}-\\u{200a}\\u{2028}\\u{2029}\\u{202f}\\u{205f}\\u{3000}]";
const SPACE = new RegExp(PY_SPACE_CLASS, "u");
const EDGES = new RegExp(`^${PY_SPACE_CLASS}+|${PY_SPACE_CLASS}+$`, "gu");
const TRAILING = new RegExp(`${PY_SPACE_CLASS}+$`, "u");
const RUN = new RegExp(`${PY_SPACE_CLASS}+`, "u");
const LINE_BREAKS: ReadonlySet<number> = new Set([10, 11, 12, 13, 28, 29, 30, 133, 8232, 8233]);
export function isPySpace(ch: string): boolean {
  const cp = ch.codePointAt(0);
  return cp !== undefined && SPACE.test(String.fromCodePoint(cp));
}
export function strip(s: string): string {
  return s.replace(EDGES, "");
}
export function rstrip(s: string): string {
  return s.replace(TRAILING, "");
}
export function splitWords(s: string): string[] {
  const clean = strip(s);
  return clean ? clean.split(RUN) : [];
}
export function splitLines(s: string): string[] {
  const result: string[] = [];
  let line = "",
    afterCr = false;
  for (const ch of s) {
    if (ch === "\n" && afterCr) {
      afterCr = false;
      continue;
    }
    const cp = ch.codePointAt(0);
    if (cp !== undefined && LINE_BREAKS.has(cp)) {
      result.push(line);
      line = "";
    } else line += ch;
    afterCr = ch === "\r";
  }
  if (line) result.push(line);
  return result;
}
const DIGIT_RANGES = [
  [0xb2, 0xb3],
  [0xb9, 0xb9],
  [0x1369, 0x1371],
  [0x19da, 0x19da],
  [0x2070, 0x2070],
  [0x2074, 0x2079],
  [0x2080, 0x2089],
  [0x2460, 0x2468],
  [0x2474, 0x247c],
  [0x2488, 0x2490],
  [0x24ea, 0x24ea],
  [0x24f5, 0x24fd],
  [0x24ff, 0x24ff],
  [0x2776, 0x277e],
  [0x2780, 0x2788],
  [0x278a, 0x2792],
  [0x10a40, 0x10a43],
  [0x10e60, 0x10e68],
  [0x11052, 0x1105a],
  [0x1f100, 0x1f10a],
] as const;
export function isDigit(s: string): boolean {
  return (
    s !== "" &&
    Array.from(s).every((ch) => {
      const cp = ch.codePointAt(0) as number;
      return /\p{Nd}/u.test(ch) || DIGIT_RANGES.some(([lo, hi]) => cp >= lo && cp <= hi);
    })
  );
}
export function casefold(s: string): string {
  return s.toUpperCase().toLowerCase().replaceAll("ς", "σ");
}
export function pyRepr(s: string): string {
  const quote = s.includes("'") && !s.includes('"') ? '"' : "'";
  let out = quote;
  for (const ch of s) {
    if (ch === "\\" || ch === quote) out += `\\${ch}`;
    else if (ch === "\t") out += "\\t";
    else if (ch === "\n") out += "\\n";
    else if (ch === "\r") out += "\\r";
    else if (ch !== " " && /[\p{Cc}\p{Cf}\p{Cs}\p{Co}\p{Cn}\p{Zl}\p{Zp}\p{Zs}]/u.test(ch)) {
      const cp = ch.codePointAt(0) as number;
      out += `\\${cp < 256 ? "x" : cp < 65536 ? "u" : "U"}${cp.toString(16).padStart(cp < 256 ? 2 : cp < 65536 ? 4 : 8, "0")}`;
    } else out += ch;
  }
  return out + quote;
}
export function codePointLength(s: string): number {
  return Array.from(s).length;
}
export function byCodePoint(a: string, b: string): number {
  const aa = Array.from(a, (ch) => ch.codePointAt(0) as number),
    bb = Array.from(b, (ch) => ch.codePointAt(0) as number);
  for (let i = 0; i < Math.min(aa.length, bb.length); i++) {
    const d = (aa[i] as number) - (bb[i] as number);
    if (d) return d;
  }
  return aa.length - bb.length;
}

export function encodeUtf8(text: string): Uint8Array {
  const bytes: number[] = [];
  const encoder = new TextEncoder();
  for (const ch of text) {
    const cp = ch.codePointAt(0) as number;
    if (cp >= 0xdc80 && cp <= 0xdcff) bytes.push(cp - 0xdc00);
    else if (cp >= 0xd800 && cp <= 0xdfff)
      throw new ValueError(`cannot encode lone surrogate ${pyRepr(ch)}`);
    else bytes.push(...encoder.encode(ch));
  }
  return new Uint8Array(bytes);
}
const UTF8_MASKS = [127, 127, 31, 15, 7] as const;
const UTF8_MINIMA = [0, 0, 0x80, 0x800, 0x10000] as const;
export function decodeUtf8(bytes: Uint8Array): string {
  let text = "";
  for (let i = 0; i < bytes.length; ) {
    const first = bytes[i] as number;
    const size =
      first < 0x80
        ? 1
        : first >= 0xc2 && first <= 0xdf
          ? 2
          : first >= 0xe0 && first <= 0xef
            ? 3
            : first >= 0xf0 && first <= 0xf4
              ? 4
              : 0;
    let cp = first & UTF8_MASKS[size];
    let valid = size > 0 && i + size <= bytes.length;
    for (let j = 1; valid && j < size; j++) {
      const next = bytes[i + j] as number;
      valid = next >= 0x80 && next <= 0xbf;
      cp = (cp << 6) | (next & 63);
    }
    valid = valid && cp >= UTF8_MINIMA[size] && cp <= 0x10ffff && !(cp >= 0xd800 && cp <= 0xdfff);
    text += String.fromCodePoint(valid ? cp : 0xdc00 + first);
    i += valid ? size : 1;
  }
  return text;
}
