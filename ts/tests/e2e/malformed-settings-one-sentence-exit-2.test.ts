import { expect, test } from "bun:test";
import { project } from "./project.ts";

test.each([
  ["[store\n", "lodge: .lodge.toml: "],
  ["[nonsense]\n", "lodge: .lodge.toml: unknown section [nonsense]"],
  ['[store]\nmode = "tree"\n', "lodge: .lodge.toml: unknown section [store]"],
  [
    "[length]\ntitle_chars = 80.0\n",
    "lodge: .lodge.toml: length.title_chars must be a positive whole number",
  ],
])("malformed_settings_one_sentence_exit_2 %p %p", async (text, start) => {
  const p = await project();
  p.configure(text);
  for (const argv of [["init"], ["search", "x"]]) {
    const r = await p.run(...argv);
    expect([r.code, r.out]).toEqual([2, ""]);
    expect(r.err.startsWith(start)).toBe(true);
    expect(r.err.split("\n")).toHaveLength(2);
  }
});
test("settings_are_not_needed_for_the_guide", async () => {
  const p = await project();
  p.configure("[store\n");
  expect((await p.run("guide")).code).toBe(0);
});
