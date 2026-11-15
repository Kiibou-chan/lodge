import { AddOutcome, type ThreadList, type ThreadShown, type Written } from "#app";
import type { Call } from "./client.ts";
import { readExact } from "./files.ts";
import type { ThreadCommand } from "./grammar.ts";
import { checkLines, heldLine, readLines } from "./output.ts";
import { threadHead, threadText } from "./thread-output.ts";
export async function runThread(
  command: ThreadCommand,
  call: Call,
  out: (text: string) => void,
): Promise<number> {
  if (command.kind === "threads") {
    const listed = (await call("threads", {})) as ThreadList;
    const heads = listed.items.map((t) => threadHead(t, listed.titles.get(t.about)));
    out(`${[...readLines(listed.read), heads.join("\n\n") || "no open threads"].join("\n")}\n`);
    return 0;
  }
  if (command.kind === "thread") {
    out(`${threadText((await call("thread", { ref: command.ref })) as ThreadShown)}\n`);
    return 0;
  }
  const text = command.file === null ? "" : readExact(command.file, "not UTF-8 text");
  const body = { by: command.by, text, where: command.where, when: command.when };
  const written = (await call(
    command.kind,
    command.kind === "ask"
      ? { ref: command.ref, raises: command.raises, ...body }
      : { thread: command.ref, ...body },
  )) as Written;
  if (written.outcome === AddOutcome.CHECK_FAILED) {
    out(`${[...checkLines(written.check), "not published: the check failed"].join("\n")}\n`);
    return 1;
  }
  out(
    `${written.outcome === AddOutcome.HELD ? heldLine(written.awaits, written.held) : `${written.outcome} ${written.ids.join(" ")}`}\n`,
  );
  return 0;
}
