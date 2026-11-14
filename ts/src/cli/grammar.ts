import { type Filters, filters, pyRepr, type Raises, type Scope } from "#core";
import { argumentsOf, type Exit, exit, usageError } from "./args.ts";
import { DECLARATIONS, TOP_HELP } from "./grammar-data.ts";

export type Command =
  | { readonly kind: "init" }
  | { readonly kind: "id"; readonly prefix: "d" | "s" }
  | {
      readonly kind: "search";
      readonly query: string;
      readonly filters: Filters;
      readonly limit: number;
    }
  | {
      readonly kind: "show";
      readonly ref: string;
      readonly reasoning: boolean;
      readonly provenance: boolean;
    }
  | { readonly kind: "draft"; readonly ref: string }
  | {
      readonly kind: "add";
      readonly files: readonly string[];
      readonly importing: boolean;
      readonly dryRun: boolean;
      readonly attachments: readonly string[];
    }
  | { readonly kind: "check"; readonly gate: boolean }
  | { readonly kind: "spec"; readonly area: string | null }
  | { readonly kind: "waiting" }
  | { readonly kind: "guide" }
  | { readonly kind: "threads" }
  | { readonly kind: "thread"; readonly ref: string }
  | {
      readonly kind: "ask";
      readonly ref: string;
      readonly raises: Raises;
      readonly by: string;
      readonly where: string | null;
      readonly when: string | null;
      readonly file: string;
    }
  | {
      readonly kind: "reply";
      readonly ref: string;
      readonly by: string;
      readonly where: string | null;
      readonly when: string | null;
      readonly file: string;
    }
  | {
      readonly kind: "close";
      readonly ref: string;
      readonly by: string;
      readonly where: string | null;
      readonly when: string | null;
      readonly file: string | null;
    };
export type ThreadCommand = Extract<
  Command,
  { readonly kind: "threads" | "thread" | "ask" | "reply" | "close" }
>;
export type { Exit } from "./args.ts";

export function parse(argv: readonly string[], version: string): Command | Exit {
  let index = 0;
  const extras: string[] = [];
  for (; index < argv.length; index++) {
    const word = argv[index] ?? "";
    if (word === "--") {
      index++;
      break;
    }
    if (!word.startsWith("-") || word === "-" || /^-\d+(?:\.\d+)?$/u.test(word)) break;
    const at = word.indexOf("=");
    const key = at < 0 ? word : word.slice(0, at);
    const help = key === "-h" || (key.startsWith("--") && "--help".startsWith(key));
    const versionFlag = key.startsWith("--") && "--version".startsWith(key);
    if (help || versionFlag) {
      if (at >= 0)
        return usageError(
          `argument ${help ? "-h/--help" : "--version"}: ignored explicit argument ${pyRepr(word.slice(at + 1))}`,
        );
      return exit(0, help ? TOP_HELP : `lodge ${version}\n`);
    }
    extras.push(word);
  }
  const name = argv[index];
  if (name === undefined) return usageError("the following arguments are required: COMMAND");
  const decl = DECLARATIONS[name];
  if (!decl)
    return usageError(
      `argument COMMAND: invalid choice: ${pyRepr(name)} (choose from ${Object.keys(DECLARATIONS).join(", ")})`,
    );
  const parsed = argumentsOf(argv.slice(index + 1), name, decl, extras);
  if (parsed.kind === "exit") return parsed;
  const a = parsed.values;
  const text = (key: string) => a[key] as string;
  const value = (key: string) => a[key];
  const nullable = (key: string) => (a[key] ?? null) as string | null;
  const ref = text("ref");
  switch (name) {
    case "init":
    case "waiting":
    case "guide":
    case "threads":
      return { kind: name };
    case "id":
      return { kind: name, prefix: text("prefix") as "d" | "s" };
    case "search":
      return {
        kind: name,
        query: text("query"),
        limit: value("limit") as number,
        filters: filters({
          kind: nullable("kind") as Filters["kind"],
          scope: nullable("scope") as Scope | null,
          status: text("status") as Filters["status"],
          area: nullable("area"),
          decidedBy: nullable("by"),
        }),
      };
    case "show":
      return {
        kind: name,
        ref,
        reasoning: !!value("reasoning"),
        provenance: !!value("provenance"),
      };
    case "draft":
    case "thread":
      return { kind: name, ref };
    case "add":
      return {
        kind: name,
        files: value("files") as string[],
        importing: !!value("importing"),
        dryRun: !!value("dry_run"),
        attachments: value("attach") as string[],
      };
    case "check":
      return { kind: name, gate: !!value("gate") };
    case "spec":
      return { kind: name, area: nullable("area") };
    case "ask":
    case "reply":
    case "close": {
      const by = text("by"),
        where = nullable("where"),
        when = nullable("when");
      if (by === "author" && (where === null || when === null))
        return exit(
          2,
          "",
          "lodge: a message by author needs --where and --when, the place and time of the author's words\n",
        );
      if (by !== "author" && (where !== null || when !== null))
        return exit(2, "", "lodge: --where and --when are for messages by author\n");
      if (name === "ask")
        return {
          kind: name,
          ref,
          by,
          where,
          when,
          file: text("file"),
          raises: text("kind") as Raises,
        };
      if (name === "reply") return { kind: name, ref, by, where, when, file: text("file") };
      return { kind: name, ref, by, where, when, file: nullable("file") };
    }
    default:
      return usageError(`unrecognized arguments: ${argv.join(" ")}`);
  }
}
