import { expect, test } from "bun:test";
import { project } from "./project.ts";

test.each([["search", "x"], ["show", "d-aaaaaa"], ["id", "s"], ["check"]].map((c) => [c]))(
  "before_init_one_sentence_exit_2 %p",
  async (argv) => {
    const p = await project();
    const r = await p.run(...argv);
    expect(r).toEqual({
      code: 2,
      out: "",
      err: "lodge: lodge has no data in this repository yet; run `lodge init`\n",
    });
  },
);
