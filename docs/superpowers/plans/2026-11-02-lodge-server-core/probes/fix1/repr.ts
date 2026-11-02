const NP = /[\p{Cc}\p{Cf}\p{Cs}\p{Co}\p{Cn}\p{Zl}\p{Zp}\p{Zs}]/u;
function pyRepr(s: string): string {
  const q = s.includes("'") && !s.includes('"') ? '"' : "'";
  let out = q;
  for (const ch of s) {
    const cp = ch.codePointAt(0)!;
    if (ch === q || ch === "\\") out += "\\" + ch;
    else if (ch === "\t") out += "\\t"; else if (ch === "\n") out += "\\n"; else if (ch === "\r") out += "\\r";
    else if (ch !== " " && NP.test(ch)) out += cp < 0x100 ? "\\x" + cp.toString(16).padStart(2, "0") : cp < 0x10000 ? "\\u" + cp.toString(16).padStart(4, "0") : "\\U" + cp.toString(16).padStart(8, "0");
    else out += ch;
  }
  return out + q;
}
const d = JSON.parse(await Bun.file(process.argv[2]!).text());
let diff = 0; const ex: string[] = [];
for (const [k, v] of Object.entries(d)) {
  const s = k === "s1" ? "it's" : k === "s2" ? "both ' and \"" : k === "s3" ? "a\\b" : String.fromCodePoint(Number(k));
  if (pyRepr(s) !== v) { diff++; if (ex.length < 6) ex.push(`${k}:${v}/${pyRepr(s)}`); }
}
console.log("pyRepr differs from Python's repr at", diff, "of", Object.keys(d).length, "texts;", ex.join(" "));
