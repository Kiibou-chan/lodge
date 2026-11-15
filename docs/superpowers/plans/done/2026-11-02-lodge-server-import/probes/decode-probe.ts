import { readFileSync } from "node:fs";
import { decodeStored, encodeStored } from "./decode.ts";
const cases: string[] = JSON.parse(readFileSync(process.argv[2] as string, "utf8"));
const expected: number[][] = JSON.parse(readFileSync(process.argv[3] as string, "utf8"));
let differ = 0, roundtrip = 0, replaced = 0;
cases.forEach((hex, n) => {
  const bytes = Uint8Array.from(Buffer.from(hex, "hex"));
  const got = [...decodeStored(bytes)].map((c) => c.codePointAt(0) as number);
  if (JSON.stringify(got) !== JSON.stringify(expected[n])) differ++;
  if (Buffer.from(encodeStored(decodeStored(bytes))).toString("hex") !== hex) roundtrip++;
  if (new TextDecoder().decode(bytes) !== decodeStored(bytes)) replaced++;
});
console.log(`cases ${cases.length}; decodeStored differs from Python's surrogateescape on ${differ}; encodeStored fails to give the bytes back on ${roundtrip}; TextDecoder differs on ${replaced}`);
console.log(`TextDecoder of ff: U+${new TextDecoder().decode(Uint8Array.of(0xff)).codePointAt(0)?.toString(16)}`);
