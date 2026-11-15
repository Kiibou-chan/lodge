import { type Added, AddOutcome, type Listed, type Read, type Shown } from "#app";
import {
  type CheckResult,
  formatLevel1,
  formatLevel3,
  type Problem,
  rstrip,
  splitLines,
  strip,
  WORD_CLASS,
} from "#core";
export const NO_MATCHES = "no matches";
export const NOTHING_RECORDED = "Nothing is recorded yet.";
export const DECISION_DRAFT_NOTE =
  "note: decisions are immutable; to change one, write a new decision with replaces or narrows";
export function isDecisionFile(text: string): boolean {
  return splitLines(text.split("\n---\n", 1)[0] ?? "").some(
    (line) => strip(line) === "kind: decision",
  );
}
export function readLines(read: Read): string[] {
  return [
    ...(read.freshness === null ? [] : [read.freshness]),
    ...read.unrecorded.map((p) => `problem: ${where(p)}: ${p.message}`),
  ];
}
export function listedText(listed: Listed, empty: string): string {
  const lines = [
    ...readLines(listed.read),
    listed.items.length ? listed.items.map(formatLevel1).join("\n\n") : empty,
  ];
  if (listed.more) {
    const total = listed.items.length + listed.more;
    lines.push(
      `${listed.items.length} of ${total} shown; narrow the query or give --limit ${total}`,
    );
  }
  return lines.join("\n");
}
export function shownText(shown: Shown): string {
  const sections = [formatLevel1(shown.level1)];
  if (shown.level2 !== null) sections.push(section("Reasoning", shown.level2));
  if (shown.level3 !== null) sections.push(section("Provenance", formatLevel3(shown.level3)));
  return [...readLines(shown.read), sections.join("\n\n")].join("\n");
}
export function checkLines(result: CheckResult, alreadyShown: readonly Problem[] = []): string[] {
  const problems = result.problems.filter(
    (p) =>
      !alreadyShown.some(
        (q) =>
          p.kind === q.kind &&
          p.path === q.path &&
          p.line === q.line &&
          p.check === q.check &&
          p.message === q.message,
      ),
  );
  return [
    ...(result.ok ? ["ok"] : problems.map((p) => `check ${p.check}: ${p.message}`)),
    ...result.notes.map((note) => `note: ${note}`),
  ];
}
export function heldLine(awaits: string | null, held: number | null): string {
  return `held for approval by ${awaits} as hold ${held}; nothing is current until they approve it`;
}
export function addedLines(added: Added, dryRun: boolean): string[] {
  const provisional = new Set(dryRun || added.outcome === AddOutcome.HELD ? added.minted : []);
  const lines = added.feedback.map(
    (f) =>
      `feedback: ${f.recordId}${provisional.has(f.recordId) ? " (provisional)" : ""}: ${f.message}`,
  );
  lines.push(
    ...added.check.notes.map((note) => `note: ${note}`),
    ...added.check.problems.map((p) => `check ${p.check}: ${marked(p.message, provisional)}`),
  );
  if (added.outcome === AddOutcome.PUBLISHED || added.outcome === AddOutcome.STAGED)
    lines.push(rstrip(`${added.outcome} ${added.ids.join(" ")}`));
  else if (added.outcome === AddOutcome.UNCHANGED) lines.push(added.outcome);
  else if (added.outcome === AddOutcome.CHECK_FAILED) {
    if (added.freshness !== null) lines.push(added.freshness);
    lines.push("not published: the check failed");
  } else if (added.outcome === AddOutcome.HELD) lines.push(heldLine(added.awaits, added.held));
  if (dryRun) {
    if (added.awaits !== null)
      lines.push(`note: ${added.awaits} approves this add before it is current`);
    lines.push("dry run: nothing published");
  }
  return lines;
}
function marked(text: string, provisional: ReadonlySet<string>): string {
  for (const id of provisional) {
    const escaped = id.replace(/[.*+?^${}()|[\]\\]/gu, "\\$&");
    text = text.replace(
      new RegExp(`(?<!${WORD_CLASS})${escaped}(?!${WORD_CLASS})(?! \\(provisional\\))`, "gu"),
      () => `${id} (provisional)`,
    );
  }
  return text;
}
function section(heading: string, text: string): string {
  return `## ${heading}\n\n${text || "none recorded"}`;
}
function where(p: Problem): string {
  return p.line ? `${p.path}:${p.line}` : p.path;
}
