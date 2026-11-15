// A surrogateescape decoder: each byte of an invalid UTF-8 sequence becomes U+DC00 + b.
export function decodeStored(bytes: Uint8Array): string {
  let out = "";
  let i = 0;
  while (i < bytes.length) {
    const b = bytes[i] as number;
    const need = b < 0x80 ? 0 : b >= 0xc2 && b <= 0xdf ? 1 : b >= 0xe0 && b <= 0xef ? 2 : b >= 0xf0 && b <= 0xf4 ? 3 : -1;
    if (need === 0) { out += String.fromCharCode(b); i += 1; continue; }
    let ok = need > 0;
    if (ok) {
      const lo = b === 0xe0 ? 0xa0 : b === 0xed ? 0x80 : b === 0xf0 ? 0x90 : 0x80;
      const hi = b === 0xe0 ? 0xbf : b === 0xed ? 0x9f : b === 0xf4 ? 0x8f : 0xbf;
      let cp = need === 1 ? b & 0x1f : need === 2 ? b & 0x0f : b & 0x07;
      for (let k = 1; k <= need; k++) {
        const c = bytes[i + k];
        if (c === undefined || c < (k === 1 ? lo : 0x80) || c > (k === 1 ? hi : 0xbf)) { ok = false; break; }
        cp = (cp << 6) | (c & 0x3f);
      }
      if (ok) { out += String.fromCodePoint(cp); i += need + 1; continue; }
    }
    out += String.fromCharCode(0xdc00 + b);
    i += 1;
  }
  return out;
}
export function encodeStored(text: string): Uint8Array {
  const parts: number[] = [];
  for (const ch of text) {
    const cp = ch.codePointAt(0) as number;
    if (cp >= 0xdc80 && cp <= 0xdcff) parts.push(cp - 0xdc00);
    else parts.push(...new TextEncoder().encode(ch));
  }
  return Uint8Array.from(parts);
}
