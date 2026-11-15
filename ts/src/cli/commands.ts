import { basename, resolve } from "node:path";
import {
  type Added,
  AddOutcome,
  type Listed,
  type Read,
  type Shown,
  type ThreadsWaiting,
} from "#app";
import type { CheckResult } from "#core";
import { client } from "./client.ts";
import { CliError } from "./errors.ts";
import { readDraft, readExact } from "./files.ts";
import { parse } from "./grammar.ts";
import guide from "./guide.md" with { type: "text" };
import {
  addedLines,
  checkLines,
  DECISION_DRAFT_NOTE,
  isDecisionFile,
  listedText,
  NO_MATCHES,
  NOTHING_RECORDED,
  readLines,
  shownText,
} from "./output.ts";
import { readSettings, repositoryRoot, serverOf, tokenOf } from "./settings.ts";
import { waitingText } from "./thread-output.ts";
import { runThread } from "./threads.ts";
export interface Io {
  readonly cwd: string;
  readonly env: Readonly<Record<string, string | undefined>>;
  readonly fetch: (request: Request) => Promise<Response>;
  readonly out: (text: string) => void;
  readonly err: (text: string) => void;
  readonly version: string;
}
export async function run(argv: readonly string[], io: Io): Promise<number> {
  let localNames: readonly string[] = [];
  try {
    const command = parse(argv, io.version);
    if (command.kind === "exit") {
      io.out(command.out);
      io.err(command.err);
      return command.code;
    }
    if (command.kind === "guide") {
      io.out(guide);
      return 0;
    }
    localNames =
      command.kind === "add"
        ? [...command.files, ...command.attachments]
        : "file" in command && command.file !== null
          ? [command.file]
          : [];
    const drafts =
      command.kind === "add"
        ? command.files.map((name) => [name, readDraft(resolve(io.cwd, name))])
        : [];
    const attachments =
      command.kind === "add"
        ? command.attachments.map((path) => [
            basename(path),
            readExact(
              resolve(io.cwd, path),
              "not UTF-8 text; attachments are text in this version",
            ),
          ])
        : [];
    const settings = readSettings(repositoryRoot(io.cwd)),
      place = serverOf(settings),
      call = client(place, tokenOf(io.env), io);
    const print = (text: string) => io.out(`${text}\n`);
    switch (command.kind) {
      case "init":
        await call("project-create", { settings: settings.core });
        print(`created project ${place.project} on ${place.url}`);
        print("next: lodge guide");
        break;
      case "id":
        print((await call("mint", { prefix: command.prefix })) as string);
        break;
      case "search":
        print(
          listedText(
            (await call("search", {
              query: command.query,
              filters: command.filters,
              limit: command.limit,
            })) as Listed,
            NO_MATCHES,
          ),
        );
        break;
      case "show":
        print(
          shownText(
            (await call("show", {
              ref: command.ref,
              reasoning: command.reasoning,
              provenance: command.provenance,
            })) as Shown,
          ),
        );
        break;
      case "draft": {
        const text = (await call("draft", { ref: command.ref })) as string;
        if (isDecisionFile(text)) io.err(`${DECISION_DRAFT_NOTE}\n`);
        io.out(text);
        break;
      }
      case "add": {
        const added = (await call("add", {
          drafts,
          attachments,
          importing: command.importing,
          dryRun: command.dryRun,
        })) as Added;
        print(addedLines(added, command.dryRun).join("\n"));
        return added.outcome === AddOutcome.CHECK_FAILED ? 1 : 0;
      }
      case "check": {
        const [result, read] = (await call("check", { gate: command.gate })) as [CheckResult, Read];
        print([...readLines(read), ...checkLines(result, read.unrecorded)].join("\n"));
        return result.ok ? 0 : 1;
      }
      case "spec": {
        const [text, read] = (await call("spec", { area: command.area })) as [
          string,
          Read,
          unknown,
        ];
        print([...readLines(read), text.replace(/\n+$/u, "") || NOTHING_RECORDED].join("\n"));
        break;
      }
      case "waiting": {
        const [listed, waiting] = (await call("waiting", {})) as [Listed, ThreadsWaiting];
        print(waitingText(listed, waiting));
        break;
      }
      default: {
        const resolved =
          "file" in command && command.file !== null
            ? { ...command, file: resolve(io.cwd, command.file) }
            : command;
        return await runThread(resolved, call, io.out);
      }
    }
    return 0;
  } catch (error) {
    if (!(error instanceof CliError)) throw error;
    let message = error.message;
    for (const name of localNames) {
      const path = resolve(io.cwd, name);
      if (message.startsWith(`${path}:`)) {
        message = name + message.slice(path.length);
        break;
      }
    }
    io.err(`lodge: ${message}\n`);
    return error.exitCode;
  }
}
