import { type Actor, coreSettings } from "#app";
import { type Filters, filters, parseCoreSettings, SettingsError } from "#core";
import { Args, isObject } from "./args.ts";
import { ApiError } from "./errors.ts";
import type { ApiOptions } from "./options.ts";

const fields: Readonly<Record<string, readonly string[]>> = {
  search: ["query", "filters", "limit"],
  show: ["ref", "reasoning", "provenance"],
  waiting: [],
  timeline: ["limit"],
  spec: ["area"],
  problems: [],
  check: ["gate"],
  draft: ["ref"],
  mint: ["prefix"],
  add: ["drafts", "attachments", "importing", "dryRun"],
  ask: ["ref", "raises", "by", "text", "where", "when"],
  reply: ["thread", "by", "text", "where", "when"],
  close: ["thread", "by", "text", "where", "when"],
  threads: [],
  thread: ["ref"],
  "behind-area": ["name"],
  "project-create": ["settings"],
};
export function operationArgs(operation: string, body: Record<string, unknown>): Args {
  if (!Object.hasOwn(fields, operation))
    throw new ApiError("not-found", `no operation named ${operation}`);
  const args = new Args(operation, body);
  args.known(["project", ...(fields[operation] ?? [])]);
  return args;
}
function searchFilters(args: Args): Filters {
  const f = new Args(args.operation, args.object("filters", {}));
  for (const key of Object.keys(f.body))
    if (!["kind", "scope", "status", "area", "decidedBy"].includes(key))
      throw new ApiError("usage", `${args.operation}: unknown field filters.${key}`);
  const nullable = (name: string) => {
    const v = f.body[name];
    if (v !== undefined && v !== null && typeof v !== "string")
      args.fail(`filters.${name}`, "a string or null");
    return v === undefined ? null : (v as string | null);
  };
  const kind = nullable("kind"),
    scope = nullable("scope");
  if (kind !== null && kind !== "decision" && kind !== "spec")
    args.fail("filters.kind", "decision or spec or null");
  if (scope !== null && !["product", "process"].includes(scope))
    args.fail("filters.scope", "product or process or null");
  const status = f.body["status"] === undefined ? "current" : f.body["status"];
  if (!["current", "replaced", "retired", "any"].includes(status as string))
    args.fail("filters.status", "current or replaced or retired or any");
  return filters({
    kind,
    scope: scope as Filters["scope"],
    status: status as Filters["status"],
    area: nullable("area"),
    decidedBy: nullable("decidedBy"),
  });
}
async function createProject(options: ApiOptions, project: string, args: Args): Promise<unknown> {
  const setup = await options.accounts.setup();
  if (!setup) throw new ApiError("usage", "the server is not set up; run lodge server setup");
  const settings = args.object("settings");
  for (const [key, value] of Object.entries(settings))
    if (key !== "length" && key !== "import")
      throw new ApiError(
        "usage",
        isObject(value) ? `settings: unknown section [${key}]` : `settings: unknown key ${key}`,
      );
  try {
    parseCoreSettings(settings);
  } catch (error) {
    if (!(error instanceof SettingsError)) throw error;
    throw new ApiError("usage", `settings: ${error.message}`);
  }
  if ((await options.projects.names()).includes(project))
    throw new ApiError("usage", `lodge is already initialised: project ${project} exists`);
  await options.projects.create(project, setup.person, settings);
  return { project };
}
export async function operate(
  options: ApiOptions,
  args: Args,
  project: string,
  actor: Actor,
): Promise<unknown> {
  if (args.operation === "project-create") return createProject(options, project, args);
  const settings = await options.projects.settings(project);
  if (settings === null) throw new ApiError("no-project", `no project named ${project}`);
  const lodge = options.lodgeFor(project, coreSettings(settings), actor);
  const message = () => ({ where: args.nullable("where"), when: args.nullable("when") });
  switch (args.operation) {
    case "search":
      return lodge.search(args.string("query", ""), searchFilters(args), { limit: args.limit(20) });
    case "show":
      return lodge.show(args.string("ref"), {
        reasoning: args.boolean("reasoning"),
        provenance: args.boolean("provenance"),
      });
    case "waiting":
      return lodge.waitingAll();
    case "timeline":
      return lodge.timeline({ limit: args.limit(50) });
    case "spec":
      return lodge.spec({ area: args.nullable("area") });
    case "problems":
      return lodge.problems();
    case "check":
      return lodge.check(args.boolean("gate"));
    case "draft":
      return lodge.draft(args.string("ref"));
    case "mint":
      return lodge.mint(args.choice("prefix", ["d", "s"], "d"));
    case "add":
      return lodge.add(args.pairs("drafts"), {
        attachments: args.pairs("attachments", true),
        importing: args.boolean("importing"),
        dryRun: args.boolean("dryRun"),
      });
    case "ask":
      return lodge.ask(
        args.string("ref"),
        args.choice("raises", ["doubt", "question"]),
        args.string("by"),
        args.string("text"),
        message(),
      );
    case "reply":
      return lodge.reply(args.string("thread"), args.string("by"), args.string("text"), message());
    case "close":
      return lodge.close(args.string("thread"), args.string("by"), {
        text: args.nullable("text"),
        ...message(),
      });
    case "threads":
      return lodge.threads();
    case "thread":
      return lodge.thread(args.string("ref"));
    case "behind-area":
      return lodge.behindArea(args.string("name"));
    default:
      throw new ApiError("not-found", `no operation named ${args.operation}`);
  }
}
