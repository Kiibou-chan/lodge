import { parseAllDocuments, parseDocument } from "yaml";
const cases: [string, string][] = [
  ["scalars", "key: yes\nb: 14:14\nc: 0x10\nd: ~\n"],
  ["empty", "key:\n"],
  ["tag int", "key: !!int 5\n"],
  ["tag python", "key: !!python/name:os.system\n"],
  ["bad line", "a: b\nc: d: e\n"],
  ["dup", "title: a\nscope: b\ntitle: c\n"],
  ["ctrl", "a: b\nc: \x01\n"],
  ["two docs", "a: b\n---\nc: d\n"],
  ["deep", "a: " + "[".repeat(5000) + "]".repeat(5000)],
  ["pair", 'a: "Ship it \\ud83d\\ude00"'],
  ["lone", 'a: "\\ud83d"'],
];
for (const [name, text] of cases) {
  try {
    const docs = parseAllDocuments(text, { schema: "failsafe", uniqueKeys: true, prettyErrors: true });
    const arr = Array.isArray(docs) ? docs : [docs];
    const d = arr[0]!;
    const errs = arr.flatMap((x) => x.errors).map((e) => `${e.code} line ${e.linePos?.[0].line}: ${e.message.split("\n")[0]}`);
    const warns = arr.flatMap((x) => x.warnings).map((e) => `${e.code}: ${e.message.split("\n")[0]}`);
    console.log(name, "docs", arr.length, JSON.stringify(d.toJS()), errs, warns);
  } catch (e) { console.log(name, "THROW", (e as Error).message.slice(0, 80)); }
}
