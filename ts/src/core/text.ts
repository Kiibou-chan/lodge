export const WORD_CLASS = "[\\p{L}\\p{N}_]";
export const PY_SPACE_CLASS =
  "[\\u{9}-\\u{d}\\u{1c}-\\u{1f}\\u{20}\\u{85}\\u{a0}\\u{1680}\\u{2000}-\\u{200a}\\u{2028}\\u{2029}\\u{202f}\\u{205f}\\u{3000}]";
export function isPySpace(ch: string): boolean {
  const cp = ch.codePointAt(0);
  return (
    cp !== undefined &&
    ((cp >= 9 && cp <= 13) ||
      (cp >= 28 && cp <= 32) ||
      cp === 133 ||
      cp === 160 ||
      cp === 5760 ||
      (cp >= 8192 && cp <= 8202) ||
      [8232, 8233, 8239, 8287, 12288].includes(cp))
  );
}
export function strip(s: string): string {
  return s.replace(new RegExp(`^${PY_SPACE_CLASS}+|${PY_SPACE_CLASS}+$`, "gu"), "");
}
export function rstrip(s: string): string {
  return s.replace(new RegExp(`${PY_SPACE_CLASS}+$`, "u"), "");
}
export function splitWords(s: string): string[] {
  const clean = strip(s);
  return clean ? clean.split(new RegExp(`${PY_SPACE_CLASS}+`, "u")) : [];
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
    if (cp !== undefined && [10, 11, 12, 13, 28, 29, 30, 133, 8232, 8233].includes(cp)) {
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
