import { type Derived, isAuthor, orderKey } from "./derive.ts";
import { LookupError, ValueError } from "./errors.ts";
import { Action, type Decision, type Scope } from "./model.ts";
import type { Snapshot } from "./snapshot.ts";
import { byCodePoint } from "./text.ts";
import { LINE_BREAKS_AND_TABS, quoted } from "./yamlio.ts";

class IndexError extends LookupError {
  override name = "IndexError";
}

export const VIEWER = "lodge viewer";
export const MINUTE_FORMAT = "%Y-%m-%d %H:%M";

export function confirmableIds(s: Snapshot, d: Derived): ReadonlySet<string> {
  return new Set(
    [...s.decisions]
      .filter(
        ([id, decision]) =>
          !isAuthor(decision) && d.status.get(id) === "current" && !d.confirmedBy.has(id),
      )
      .map(([id]) => id),
  );
}
export function behindArea(s: Snapshot, d: Derived, area: string): readonly string[] {
  const entries = new Set([...s.entries].filter(([, e]) => e.area === area).map(([id]) => id));
  return [...confirmableIds(s, d)]
    .filter(
      (id) =>
        s.decisions
          .get(id)
          ?.changes.some((c) => entries.has(c.entry) && c.action === Action.CREATE) ||
        [...entries].some((e) => d.changedBy.get(e)?.[0] === id),
    )
    .sort((a, b) => {
      const [at, ai] = orderKey(s.decisions.get(a) as Decision);
      const [bt, bi] = orderKey(s.decisions.get(b) as Decision);
      return at - bt || byCodePoint(ai, bi);
    });
}
export function confirmationDraft(
  confirms: readonly string[],
  scope: Scope,
  words: string,
  when: string,
  area: string | null,
): string {
  if (area === null && confirms.length !== 1)
    throw new ValueError("a confirmation without an area needs one decision");
  const title =
    area === null ? `Confirms ${confirms[0]}` : `Confirms the decisions behind area ${area}`;
  if (confirms.length === 0) throw new IndexError("list index out of range");
  const listed =
    confirms.length === 1
      ? confirms[0]
      : confirms.length === 2
        ? confirms.join(" and ")
        : `${confirms.slice(0, -1).join(", ")}, and ${confirms[confirms.length - 1]}`;
  const ids = confirms.map((i) => quoted(i)).join(", ");
  const text = quoted(words, LINE_BREAKS_AND_TABS);
  return (
    `---\nkind: decision\ntitle: ${quoted(title)}\nscope: ${scope}\n` +
    `decided_by: author\nconfirms: [${ids}]\n` +
    `quote: {text: ${text}, where: ${quoted(VIEWER)}, when: ${quoted(when)}}\n---\n\n` +
    `The author confirms ${listed}.\n\n## Reasoning\n\n${words}\n`
  );
}
