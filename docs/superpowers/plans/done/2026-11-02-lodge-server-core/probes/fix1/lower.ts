const d = JSON.parse(await Bun.file(process.argv[2]!).text());
let diff = 0; const ex: string[] = [];
for (let cp = 0; cp < 0x110000; cp++) { if (cp >= 0xd800 && cp <= 0xdfff) continue; const c = String.fromCodePoint(cp); const py = d[cp] ?? c; if (c.toLowerCase() !== py) { diff++; if (ex.length < 5) ex.push(cp.toString(16)); } }
console.log("lower differs from toLowerCase at", diff, "code points, e.g.", ex.join(" "), "; final sigma:", JSON.stringify(d.sigma), JSON.stringify("ΑΣ ΑΣΑ Σ".toLowerCase()));
