import { expect, test } from "bun:test";
import { mkdirSync } from "node:fs";
import { join } from "node:path";
import { project } from "./project.ts";

test.each([["init"], ["search", "x"], ["id", "d"], ["check"], ["waiting"]].map((c) => [c]))(
  "outside_repository_one_sentence_exit_2 %p",
  async (argv) => {
    const p = await project();
    const plain = join(p.root, "..", "plain");
    mkdirSync(plain);
    expect(await p.runIn(plain, ...argv)).toEqual({
      code: 2,
      out: "",
      err: `lodge: ${plain} is not inside a git repository\n`,
    });
  },
);
