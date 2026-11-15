import { expect, test } from "bun:test";
import { contentHash, decodeUtf8, encodeUtf8, ValueError } from "#core";

const cases = [
  ["efbbbf61", [0xfeff, 97]],
  ["80ff", [0xdc80, 0xdcff]],
  ["c0af", [0xdcc0, 0xdcaf]],
  ["e282", [0xdce2, 0xdc82]],
  ["eda080", [0xdced, 0xdca0, 0xdc80]],
  ["f09f9880", [0x1f600]],
  ["f4908080", [0xdcf4, 0xdc90, 0xdc80, 0xdc80]],
  ["61e282ac62", [97, 0x20ac, 98]],
  ["e2c2a9", [0xdce2, 0xa9]],
  ["e28241", [0xdce2, 0xdc82, 65]],
  ["f09f41", [0xdcf0, 0xdc9f, 65]],
] as const;
test.each(cases.map((c) => [c] as const))(
  "decode_utf8_like_surrogateescape %p",
  ([hex, points]) => {
    expect(Array.from(decodeUtf8(Buffer.from(hex, "hex")), (c) => c.codePointAt(0))).toEqual([
      ...points,
    ]);
  },
);
test.each(cases.map((c) => [c] as const))("encode_utf8_reverses_decode %p", ([hex]) => {
  const bytes = new Uint8Array(Buffer.from(hex, "hex"));
  expect(encodeUtf8(decodeUtf8(bytes))).toEqual(bytes);
});
test.each([["\ud83d"], ["\udc7f"]])(
  "encode_refuses_a_lone_surrogate_outside_the_escapes %p",
  (text) => {
    expect(() => encodeUtf8(text)).toThrow(ValueError);
    expect(() => contentHash(text)).toThrow(ValueError);
  },
);
test("content_hash_encodes_escaped_bytes", () => {
  expect(contentHash("a\udc80\n")).toBe("518254327818");
});
