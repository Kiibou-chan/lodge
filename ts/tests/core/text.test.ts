import { expect, test } from "bun:test";
import {
  byCodePoint,
  casefold,
  codePointLength,
  isDigit,
  isPySpace,
  PY_SPACE_CLASS,
  pyRepr,
  rstrip,
  splitLines,
  splitWords,
  strip,
  WORD_CLASS,
} from "#core";

const spaces = [
  9,
  10,
  11,
  12,
  13,
  28,
  29,
  30,
  31,
  32,
  133,
  160,
  5760,
  ...Array.from({ length: 11 }, (_, i) => 8192 + i),
  8232,
  8233,
  8239,
  8287,
  12288,
];
test("is_py_space_matches_python", () => {
  for (const cp of spaces) expect(isPySpace(String.fromCodePoint(cp))).toBe(true);
  for (const ch of ["\uFEFF", "\u200B", "a"]) expect(isPySpace(ch)).toBe(false);
});
test("strip_removes_python_whitespace_only", () => {
  expect(strip("\x1c a \x85")).toBe("a");
  expect(strip("\uFEFFa")).toBe("\uFEFFa");
});
test("rstrip_like_python", () => {
  expect(rstrip("a \x85")).toBe("a");
  expect(rstrip("a\uFEFF")).toBe("a\uFEFF");
  expect(rstrip("## Reasoning\x1c")).toBe("## Reasoning");
});
test("split_words_like_python", () => expect(splitWords(" a\x1fb  c ")).toEqual(["a", "b", "c"]));
test("split_lines_like_python", () =>
  expect(splitLines("a\r\nb\x0bc\x1cd\u2028e\n")).toEqual(["a", "b", "c", "d", "e"]));
test("is_digit_like_python", () => {
  for (const s of ["12", "²", "①"]) expect(isDigit(s)).toBe(true);
  for (const s of ["", "1a", "½"]) expect(isDigit(s)).toBe(false);
});
test("casefold_like_python", () => {
  for (const [s, want] of [
    ["Straße", "strasse"],
    ["ſ", "s"],
    ["ﬆ", "st"],
    ["ΑΣ", "ασ"],
  ])
    expect(casefold(s as string)).toBe(want as string);
});
test("py_repr_matches_python", () => {
  for (const [s, want] of [
    ["a", "'a'"],
    ["it's", '"it\'s"'],
    ["both ' and \"", "'both \\' and \"'"],
    ["a\\b", "'a\\\\b'"],
    ["\x01", "'\\x01'"],
    ["\x85", "'\\x85'"],
    ["\u200b", "'\\u200b'"],
    ["\ud83d", "'\\ud83d'"],
    ["\t\n", "'\\t\\n'"],
    ["😀", "'😀'"],
  ])
    expect(pyRepr(s as string)).toBe(want as string);
});
test("code_point_length_counts_astral_once", () => expect(codePointLength("a😀")).toBe(2));
test("word_class_matches_python_w", () => {
  const re = new RegExp(`^${WORD_CLASS}$`, "u");
  for (const s of ["a", "é", "٣", "_"]) expect(re.test(s)).toBe(true);
  for (const s of ["-", " "]) expect(re.test(s)).toBe(false);
});
test("py_space_class_matches_is_py_space", () => {
  const re = new RegExp(PY_SPACE_CLASS, "u");
  for (let cp = 0; cp <= 0x10ffff; cp++) {
    const s = String.fromCodePoint(cp);
    if (re.test(s) !== isPySpace(s)) throw new Error(`space mismatch ${cp}`);
  }
});
test("by_code_point_orders_astral_after_bmp", () =>
  expect(byCodePoint("\uFFFF", "😀")).toBeLessThan(0));
