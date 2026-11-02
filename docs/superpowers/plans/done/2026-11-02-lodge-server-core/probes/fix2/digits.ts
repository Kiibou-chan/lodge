const dec = new Set((await Bun.file(process.argv[2]!).text()).split(" ").map(Number));
const nd: number[] = [];
for (let c = 0; c < 0x110000; c++) if (/\p{Nd}/u.test(String.fromCodePoint(c))) nd.push(c);
const extra = nd.filter((c) => !dec.has(c));
const missing = [...dec].filter((c) => !/\p{Nd}/u.test(String.fromCodePoint(c)));
const blocks = new Map<number, number>();
for (const c of extra) blocks.set(c & ~0xf, (blocks.get(c & ~0xf) ?? 0) + 1);
console.log(`\\p{Nd} ${nd.length}, more than isdecimal ${extra.length}, isdecimal not \\p{Nd} ${missing.length}`);
console.log("first extra:", extra.slice(0, 3).map((c) => c.toString(16)).join(" "), "unicode of bun:", process.versions.unicode ?? "n/a");
