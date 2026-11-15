import { parse } from "smol-toml";
const cases = [
  "[length]\ntitle_chars = 80.0\n",
  "[length]\ntitle_chars = 8e1\n",
  "[length]\ntitle_chars = 80\n",
  "length = {title_chars = 80.0}\n",
  "length.title_chars = 80.0\n",
  "[length]\ntitle_chars = 0x50\n",
  "[length]\ntitle_chars = 99999999999999999999\n",
  "[length]\ntitle_chars = inf\n",
  "[store\n",
];
const show = (v: unknown) =>
  typeof v === "string"
    ? v
    : JSON.stringify(v, (_k, x) =>
        typeof x === "bigint" ? `${x}n` : typeof x === "number" ? `number ${x}` : x,
      );
for (const c of cases) {
  const out = [Bun.TOML.parse, (t: string) => parse(t, { integersAsBigInt: true })].map((f) => {
    try {
      return show(f(c));
    } catch (e) {
      return `error: ${(e as Error).message.split("\n")[0]}`;
    }
  });
  console.log(`${JSON.stringify(c)} | Bun.TOML ${out[0]} | smol-toml ${out[1]}`);
}
