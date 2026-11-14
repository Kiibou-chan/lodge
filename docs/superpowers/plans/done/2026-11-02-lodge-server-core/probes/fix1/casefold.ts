// bun casefold.ts PY_JSON, where PY_JSON holds Python's casefold of every code point that changes ("cf"), the code points where isdigit() holds and isdecimal() does not ("dig"), and those where isdecimal() holds ("isdecimal").
// The JSON comes from `uv run --frozen python`: {"ver", "uni", "cf": {cp: s.casefold()} where it changes, "dig": [cp where isdigit() and not isdecimal()], "isdecimal": [cp where isdecimal()]}.
const d = JSON.parse(await Bun.file(process.argv[2] ?? "").text());
console.log("python", d.ver, "unicode", d.uni);
let diff = 0;
let hits = 0;
for (let cp = 0; cp < 0x110000; cp++) {
  if (cp >= 0xd800 && cp <= 0xdfff) continue;
  const c = String.fromCodePoint(cp);
  const py = d.cf[cp] ?? c;
  const js = c.toUpperCase().toLowerCase();
  if (py !== js) {
    diff++;
    if (/[authorAUTHOR]/.test(py) || /[author]/.test(js)) hits++;
  }
}
console.log("casefold differs from toUpperCase().toLowerCase() at", diff, "code points; of them yielding a letter of 'author'", hits);
const r: string[] = [];
let s = -1;
let p = -2;
for (const c of d.dig as number[]) {
  if (c !== p + 1) {
    if (s >= 0) r.push(s === p ? s.toString(16) : `${s.toString(16)}-${p.toString(16)}`);
    s = c;
  }
  p = c;
}
r.push(s === p ? s.toString(16) : `${s.toString(16)}-${p.toString(16)}`);
console.log("isdigit and not isdecimal:", (d.dig as number[]).length, "code points in", r.length, "ranges:", r.join(" "));
const nd = new Set<number>();
for (let cp = 0; cp < 0x110000; cp++) if (/\p{Nd}/u.test(String.fromCodePoint(cp))) nd.add(cp);
const pyDecimal = new Set<number>(d.isdecimal);
let onlyPy = 0;
let onlyJs = 0;
for (const c of pyDecimal) if (!nd.has(c)) onlyPy++;
for (const c of nd) if (!pyDecimal.has(c)) onlyJs++;
console.log("isdecimal vs \\p{Nd}: python only", onlyPy, "js only", onlyJs);
