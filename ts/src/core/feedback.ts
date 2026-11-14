import { type Derived, isAuthor } from "./derive.ts";
import { areaPath } from "./fileformat.ts";
import { Action, type Decision, type Record, type SpecEntry } from "./model.ts";
import { related } from "./search.ts";
import type { LengthGuidance } from "./settings.ts";
import type { Snapshot } from "./snapshot.ts";
import {
  byCodePoint,
  codePointLength,
  PY_SPACE_CLASS,
  splitWords,
  strip,
  WORD_CLASS,
} from "./text.ts";

const START = `(?<!${WORD_CLASS})`;
const END = `(?!${WORD_CLASS})`;
const CODE_SPAN = /```.*?```|`[^`\n]*`/gsu;
const ID = new RegExp(`${START}[dsq]-[0-9a-hjkmnp-tv-z]{6}${END}`, "gu");
const ENTRY_ID = new RegExp(`${START}s-[0-9a-hjkmnp-tv-z]{6}${END}`, "gu");
const CODE = new RegExp(`${START}[A-Za-z][A-Za-z0-9]*-\\p{Nd}+${END}`, "gu");
const DATE = new RegExp(
  `${START}\\p{Nd}{4}-\\p{Nd}{2}-\\p{Nd}{2}(?:T[0-9:.]+(?:Z|[+-][0-9:]+)?)?`,
  "gu",
);
const NUMBER = new RegExp(`${START}\\p{Nd}+(?:[.,]\\p{Nd}+)*(?:${PY_SPACE_CLASS}?%)?`, "gu");

export interface Feedback {
  readonly recordId: string;
  readonly message: string;
}
export function feedback(
  added: readonly Record[],
  after: Snapshot,
  d: Derived,
  length: LengthGuidance,
): Feedback[] {
  return added.flatMap((record) =>
    [...messages(record, after, d, length)].map((message) => ({ recordId: record.id, message })),
  );
}
function* messages(
  record: Record,
  after: Snapshot,
  d: Derived,
  length: LengthGuidance,
): Generator<string> {
  const chars = codePointLength(record.title);
  if (chars > length.titleChars)
    yield `the title is ${chars} characters; guidance is ${length.titleChars} or fewer, on one line`;
  if (record.kind === "decision") yield* decisionMessages(record, after, d, length);
  else yield* entryMessages(record, after, length);
}
function* entryMessages(
  record: SpecEntry,
  after: Snapshot,
  length: LengthGuidance,
): Generator<string> {
  for (const target of new Set(record.statement.match(ENTRY_ID) ?? [])) {
    if (after.entries.has(target) && target !== record.id && !record.restsOn.includes(target))
      yield `the statement names ${target}, but rests_on does not list it; does ${record.id} rest on ${target}? If so, add it to rests_on`;
  }
  const words = splitWords(record.statement).length;
  if (words > length.specStatementWords)
    yield `the statement is ${words} words; guidance is ${length.specStatementWords} or fewer for a specification entry`;
}
function* decisionMessages(
  decision: Decision,
  after: Snapshot,
  d: Derived,
  length: LengthGuidance,
): Generator<string> {
  const words = splitWords(decision.statement).length;
  if (words > length.decisionStatementWords)
    yield `the statement is ${words} words; guidance is ${length.decisionStatementWords} or fewer for a decision`;
  const reasoning = splitWords(decision.reasoning).length;
  if (reasoning > length.reasoningWords)
    yield `the reasoning is ${reasoning} words; guidance is ${length.reasoningWords} or fewer`;
  if (!decision.replaces.length && !decision.narrows.length)
    yield* relatedMessage(decision, after, d);
  if (!decision.numbers.length) yield* numberMessage(decision, after);
  for (const target of decision.replaces) {
    const others = (d.replacedBy.get(target) ?? []).filter((i) => i !== decision.id);
    if (others.length) yield `${target} is already replaced by ${listed(others)}`;
  }
  yield* editBackMessage(decision, after, d);
  yield* revivalMessage(decision, after, d);
  if (d.awaitingAuthor.has(decision.id))
    yield "this decision will wait for the author: it takes effect at once, and a later author decision that confirms or replaces it clears the flag";
}
function* editBackMessage(decision: Decision, after: Snapshot, d: Derived): Generator<string> {
  if (!isAuthor(decision)) return;
  const own = new Set(decision.changes.map((c) => c.entry));
  for (const target of decision.replaces) {
    const replaced = after.decisions.get(target);
    if (!replaced || isAuthor(replaced)) continue;
    const edited = new Set(
      replaced.changes.filter((c) => c.action === Action.EDIT).map((c) => c.entry),
    );
    for (const entry of [...edited].sort(byCodePoint)) {
      if (!own.has(entry) && newestTextChange(entry, after, d) === replaced.id)
        yield `it replaces ${replaced.id}, whose edit of ${entry} is still the latest edit of that entry; does ${decision.id} edit ${entry} back? If so, add an edit draft of ${entry} and list it in changes with action edit`;
    }
  }
}
function newestTextChange(entry: string, after: Snapshot, d: Derived): string | null {
  for (const id of d.changedBy.get(entry) ?? []) {
    const decision = after.decisions.get(id) as Decision;
    if (
      decision.changes.some(
        (c) => c.entry === entry && (c.action === Action.CREATE || c.action === Action.EDIT),
      )
    )
      return id;
  }
  return null;
}
function* revivalMessage(decision: Decision, after: Snapshot, d: Derived): Generator<string> {
  const own = new Set(decision.changes.map((c) => c.entry));
  for (const entry of d.revived.get(decision.id) ?? []) {
    if (own.has(entry) || d.status.get(entry) !== "current") continue;
    const retirements = decision.replaces.filter(
      (t) =>
        after.decisions.has(t) &&
        d.replacedBy.get(t)?.at(-1) === decision.id &&
        after.decisions
          .get(t)
          ?.changes.some((c) => c.entry === entry && c.action === Action.RETIRE),
    );
    if (!retirements.length) continue;
    yield `it replaces ${listed(retirements)}, the last standing ${retirements.length > 1 ? "retirements" : "retirement"} of ${entry}, so ${entry} becomes current again; to keep it retired, list it in changes with action retire`;
  }
}
function listed(items: readonly string[]): string {
  if (items.length < 3) return items.join(" and ");
  return `${items.slice(0, -1).join(", ")}, and ${items.at(-1)}`;
}
function* relatedMessage(decision: Decision, after: Snapshot, d: Derived): Generator<string> {
  const found = related(after, d, decision);
  if (!found.length) return;
  const titles = found.map((i) => `${i} (${after.decisions.get(i)?.title})`).join(", ");
  const these = found.length > 1 ? "these current decisions look" : "this current decision looks";
  const target = found.length > 1 ? "any of them" : found[0];
  yield `it replaces and narrows nothing, but ${these} related: ${titles}; does ${decision.id} replace or narrow ${target}? If so, set replaces or narrows in the draft before adding it`;
}
function* numberMessage(decision: Decision, after: Snapshot): Generator<string> {
  const records = [...after.decisions.values(), ...after.entries.values()];
  const codes = new Set(records.flatMap((r) => (r.code ? [r.code.toLowerCase()] : [])));
  let text = `${decision.statement}\n${decision.reasoning}`;
  for (const hidden of [CODE_SPAN, DATE, ID]) text = text.replace(hidden, " ");
  text = text.replace(CODE, (code) => (codes.has(code.toLowerCase()) ? " " : code));
  const found = [...new Set((text.match(NUMBER) ?? []).map(strip))];
  if (found.length) {
    const noun = found.length > 1 ? "the numbers" : "the number";
    yield `the text holds ${noun} ${found.join(", ")} without a numbers handle; before adding the draft, give each one as \`numbers: [{value: "…", handle: "…"}]\`, the handle a record and key or a runnable command`;
  }
}
export function areaFeedback(
  after: Snapshot,
  writtenPaths: ReadonlySet<string> | readonly string[],
): Feedback[] {
  const paths = new Set(writtenPaths);
  const notes: Feedback[] = [];
  for (const [name, area] of [...after.areas].sort(([a], [b]) => byCodePoint(a, b))) {
    if (area.rank === null || !paths.has(areaPath(name))) continue;
    const others = [...after.areas]
      .filter(([n, a]) => n !== name && a.rank === area.rank)
      .map(([n]) => n)
      .sort(byCodePoint);
    if (others.length)
      notes.push({
        recordId: `area:${name}`,
        message: `rank ${area.rank} is shared with area ${listed(others)}; areas that share a rank are ordered by name`,
      });
  }
  return notes;
}
