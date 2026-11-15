import { type Actor, AddOutcome, coreSettings, type Held } from "#app";
import { parseDraft, recordFromDraft } from "#core";
import { Args } from "./args.ts";
import { ApiError } from "./errors.ts";
import type { ApiOptions } from "./options.ts";
import { issueToken } from "./tokens.ts";

const fields: Readonly<Record<string, readonly string[]>> = {
  "token-issue": ["project", "label", "role"],
  "token-revoke": ["id"],
  tokens: [],
  projects: [],
  confirm: ["project", "ids", "words", "area"],
  held: ["project"],
  approve: ["project", "seq"],
  decline: ["project", "seq", "reason"],
};
export function isPersonOperation(operation: string): boolean {
  return Object.hasOwn(fields, operation);
}
function heldDraft(name: string, text: string, at: string): unknown {
  const draft = parseDraft(name, text);
  if (draft.kind === "problem") return { name, problem: draft.message, text };
  const ownId = draft.header.get("id"),
    ownArea = draft.header.get("area");
  const id =
    typeof ownId === "string" ? ownId : draft.kind === "decision" ? "d-000000" : "s-000000";
  const area = draft.kind === "spec" ? (typeof ownArea === "string" ? ownArea : "held") : null;
  const record = recordFromDraft(draft, id, at, area);
  switch (record.kind) {
    case "problem":
      return { name, problem: record.message, text };
    case "decision":
      return {
        name,
        text,
        kind: record.kind,
        title: record.title,
        statement: record.statement,
        quote: record.quote,
      };
    case "spec":
      return { name, text, kind: record.kind, title: record.title, statement: record.statement };
    case "area":
      return { name, text, kind: record.kind, title: record.title, intro: record.intro };
  }
}
function presentHeld(h: Held): unknown {
  const common = { seq: h.seq, at: h.at, by: h.by, kind: h.kind };
  if (h.kind === "message")
    return {
      ...common,
      operation: h.operation,
      ref: h.ref,
      raises: h.raises,
      text: h.text,
      where: h.where,
      when: h.when,
    };
  return {
    ...common,
    drafts: h.drafts.map(([name, text]) => heldDraft(name, text, h.at)),
    attachments: h.attachments.map(([name, text]) => ({ name, text })),
  };
}
export interface PersonAnswer {
  readonly result: unknown;
  readonly checkFailed: boolean;
}
export async function personOperation(
  options: ApiOptions,
  operation: string,
  body: Record<string, unknown>,
  actor: Actor,
): Promise<PersonAnswer> {
  if (actor.kind !== "person")
    throw new ApiError("forbidden", `only the signed-in person may ${operation}`);
  const args = new Args(operation, body);
  args.known(fields[operation] ?? []);
  switch (operation) {
    case "token-issue":
      return {
        result: await issueToken(
          options,
          args.string("project"),
          args.string("label"),
          args.nullable("role"),
        ),
        checkFailed: false,
      };
    case "token-revoke":
      if (!(await options.accounts.revokeToken(args.string("id"))))
        throw new ApiError("not-found", "no live token with that id");
      return { result: null, checkFailed: false };
    case "tokens":
      return { result: await options.accounts.tokens(), checkFailed: false };
    case "projects":
      return { result: await options.projects.names(), checkFailed: false };
  }
  const project = args.string("project"),
    settings = await options.projects.settings(project);
  if (settings === null) throw new ApiError("no-project", `no project named ${project}`);
  const lodge = options.lodgeFor(project, coreSettings(settings), actor);
  if (operation === "confirm") {
    const ids = args.body["ids"];
    if (!Array.isArray(ids) || !ids.every((id) => typeof id === "string"))
      return args.fail("ids", "a list of strings");
    const result = await lodge.confirm(ids, args.string("words"), { area: args.nullable("area") });
    return { result, checkFailed: result.outcome === AddOutcome.CHECK_FAILED };
  }
  if (operation === "held")
    return {
      result: (await lodge.held())
        .filter((h) => h.person === actor.name)
        .sort((a, b) => a.seq - b.seq)
        .map(presentHeld),
      checkFailed: false,
    };
  const seq = args.body["seq"];
  if (typeof seq !== "number" || !Number.isSafeInteger(seq) || seq < 1)
    return args.fail("seq", "a positive whole number");
  if (operation === "approve") {
    const result = await lodge.approve(seq);
    const outcome = result.kind === "add" ? result.added : result.written;
    return { result, checkFailed: outcome.outcome === AddOutcome.CHECK_FAILED };
  }
  await lodge.decline(seq, args.string("reason"));
  return { result: null, checkFailed: false };
}
